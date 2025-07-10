"""
Obsidian Vault Client for Bidirectional Sync
Handles all Obsidian file operations with intelligent link management
"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Optional, Set
import re
import logging
from datetime import datetime

class ObsidianSyncClient:
    """Enhanced Obsidian client for bidirectional sync operations"""
    
    def __init__(self, vault_path: str, sync_folder: str = "Notion Sync"):
        self.vault_path = Path(vault_path)
        self.sync_folder = sync_folder
        self.sync_path = self.vault_path / sync_folder
        self.logger = logging.getLogger(__name__)
        
        # Ensure sync folder exists
        self.sync_path.mkdir(parents=True, exist_ok=True)
        
        # Patterns for link detection
        self.wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        self.markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def get_all_files(self) -> List[Path]:
        """Get all markdown files in the sync folder"""
        return list(self.sync_path.glob("**/*.md"))
    
    async def read_file(self, file_path: Path) -> str:
        """Read content from a markdown file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    async def write_file(self, file_path: Path, content: str):
        """Write content to a markdown file"""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
                
            self.logger.debug(f"✅ Wrote file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to write file {file_path}: {e}")
            raise
    
    async def delete_file(self, file_path: Path):
        """Delete a markdown file"""
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"🗑️ Deleted file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {e}")
            raise
    
    def get_file_path(self, title: str) -> Path:
        """Get the file path for a given title"""
        # Sanitize title for filename
        safe_title = self._sanitize_filename(title)
        return self.sync_path / f"{safe_title}.md"
    
    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename"""
        # Remove or replace invalid characters
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        safe_title = safe_title.strip()
        
        # Limit length
        if len(safe_title) > 200:
            safe_title = safe_title[:200]
        
        return safe_title or "Untitled"
    
    def extract_frontmatter(self, content: str) -> tuple[Dict, str]:
        """Extract YAML frontmatter from markdown content"""
        frontmatter = {}
        body = content
        
        if content.startswith('---\n'):
            try:
                # Find end of frontmatter
                end_index = content.find('\n---\n', 4)
                if end_index != -1:
                    frontmatter_text = content[4:end_index]
                    body = content[end_index + 5:]
                    
                    # Parse YAML frontmatter
                    import yaml
                    frontmatter = yaml.safe_load(frontmatter_text) or {}
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse frontmatter: {e}")
        
        return frontmatter, body
    
    def add_frontmatter(self, content: str, metadata: Dict) -> str:
        """Add YAML frontmatter to markdown content"""
        if not metadata:
            return content
        
        import yaml
        
        # Extract existing frontmatter
        existing_frontmatter, body = self.extract_frontmatter(content)
        
        # Merge metadata
        existing_frontmatter.update(metadata)
        
        # Generate new frontmatter
        frontmatter_yaml = yaml.dump(existing_frontmatter, default_flow_style=False)
        
        return f"---\n{frontmatter_yaml}---\n{body}"
    
    def extract_wikilinks(self, content: str) -> Set[str]:
        """Extract all wikilinks from content"""
        return set(self.wikilink_pattern.findall(content))
    
    def convert_wikilinks_to_markdown(self, content: str, link_mapping: Dict[str, str]) -> str:
        """Convert wikilinks to markdown links using provided mapping"""
        def replace_link(match):
            link_text = match.group(1)
            if link_text in link_mapping:
                return f"[{link_text}]({link_mapping[link_text]})"
            return match.group(0)  # Keep original if no mapping
        
        return self.wikilink_pattern.sub(replace_link, content)
    
    def convert_markdown_links_to_wikilinks(self, content: str) -> str:
        """Convert markdown links to wikilinks where appropriate"""
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Only convert if it looks like an internal link
            if not link_url.startswith(('http://', 'https://', 'mailto:')):
                return f"[[{link_text}]]"
            
            return match.group(0)  # Keep original for external links
        
        return self.markdown_link_pattern.sub(replace_link, content)
    
    def extract_tags(self, content: str) -> Set[str]:
        """Extract hashtags from content"""
        tag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
        return set(tag_pattern.findall(content))
    
    def get_file_stats(self, file_path: Path) -> Dict:
        """Get file statistics"""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime)
        }
    
    async def backup_file(self, file_path: Path) -> Path:
        """Create a backup of a file before modifying"""
        if not file_path.exists():
            return file_path
        
        backup_path = file_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        
        try:
            content = await self.read_file(file_path)
            await self.write_file(backup_path, content)
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to backup file {file_path}: {e}")
            raise
    
    def find_files_by_title(self, title: str) -> List[Path]:
        """Find files that might match a given title"""
        safe_title = self._sanitize_filename(title)
        
        # Exact match
        exact_path = self.get_file_path(title)
        if exact_path.exists():
            return [exact_path]
        
        # Fuzzy search
        matches = []
        for file_path in self.get_all_files():
            if safe_title.lower() in file_path.stem.lower():
                matches.append(file_path)
        
        return matches
    
    async def get_all_links(self) -> Dict[str, Set[str]]:
        """Get all links from all files in the sync folder"""
        all_links = {}
        
        for file_path in self.get_all_files():
            try:
                content = await self.read_file(file_path)
                links = self.extract_wikilinks(content)
                all_links[file_path.stem] = links
            except Exception as e:
                self.logger.error(f"Failed to extract links from {file_path}: {e}")
        
        return all_links
    
    async def update_link_references(self, old_title: str, new_title: str):
        """Update all references to a renamed file"""
        old_link = f"[[{old_title}]]"
        new_link = f"[[{new_title}]]"
        
        for file_path in self.get_all_files():
            try:
                content = await self.read_file(file_path)
                
                if old_link in content:
                    updated_content = content.replace(old_link, new_link)
                    await self.write_file(file_path, updated_content)
                    self.logger.debug(f"Updated links in {file_path}")
                    
            except Exception as e:
                self.logger.error(f"Failed to update links in {file_path}: {e}")
    
    def get_orphaned_files(self) -> List[Path]:
        """Find files that aren't linked to by any other file"""
        # This would require analyzing all links across all files
        # Implementation depends on specific requirements
        return []
    
    def get_broken_links(self) -> Dict[Path, List[str]]:
        """Find broken wikilinks in all files"""
        # This would require checking if linked files exist
        # Implementation depends on specific requirements
        return {}

