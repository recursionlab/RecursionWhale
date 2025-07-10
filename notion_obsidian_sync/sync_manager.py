#!/usr/bin/env python3
"""
Notion ↔ Obsidian Bidirectional Sync Manager
Invisible intelligence for seamless knowledge management
"""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from notion_client.client import NotionSyncClient
from obsidian_client.client import ObsidianSyncClient
from converters.notion_to_obsidian import NotionToObsidianConverter
from converters.obsidian_to_notion import ObsidianToNotionConverter
from conflict_resolver.resolver import ConflictResolver
from watchers.file_watcher import FileWatcher
from watchers.notion_watcher import NotionWatcher

class SyncManager:
    """Main orchestrator for bidirectional sync between Notion and Obsidian"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Initialize clients
        self.notion_client = NotionSyncClient(
            token=self.config['notion']['token'],
            database_ids=self.config['notion']['database_ids']
        )
        
        self.obsidian_client = ObsidianSyncClient(
            vault_path=self.config['obsidian']['vault_path'],
            sync_folder=self.config['obsidian']['sync_folder']
        )
        
        # Initialize converters
        self.notion_to_obsidian = NotionToObsidianConverter(self.config)
        self.obsidian_to_notion = ObsidianToNotionConverter(self.config)
        
        # Initialize conflict resolver
        self.conflict_resolver = ConflictResolver(self.config)
        
        # Initialize watchers
        self.file_watcher = FileWatcher(
            self.obsidian_client.sync_path,
            self._on_obsidian_change
        )
        self.notion_watcher = NotionWatcher(
            self.notion_client,
            self._on_notion_change
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def initial_sync(self):
        """Perform initial bidirectional sync"""
        self.logger.info("🚀 Starting initial bidirectional sync...")
        
        # Sync Notion → Obsidian
        await self._sync_notion_to_obsidian()
        
        # Sync Obsidian → Notion  
        await self._sync_obsidian_to_notion()
        
        self.logger.info("✅ Initial sync completed!")
    
    async def _sync_notion_to_obsidian(self):
        """Sync all Notion pages to Obsidian"""
        self.logger.info("📥 Syncing Notion → Obsidian...")
        
        # Get all pages from configured databases
        pages = await self.notion_client.get_all_pages()
        
        for page in pages:
            try:
                # Convert Notion page to Obsidian markdown
                markdown_content = await self.notion_to_obsidian.convert(page)
                
                # Write to Obsidian vault
                file_path = self.obsidian_client.get_file_path(page['title'])
                await self.obsidian_client.write_file(file_path, markdown_content)
                
                self.logger.debug(f"✅ Synced: {page['title']}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to sync {page['title']}: {e}")
    
    async def _sync_obsidian_to_notion(self):
        """Sync all Obsidian files to Notion"""
        self.logger.info("📤 Syncing Obsidian → Notion...")
        
        # Get all markdown files in sync folder
        files = self.obsidian_client.get_all_files()
        
        for file_path in files:
            try:
                # Read markdown content
                content = await self.obsidian_client.read_file(file_path)
                
                # Convert to Notion format
                notion_data = await self.obsidian_to_notion.convert(content, file_path)
                
                # Create or update in Notion
                await self.notion_client.create_or_update_page(notion_data)
                
                self.logger.debug(f"✅ Synced: {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to sync {file_path.name}: {e}")
    
    async def _on_obsidian_change(self, file_path: Path, event_type: str):
        """Handle Obsidian file changes"""
        self.logger.info(f"📝 Obsidian change detected: {file_path.name} ({event_type})")
        
        try:
            if event_type in ['created', 'modified']:
                # Read and convert file
                content = await self.obsidian_client.read_file(file_path)
                notion_data = await self.obsidian_to_notion.convert(content, file_path)
                
                # Check for conflicts
                if await self._has_conflict(notion_data):
                    resolved_data = await self.conflict_resolver.resolve(notion_data)
                    notion_data = resolved_data
                
                # Update Notion
                await self.notion_client.create_or_update_page(notion_data)
                
            elif event_type == 'deleted':
                # Archive corresponding Notion page
                await self.notion_client.archive_page_by_title(file_path.stem)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to handle Obsidian change: {e}")
    
    async def _on_notion_change(self, page_data: Dict, event_type: str):
        """Handle Notion page changes"""
        self.logger.info(f"📝 Notion change detected: {page_data['title']} ({event_type})")
        
        try:
            if event_type in ['created', 'modified']:
                # Convert to Obsidian format
                markdown_content = await self.notion_to_obsidian.convert(page_data)
                
                # Check for conflicts
                file_path = self.obsidian_client.get_file_path(page_data['title'])
                if await self._has_file_conflict(file_path, markdown_content):
                    resolved_content = await self.conflict_resolver.resolve_file(
                        file_path, markdown_content
                    )
                    markdown_content = resolved_content
                
                # Write to Obsidian
                await self.obsidian_client.write_file(file_path, markdown_content)
                
            elif event_type == 'deleted':
                # Delete corresponding Obsidian file
                file_path = self.obsidian_client.get_file_path(page_data['title'])
                await self.obsidian_client.delete_file(file_path)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to handle Notion change: {e}")
    
    async def _has_conflict(self, notion_data: Dict) -> bool:
        """Check if there's a conflict with existing Notion page"""
        existing_page = await self.notion_client.get_page_by_title(notion_data['title'])
        if not existing_page:
            return False
        
        # Compare last modified times
        return existing_page['last_edited_time'] > notion_data.get('last_modified', '')
    
    async def _has_file_conflict(self, file_path: Path, new_content: str) -> bool:
        """Check if there's a conflict with existing Obsidian file"""
        if not file_path.exists():
            return False
        
        existing_content = await self.obsidian_client.read_file(file_path)
        existing_modified = file_path.stat().st_mtime
        
        # Simple conflict detection - can be enhanced
        return existing_content != new_content
    
    async def start_watching(self):
        """Start continuous sync with file watching"""
        self.logger.info("👀 Starting continuous sync...")
        
        # Start watchers
        await asyncio.gather(
            self.file_watcher.start(),
            self.notion_watcher.start()
        )
    
    async def stop_watching(self):
        """Stop continuous sync"""
        self.logger.info("🛑 Stopping continuous sync...")
        
        await asyncio.gather(
            self.file_watcher.stop(),
            self.notion_watcher.stop()
        )

async def main():
    parser = argparse.ArgumentParser(description="Notion ↔ Obsidian Sync")
    parser.add_argument('--initial-sync', action='store_true', 
                       help='Perform initial bidirectional sync')
    parser.add_argument('--watch', action='store_true',
                       help='Start continuous sync with file watching')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    sync_manager = SyncManager(args.config)
    
    try:
        if args.initial_sync:
            await sync_manager.initial_sync()
        
        if args.watch:
            await sync_manager.start_watching()
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await sync_manager.stop_watching()
    
    except Exception as e:
        logging.error(f"❌ Sync failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

