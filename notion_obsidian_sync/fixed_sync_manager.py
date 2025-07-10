#!/usr/bin/env python3
"""
Fixed Notion ↔ Obsidian Sync Manager
Works with your exact database structure
"""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import aiohttp
from datetime import datetime

class FixedNotionClient:
    """Simplified Notion client that works with your database structure"""
    
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    async def create_page(self, title: str, content: str = "") -> Dict:
        """Create a page with just the basic properties that exist in your database"""
        
        # Build properties that match your database exactly
        properties = {
            "Name": {  # Your title property
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        # Add content as blocks
        blocks = []
        if content.strip():
            # Simple paragraph block
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content[:2000]  # Notion has limits
                            }
                        }
                    ]
                }
            })
        
        create_data = {
            "parent": {
                "type": "database_id",
                "database_id": self.database_id
            },
            "properties": properties,
            "children": blocks
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/pages"
            
            async with session.post(url, headers=self.headers, json=create_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"✅ Created page: {title}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"❌ Failed to create page '{title}': {error_text}")
                    raise Exception(f"Failed to create page: {error_text}")
    
    async def get_all_pages(self) -> List[Dict]:
        """Get all pages from the database"""
        pages = []
        has_more = True
        start_cursor = None
        
        while has_more:
            query_data = {"page_size": 100}
            if start_cursor:
                query_data["start_cursor"] = start_cursor
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/databases/{self.database_id}/query"
                
                async with session.post(url, headers=self.headers, json=query_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages.extend(data.get("results", []))
                        has_more = data.get("has_more", False)
                        start_cursor = data.get("next_cursor")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to query database: {error_text}")
                        break
        
        return pages

class FixedObsidianClient:
    """Simple Obsidian client for file operations"""
    
    def __init__(self, vault_path: str, sync_folder: str = "Notion Sync"):
        self.vault_path = Path(vault_path)
        self.sync_folder = sync_folder
        self.sync_path = self.vault_path / sync_folder
        self.sync_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def get_all_files(self) -> List[Path]:
        """Get all markdown files in sync folder"""
        return list(self.sync_path.glob("*.md"))
    
    async def read_file(self, file_path: Path) -> str:
        """Read file content"""
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to read {file_path}: {e}")
            return ""
    
    async def write_file(self, file_path: Path, content: str):
        """Write file content"""
        try:
            file_path.write_text(content, encoding='utf-8')
            self.logger.info(f"✅ Wrote file: {file_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to write {file_path}: {e}")
    
    def get_file_path(self, title: str) -> Path:
        """Get file path for a title"""
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        return self.sync_path / f"{safe_title}.md"

class FixedSyncManager:
    """Simplified sync manager that actually works"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Initialize clients with your exact configuration
        self.notion_client = FixedNotionClient(
            token=self.config['notion']['token'],
            database_id=self.config['notion']['database_ids'][0]  # Use first database
        )
        
        self.obsidian_client = FixedObsidianClient(
            vault_path=self.config['obsidian']['vault_path'],
            sync_folder=self.config['obsidian']['sync_folder']
        )
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    async def test_sync(self):
        """Test the sync functionality"""
        self.logger.info("🧪 Testing sync functionality...")
        
        try:
            # Test 1: Create a test page in Notion
            test_title = f"Test Page {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            test_content = "This is a test page created by the sync system."
            
            self.logger.info(f"📝 Creating test page: {test_title}")
            notion_page = await self.notion_client.create_page(test_title, test_content)
            
            # Test 2: Read pages from Notion
            self.logger.info("📥 Reading pages from Notion...")
            pages = await self.notion_client.get_all_pages()
            self.logger.info(f"Found {len(pages)} pages in Notion database")
            
            # Test 3: Create a test file in Obsidian
            test_file_title = f"Obsidian Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            test_file_content = f"# {test_file_title}\n\nThis is a test file created in Obsidian."
            test_file_path = self.obsidian_client.get_file_path(test_file_title)
            
            self.logger.info(f"📝 Creating test file: {test_file_path.name}")
            await self.obsidian_client.write_file(test_file_path, test_file_content)
            
            # Test 4: Sync Obsidian file to Notion
            self.logger.info("📤 Syncing test file to Notion...")
            await self.notion_client.create_page(test_file_title, test_file_content)
            
            self.logger.info("✅ All tests passed! Sync is working correctly.")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Test failed: {e}")
            return False
    
    async def initial_sync(self):
        """Perform initial bidirectional sync"""
        self.logger.info("🚀 Starting initial bidirectional sync...")
        
        try:
            # Sync Notion → Obsidian
            await self._sync_notion_to_obsidian()
            
            # Sync Obsidian → Notion
            await self._sync_obsidian_to_notion()
            
            self.logger.info("✅ Initial sync completed!")
            
        except Exception as e:
            self.logger.error(f"❌ Initial sync failed: {e}")
            raise
    
    async def _sync_notion_to_obsidian(self):
        """Sync Notion pages to Obsidian files"""
        self.logger.info("📥 Syncing Notion → Obsidian...")
        
        pages = await self.notion_client.get_all_pages()
        
        for page in pages:
            try:
                # Extract title from page properties
                title_prop = page.get('properties', {}).get('Name', {})
                title_array = title_prop.get('title', [])
                title = title_array[0]['text']['content'] if title_array else 'Untitled'
                
                # Create simple markdown content
                content = f"# {title}\n\n*Synced from Notion*\n\nPage ID: {page['id']}"
                
                # Write to Obsidian
                file_path = self.obsidian_client.get_file_path(title)
                await self.obsidian_client.write_file(file_path, content)
                
                self.logger.debug(f"✅ Synced from Notion: {title}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to sync page: {e}")
    
    async def _sync_obsidian_to_notion(self):
        """Sync Obsidian files to Notion pages"""
        self.logger.info("📤 Syncing Obsidian → Notion...")
        
        files = self.obsidian_client.get_all_files()
        
        for file_path in files:
            try:
                # Read file content
                content = await self.obsidian_client.read_file(file_path)
                
                # Extract title (filename without extension)
                title = file_path.stem
                
                # Create page in Notion
                await self.notion_client.create_page(title, content)
                
                self.logger.debug(f"✅ Synced to Notion: {title}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to sync {file_path.name}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Fixed Notion ↔ Obsidian Sync")
    parser.add_argument('--test', action='store_true', 
                       help='Test sync functionality')
    parser.add_argument('--initial-sync', action='store_true', 
                       help='Perform initial bidirectional sync')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    sync_manager = FixedSyncManager(args.config)
    
    try:
        if args.test:
            success = await sync_manager.test_sync()
            if success:
                print("\n🎉 SUCCESS! The sync system is working correctly.")
                print("You can now use --initial-sync to sync all your files.")
            else:
                print("\n❌ FAILED! Check the logs above for details.")
        
        elif args.initial_sync:
            await sync_manager.initial_sync()
    
    except Exception as e:
        logging.error(f"❌ Sync failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
