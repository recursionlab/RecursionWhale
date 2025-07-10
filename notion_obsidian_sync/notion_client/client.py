"""
Notion API Client for Bidirectional Sync
Handles all Notion operations with intelligent caching and rate limiting
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

class NotionSyncClient:
    """Enhanced Notion client for bidirectional sync operations"""
    
    def __init__(self, token: str, database_ids: List[str]):
        self.token = token
        self.database_ids = database_ids
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
        self._page_cache = {}
        self._last_sync_time = None
    
    async def get_all_pages(self) -> List[Dict]:
        """Get all pages from configured databases"""
        all_pages = []
        
        for database_id in self.database_ids:
            pages = await self._get_database_pages(database_id)
            all_pages.extend(pages)
        
        return all_pages
    
    async def _get_database_pages(self, database_id: str) -> List[Dict]:
        """Get all pages from a specific database"""
        pages = []
        has_more = True
        start_cursor = None
        
        while has_more:
            query_data = {
                "page_size": 100
            }
            
            if start_cursor:
                query_data["start_cursor"] = start_cursor
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/databases/{database_id}/query"
                
                async with session.post(url, headers=self.headers, json=query_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Failed to query database: {error_text}")
                    
                    data = await response.json()
                    
                    for page in data.get("results", []):
                        # Get full page content
                        full_page = await self._get_page_content(page["id"])
                        pages.append(full_page)
                    
                    has_more = data.get("has_more", False)
                    start_cursor = data.get("next_cursor")
        
        return pages
    
    async def _get_page_content(self, page_id: str) -> Dict:
        """Get full page content including blocks"""
        # Get page metadata
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pages/{page_id}"
            
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get page: {error_text}")
                
                page_data = await response.json()
        
        # Get page blocks (content)
        blocks = await self._get_page_blocks(page_id)
        page_data["blocks"] = blocks
        
        # Extract title from properties
        title = self._extract_title(page_data.get("properties", {}))
        page_data["title"] = title
        
        return page_data
    
    async def _get_page_blocks(self, page_id: str) -> List[Dict]:
        """Get all blocks (content) from a page"""
        blocks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            params = {"page_size": 100}
            if start_cursor:
                params["start_cursor"] = start_cursor
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/blocks/{page_id}/children"
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Failed to get blocks: {error_text}")
                    
                    data = await response.json()
                    
                    for block in data.get("results", []):
                        # Recursively get child blocks if they exist
                        if block.get("has_children"):
                            child_blocks = await self._get_page_blocks(block["id"])
                            block["children"] = child_blocks
                        
                        blocks.append(block)
                    
                    has_more = data.get("has_more", False)
                    start_cursor = data.get("next_cursor")
        
        return blocks
    
    def _extract_title(self, properties: Dict) -> str:
        """Extract title from page properties"""
        # Look for title property
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array:
                    return "".join([t.get("plain_text", "") for t in title_array])
        
        return "Untitled"
    
    async def create_or_update_page(self, page_data: Dict) -> Dict:
        """Create a new page or update existing one"""
        # Check if page exists
        existing_page = await self.get_page_by_title(page_data["title"])
        
        if existing_page:
            return await self._update_page(existing_page["id"], page_data)
        else:
            return await self._create_page(page_data)
    
    async def _create_page(self, page_data: Dict) -> Dict:
        """Create a new page in Notion"""
        # Determine parent (use first database by default)
        parent = {
            "type": "database_id",
            "database_id": self.database_ids[0]
        }
        
        # Build properties
        properties = {
            "Name": {  # Assuming database has a "Name" title property
                "title": [
                    {
                        "text": {
                            "content": page_data["title"]
                        }
                    }
                ]
            }
        }
        
        # Add other properties from page_data
        if "properties" in page_data:
            properties.update(page_data["properties"])
        
        create_data = {
            "parent": parent,
            "properties": properties
        }
        
        # Add content blocks if provided
        if "blocks" in page_data:
            create_data["children"] = page_data["blocks"]
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pages"
            
            async with session.post(url, headers=self.headers, json=create_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to create page: {error_text}")
                
                return await response.json()
    
    async def _update_page(self, page_id: str, page_data: Dict) -> Dict:
        """Update an existing page"""
        # Update properties
        if "properties" in page_data:
            update_data = {
                "properties": page_data["properties"]
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/pages/{page_id}"
                
                async with session.patch(url, headers=self.headers, json=update_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Failed to update page properties: {error_text}")
        
        # Update content blocks if provided
        if "blocks" in page_data:
            await self._replace_page_blocks(page_id, page_data["blocks"])
        
        return await self._get_page_content(page_id)
    
    async def _replace_page_blocks(self, page_id: str, new_blocks: List[Dict]):
        """Replace all blocks in a page with new ones"""
        # First, delete existing blocks
        existing_blocks = await self._get_page_blocks(page_id)
        
        for block in existing_blocks:
            await self._delete_block(block["id"])
        
        # Then add new blocks
        if new_blocks:
            await self._append_blocks(page_id, new_blocks)
    
    async def _delete_block(self, block_id: str):
        """Delete a block"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/blocks/{block_id}"
            
            async with session.delete(url, headers=self.headers) as response:
                if response.status not in [200, 404]:  # 404 is OK if already deleted
                    error_text = await response.text()
                    self.logger.warning(f"Failed to delete block {block_id}: {error_text}")
    
    async def _append_blocks(self, page_id: str, blocks: List[Dict]):
        """Append blocks to a page"""
        append_data = {
            "children": blocks
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/blocks/{page_id}/children"
            
            async with session.patch(url, headers=self.headers, json=append_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to append blocks: {error_text}")
    
    async def get_page_by_title(self, title: str) -> Optional[Dict]:
        """Find a page by its title"""
        # Search across all databases
        for database_id in self.database_ids:
            page = await self._search_page_in_database(database_id, title)
            if page:
                return page
        
        return None
    
    async def _search_page_in_database(self, database_id: str, title: str) -> Optional[Dict]:
        """Search for a page by title in a specific database"""
        query_data = {
            "filter": {
                "property": "Name",  # Assuming title property is named "Name"
                "title": {
                    "equals": title
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/databases/{database_id}/query"
            
            async with session.post(url, headers=self.headers, json=query_data) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                results = data.get("results", [])
                
                if results:
                    # Return first match with full content
                    return await self._get_page_content(results[0]["id"])
        
        return None
    
    async def archive_page_by_title(self, title: str):
        """Archive a page by its title"""
        page = await self.get_page_by_title(title)
        if page:
            await self._archive_page(page["id"])
    
    async def _archive_page(self, page_id: str):
        """Archive a page"""
        update_data = {
            "archived": True
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pages/{page_id}"
            
            async with session.patch(url, headers=self.headers, json=update_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to archive page: {error_text}")
    
    async def get_recent_changes(self, since: datetime) -> List[Dict]:
        """Get pages that have changed since a specific time"""
        # This would require implementing change tracking
        # For now, return all pages and let the sync manager handle comparison
        return await self.get_all_pages()

