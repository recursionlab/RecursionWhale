"""
Notion Change Watcher
Monitors Notion for page changes and triggers sync
"""

import asyncio
from typing import Callable, Dict, List, Optional, Set
import logging
from datetime import datetime, timezone

class NotionWatcher:
    """Watch Notion for page changes"""
    
    def __init__(self, notion_client, callback: Callable):
        self.notion_client = notion_client
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
        self._running = False
        self._poll_interval = 30  # seconds
        self._last_check = None
        self._known_pages: Dict[str, datetime] = {}
    
    async def start(self):
        """Start watching for Notion changes"""
        self.logger.info("👀 Starting Notion watcher...")
        
        # Initialize known pages
        await self._initialize_known_pages()
        
        self._running = True
        self._last_check = datetime.now(timezone.utc)
        
        # Start polling loop
        asyncio.create_task(self._poll_loop())
        
        self.logger.info("✅ Notion watcher started")
    
    async def stop(self):
        """Stop watching for Notion changes"""
        self.logger.info("🛑 Stopping Notion watcher...")
        self._running = False
        self.logger.info("✅ Notion watcher stopped")
    
    async def _initialize_known_pages(self):
        """Initialize the set of known pages"""
        try:
            pages = await self.notion_client.get_all_pages()
            
            for page in pages:
                page_id = page.get('id')
                last_edited = page.get('last_edited_time')
                
                if page_id and last_edited:
                    # Parse ISO timestamp
                    last_edited_dt = datetime.fromisoformat(
                        last_edited.replace('Z', '+00:00')
                    )
                    self._known_pages[page_id] = last_edited_dt
            
            self.logger.info(f"📊 Initialized with {len(self._known_pages)} known pages")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize known pages: {e}")
    
    async def _poll_loop(self):
        """Main polling loop"""
        while self._running:
            try:
                await self._check_for_changes()
                await asyncio.sleep(self._poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in Notion polling loop: {e}")
                await asyncio.sleep(self._poll_interval)
    
    async def _check_for_changes(self):
        """Check for changes in Notion pages"""
        try:
            # Get current pages
            current_pages = await self.notion_client.get_all_pages()
            current_page_ids = set()
            
            for page in current_pages:
                page_id = page.get('id')
                last_edited = page.get('last_edited_time')
                title = page.get('title', 'Untitled')
                
                if not page_id or not last_edited:
                    continue
                
                current_page_ids.add(page_id)
                
                # Parse timestamp
                last_edited_dt = datetime.fromisoformat(
                    last_edited.replace('Z', '+00:00')
                )
                
                # Check if page is new or modified
                if page_id not in self._known_pages:
                    # New page
                    self.logger.info(f"📄 New page detected: {title}")
                    await self._handle_page_change(page, 'created')
                    self._known_pages[page_id] = last_edited_dt
                    
                elif last_edited_dt > self._known_pages[page_id]:
                    # Modified page
                    self.logger.info(f"✏️ Modified page detected: {title}")
                    await self._handle_page_change(page, 'modified')
                    self._known_pages[page_id] = last_edited_dt
            
            # Check for deleted pages
            deleted_page_ids = set(self._known_pages.keys()) - current_page_ids
            
            for deleted_id in deleted_page_ids:
                self.logger.info(f"🗑️ Deleted page detected: {deleted_id}")
                
                # Create minimal page data for deletion
                deleted_page_data = {
                    'id': deleted_id,
                    'title': f"Deleted Page {deleted_id[:8]}",
                    'deleted': True
                }
                
                await self._handle_page_change(deleted_page_data, 'deleted')
                del self._known_pages[deleted_id]
            
            self._last_check = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Failed to check for Notion changes: {e}")
    
    async def _handle_page_change(self, page_data: Dict, event_type: str):
        """Handle a detected page change"""
        try:
            await self.callback(page_data, event_type)
        except Exception as e:
            self.logger.error(f"Failed to handle page change: {e}")
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self._running
    
    def get_status(self) -> Dict:
        """Get watcher status"""
        return {
            'running': self._running,
            'last_check': self._last_check,
            'known_pages_count': len(self._known_pages),
            'poll_interval': self._poll_interval
        }

