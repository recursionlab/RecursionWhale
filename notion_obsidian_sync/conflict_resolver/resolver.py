"""
Conflict Resolution System
Handles conflicts between Notion and Obsidian versions intelligently
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import difflib
import hashlib

class ConflictResolver:
    """Intelligent conflict resolution for bidirectional sync"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get conflict resolution strategy from config
        self.strategy = config.get('conflict_resolution', {}).get('strategy', 'newest_wins')
        self.create_conflict_files = config.get('conflict_resolution', {}).get('create_conflict_files', True)
    
    async def resolve(self, notion_data: Dict) -> Dict:
        """Resolve conflicts for Notion page data"""
        try:
            if self.strategy == 'manual':
                return await self._handle_manual_resolution_notion(notion_data)
            elif self.strategy == 'notion_wins':
                return notion_data  # No conflict, Notion always wins
            elif self.strategy == 'obsidian_wins':
                return await self._get_obsidian_version(notion_data)
            elif self.strategy == 'newest_wins':
                return await self._resolve_by_timestamp_notion(notion_data)
            else:
                self.logger.warning(f"Unknown conflict strategy: {self.strategy}")
                return notion_data
                
        except Exception as e:
            self.logger.error(f"Failed to resolve Notion conflict: {e}")
            return notion_data
    
    async def resolve_file(self, file_path: Path, new_content: str) -> str:
        """Resolve conflicts for Obsidian file content"""
        try:
            if self.strategy == 'manual':
                return await self._handle_manual_resolution_file(file_path, new_content)
            elif self.strategy == 'notion_wins':
                return new_content  # Notion content wins
            elif self.strategy == 'obsidian_wins':
                # Keep existing file content
                if file_path.exists():
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        return await f.read()
                return new_content
            elif self.strategy == 'newest_wins':
                return await self._resolve_by_timestamp_file(file_path, new_content)
            else:
                self.logger.warning(f"Unknown conflict strategy: {self.strategy}")
                return new_content
                
        except Exception as e:
            self.logger.error(f"Failed to resolve file conflict: {e}")
            return new_content
    
    async def _resolve_by_timestamp_notion(self, notion_data: Dict) -> Dict:
        """Resolve conflict by comparing timestamps"""
        # This would require getting the corresponding Obsidian file
        # and comparing modification times
        # For now, return the Notion data
        return notion_data
    
    async def _resolve_by_timestamp_file(self, file_path: Path, new_content: str) -> str:
        """Resolve file conflict by comparing timestamps"""
        if not file_path.exists():
            return new_content
        
        # Get file modification time
        file_mtime = file_path.stat().st_mtime
        current_time = datetime.now().timestamp()
        
        # If file was modified very recently, prefer existing content
        if current_time - file_mtime < 60:  # Within last minute
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                existing_content = await f.read()
            
            # If content is different, create conflict file
            if existing_content != new_content and self.create_conflict_files:
                await self._create_conflict_file(file_path, existing_content, new_content)
            
            return existing_content
        
        return new_content
    
    async def _handle_manual_resolution_notion(self, notion_data: Dict) -> Dict:
        """Handle manual conflict resolution for Notion data"""
        # Create conflict markers and let user resolve manually
        if self.create_conflict_files:
            await self._create_notion_conflict_file(notion_data)
        
        # For now, return original data
        return notion_data
    
    async def _handle_manual_resolution_file(self, file_path: Path, new_content: str) -> str:
        """Handle manual conflict resolution for file content"""
        if not file_path.exists():
            return new_content
        
        # Read existing content
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            existing_content = await f.read()
        
        # If content is the same, no conflict
        if existing_content == new_content:
            return new_content
        
        # Create conflict file with both versions
        if self.create_conflict_files:
            await self._create_conflict_file(file_path, existing_content, new_content)
        
        # Return merged content with conflict markers
        return self._create_conflict_markers(existing_content, new_content)
    
    async def _create_conflict_file(self, original_path: Path, existing_content: str, new_content: str):
        """Create a conflict file showing both versions"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conflict_path = original_path.with_suffix(f'.conflict.{timestamp}.md')
        
        conflict_content = f"""# Conflict Resolution Required
        
**File:** {original_path.name}
**Timestamp:** {datetime.now().isoformat()}

## Existing Version (Obsidian)
```
{existing_content}
```

## New Version (Notion)
```
{new_content}
```

## Diff
```diff
{self._generate_diff(existing_content, new_content)}
```

## Instructions
1. Review both versions above
2. Edit the original file with your preferred content
3. Delete this conflict file when resolved
"""
        
        async with aiofiles.open(conflict_path, 'w', encoding='utf-8') as f:
            await f.write(conflict_content)
        
        self.logger.info(f"📝 Created conflict file: {conflict_path}")
    
    async def _create_notion_conflict_file(self, notion_data: Dict):
        """Create a conflict file for Notion data"""
        # This would create a file showing the conflicting Notion data
        # Implementation depends on specific requirements
        pass
    
    def _create_conflict_markers(self, existing_content: str, new_content: str) -> str:
        """Create Git-style conflict markers in content"""
        return f"""<<<<<<< Obsidian (existing)
{existing_content}
=======
{new_content}
>>>>>>> Notion (incoming)
"""
    
    def _generate_diff(self, content1: str, content2: str) -> str:
        """Generate a unified diff between two content strings"""
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile='Obsidian',
            tofile='Notion',
            lineterm=''
        )
        
        return ''.join(diff)
    
    async def _get_obsidian_version(self, notion_data: Dict) -> Dict:
        """Get the Obsidian version of the data (placeholder)"""
        # This would require looking up the corresponding Obsidian file
        # and converting it back to Notion format
        return notion_data
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content for comparison"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def detect_conflicts(self, notion_data: Dict, file_path: Path) -> bool:
        """Detect if there are conflicts between Notion and Obsidian versions"""
        if not file_path.exists():
            return False
        
        try:
            # Read Obsidian file
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                obsidian_content = await f.read()
            
            # This would require converting Notion data to markdown
            # and comparing with Obsidian content
            # For now, assume no conflicts
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to detect conflicts: {e}")
            return False
    
    def get_conflict_stats(self) -> Dict:
        """Get statistics about conflicts"""
        # This would track conflict resolution statistics
        return {
            'total_conflicts': 0,
            'resolved_conflicts': 0,
            'pending_conflicts': 0,
            'strategy': self.strategy
        }

