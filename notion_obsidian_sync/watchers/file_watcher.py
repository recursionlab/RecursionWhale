"""
File System Watcher for Obsidian Changes
Monitors Obsidian vault for file changes and triggers sync
"""

import asyncio
from pathlib import Path
from typing import Callable, Optional
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

class ObsidianFileHandler(FileSystemEventHandler):
    """Handle file system events for Obsidian files"""
    
    def __init__(self, callback: Callable, sync_path: Path):
        self.callback = callback
        self.sync_path = sync_path
        self.logger = logging.getLogger(__name__)
        
        # Debounce rapid file changes
        self._pending_events = {}
        self._debounce_delay = 1.0  # seconds
    
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._schedule_callback(event.src_path, 'modified')
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._schedule_callback(event.src_path, 'created')
    
    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.md'):
            self._schedule_callback(event.src_path, 'deleted')
    
    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory and event.src_path.endswith('.md'):
            # Handle as delete + create
            self._schedule_callback(event.src_path, 'deleted')
            if hasattr(event, 'dest_path'):
                self._schedule_callback(event.dest_path, 'created')
    
    def _schedule_callback(self, file_path: str, event_type: str):
        """Schedule callback with debouncing"""
        path_obj = Path(file_path)
        
        # Only process files in sync folder
        if not self._is_in_sync_folder(path_obj):
            return
        
        # Cancel previous event for this file
        if file_path in self._pending_events:
            self._pending_events[file_path].cancel()
        
        # Schedule new event
        loop = asyncio.get_event_loop()
        self._pending_events[file_path] = loop.call_later(
            self._debounce_delay,
            self._execute_callback,
            path_obj,
            event_type
        )
    
    def _is_in_sync_folder(self, file_path: Path) -> bool:
        """Check if file is in the sync folder"""
        try:
            file_path.relative_to(self.sync_path)
            return True
        except ValueError:
            return False
    
    def _execute_callback(self, file_path: Path, event_type: str):
        """Execute the callback in an async context"""
        # Remove from pending events
        if str(file_path) in self._pending_events:
            del self._pending_events[str(file_path)]
        
        # Create async task for callback
        loop = asyncio.get_event_loop()
        loop.create_task(self.callback(file_path, event_type))

class FileWatcher:
    """Watch Obsidian vault for file changes"""
    
    def __init__(self, sync_path: Path, callback: Callable):
        self.sync_path = sync_path
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        
        self.observer: Optional[Observer] = None
        self.handler: Optional[ObsidianFileHandler] = None
    
    async def start(self):
        """Start watching for file changes"""
        self.logger.info(f"👀 Starting file watcher for {self.sync_path}")
        
        # Create handler
        self.handler = ObsidianFileHandler(self.callback, self.sync_path)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(
            self.handler,
            str(self.sync_path),
            recursive=True
        )
        
        # Start observer
        self.observer.start()
        
        self.logger.info("✅ File watcher started")
    
    async def stop(self):
        """Stop watching for file changes"""
        if self.observer:
            self.logger.info("🛑 Stopping file watcher...")
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.logger.info("✅ File watcher stopped")
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self.observer is not None and self.observer.is_alive()

