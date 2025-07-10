"""
Obsidian to Notion Converter
Converts Obsidian markdown to Notion-compatible format with intelligent parsing
"""

import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import yaml

class ObsidianToNotionConverter:
    """Converts Obsidian markdown to Notion format"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for markdown parsing
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        self.markdown_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
        self.italic_pattern = re.compile(r'\*([^*]+)\*')
        self.strikethrough_pattern = re.compile(r'~~([^~]+)~~')
        self.blockquote_pattern = re.compile(r'^>\s+(.+)$', re.MULTILINE)
        self.list_pattern = re.compile(r'^(\s*)[-*+]\s+(.+)$', re.MULTILINE)
        self.numbered_list_pattern = re.compile(r'^(\s*)\d+\.\s+(.+)$', re.MULTILINE)
        self.todo_pattern = re.compile(r'^(\s*)[-*+]\s+\[([ x])\]\s+(.+)$', re.MULTILINE)
        self.tag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
    
    async def convert(self, markdown_content: str, file_path: Path) -> Dict:
        """Convert Obsidian markdown to Notion page data"""
        try:
            # Parse frontmatter and content
            frontmatter, content = self._parse_frontmatter(markdown_content)
            
            # Extract title (from frontmatter or filename)
            title = frontmatter.get('title') or file_path.stem
            
            # Convert markdown content to Notion blocks
            blocks = await self._convert_content_to_blocks(content)
            
            # Build Notion page data
            notion_data = {
                'title': title,
                'properties': self._build_properties(frontmatter, content),
                'blocks': blocks,
                'last_modified': file_path.stat().st_mtime if file_path.exists() else None
            }
            
            return notion_data
            
        except Exception as e:
            self.logger.error(f"Failed to convert Obsidian file {file_path}: {e}")
            raise
    
    def _parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter from markdown content"""
        frontmatter = {}
        body = content
        
        if content.startswith('---\n'):
            try:
                # Find end of frontmatter
                end_index = content.find('\n---\n', 4)
                if end_index != -1:
                    frontmatter_text = content[4:end_index]
                    body = content[end_index + 5:].strip()
                    
                    # Parse YAML
                    frontmatter = yaml.safe_load(frontmatter_text) or {}
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse frontmatter: {e}")
        
        return frontmatter, body
    
    def _build_properties(self, frontmatter: Dict, content: str) -> Dict:
        """Build Notion properties from frontmatter and content analysis"""
        properties = {}
        
        # Convert frontmatter to Notion properties
        for key, value in frontmatter.items():
            if key == 'title':
                continue  # Title is handled separately
            
            notion_key = key.replace('_', ' ').title()
            
            if isinstance(value, str):
                properties[notion_key] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": value
                            }
                        }
                    ]
                }
            elif isinstance(value, (int, float)):
                properties[notion_key] = {
                    "number": value
                }
            elif isinstance(value, bool):
                properties[notion_key] = {
                    "checkbox": value
                }
            elif isinstance(value, list):
                # Convert to multi-select
                properties[notion_key] = {
                    "multi_select": [
                        {"name": str(item)} for item in value
                    ]
                }
        
        # Extract tags from content
        tags = self.tag_pattern.findall(content)
        if tags:
            properties["Tags"] = {
                "multi_select": [
                    {"name": tag} for tag in set(tags)
                ]
            }
        
        return properties
    
    async def _convert_content_to_blocks(self, content: str) -> List[Dict]:
        """Convert markdown content to Notion blocks"""
        blocks = []
        
        # Split content into sections by double newlines
        sections = re.split(r'\n\s*\n', content.strip())
        
        for section in sections:
            if not section.strip():
                continue
            
            try:
                block = await self._convert_section_to_block(section.strip())
                if block:
                    blocks.append(block)
            except Exception as e:
                self.logger.warning(f"Failed to convert section: {e}")
                # Add as plain paragraph
                blocks.append(self._create_paragraph_block(section))
        
        return blocks
    
    async def _convert_section_to_block(self, section: str) -> Optional[Dict]:
        """Convert a section of markdown to a Notion block"""
        section = section.strip()
        
        if not section:
            return None
        
        # Check for different block types
        
        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', section)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            return self._create_heading_block(text, level)
        
        # Code blocks
        code_match = self.code_block_pattern.match(section)
        if code_match:
            language = code_match.group(1) or 'plain text'
            code_content = code_match.group(2)
            return self._create_code_block(code_content, language)
        
        # Blockquotes
        if section.startswith('>'):
            quote_text = re.sub(r'^>\s*', '', section, flags=re.MULTILINE)
            return self._create_quote_block(quote_text)
        
        # Lists (bulleted)
        if re.match(r'^[-*+]\s+', section):
            return await self._create_list_block(section, 'bulleted_list_item')
        
        # Lists (numbered)
        if re.match(r'^\d+\.\s+', section):
            return await self._create_list_block(section, 'numbered_list_item')
        
        # To-do items
        if re.match(r'^[-*+]\s+\[([ x])\]\s+', section):
            return await self._create_todo_block(section)
        
        # Images
        image_match = self.image_pattern.search(section)
        if image_match:
            alt_text = image_match.group(1)
            image_url = image_match.group(2)
            return self._create_image_block(image_url, alt_text)
        
        # Horizontal rule
        if section.strip() in ['---', '***', '___']:
            return self._create_divider_block()
        
        # Default to paragraph
        return self._create_paragraph_block(section)
    
    def _create_heading_block(self, text: str, level: int) -> Dict:
        """Create a heading block"""
        heading_type = f"heading_{min(level, 3)}"  # Notion only supports h1-h3
        
        return {
            "type": heading_type,
            heading_type: {
                "rich_text": self._convert_text_to_rich_text(text)
            }
        }
    
    def _create_paragraph_block(self, text: str) -> Dict:
        """Create a paragraph block"""
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": self._convert_text_to_rich_text(text)
            }
        }
    
    def _create_code_block(self, code: str, language: str) -> Dict:
        """Create a code block"""
        return {
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": code
                        }
                    }
                ],
                "language": language.lower() if language else "plain text"
            }
        }
    
    def _create_quote_block(self, text: str) -> Dict:
        """Create a quote block"""
        return {
            "type": "quote",
            "quote": {
                "rich_text": self._convert_text_to_rich_text(text)
            }
        }
    
    async def _create_list_block(self, text: str, list_type: str) -> Dict:
        """Create a list item block"""
        # Extract the first list item
        if list_type == 'bulleted_list_item':
            match = re.match(r'^[-*+]\s+(.+)', text)
        else:  # numbered_list_item
            match = re.match(r'^\d+\.\s+(.+)', text)
        
        if match:
            item_text = match.group(1)
            return {
                "type": list_type,
                list_type: {
                    "rich_text": self._convert_text_to_rich_text(item_text)
                }
            }
        
        # Fallback to paragraph
        return self._create_paragraph_block(text)
    
    async def _create_todo_block(self, text: str) -> Dict:
        """Create a to-do block"""
        match = re.match(r'^[-*+]\s+\[([ x])\]\s+(.+)', text)
        if match:
            checked = match.group(1) == 'x'
            todo_text = match.group(2)
            
            return {
                "type": "to_do",
                "to_do": {
                    "rich_text": self._convert_text_to_rich_text(todo_text),
                    "checked": checked
                }
            }
        
        # Fallback to paragraph
        return self._create_paragraph_block(text)
    
    def _create_image_block(self, url: str, alt_text: str = "") -> Dict:
        """Create an image block"""
        block = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": url
                }
            }
        }
        
        if alt_text:
            block["image"]["caption"] = [
                {
                    "type": "text",
                    "text": {
                        "content": alt_text
                    }
                }
            ]
        
        return block
    
    def _create_divider_block(self) -> Dict:
        """Create a divider block"""
        return {
            "type": "divider",
            "divider": {}
        }
    
    def _convert_text_to_rich_text(self, text: str) -> List[Dict]:
        """Convert markdown text to Notion rich text format"""
        # This is a simplified conversion - a full implementation would need
        # to handle overlapping formatting and preserve exact positions
        
        rich_text = []
        
        # For now, create a single text object and apply basic formatting detection
        # A more sophisticated implementation would parse the text more carefully
        
        # Convert wikilinks to mentions (simplified)
        text = self.wikilink_pattern.sub(r'[\1]', text)
        
        # Create basic rich text object
        rich_text_obj = {
            "type": "text",
            "text": {
                "content": text
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            }
        }
        
        # Simple formatting detection (this could be much more sophisticated)
        if '**' in text or '__' in text:
            rich_text_obj["annotations"]["bold"] = True
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'__([^_]+)__', r'\1', text)
            rich_text_obj["text"]["content"] = text
        
        if '*' in text or '_' in text:
            rich_text_obj["annotations"]["italic"] = True
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'_([^_]+)_', r'\1', text)
            rich_text_obj["text"]["content"] = text
        
        if '~~' in text:
            rich_text_obj["annotations"]["strikethrough"] = True
            text = re.sub(r'~~([^~]+)~~', r'\1', text)
            rich_text_obj["text"]["content"] = text
        
        if '`' in text and not text.startswith('```'):
            rich_text_obj["annotations"]["code"] = True
            text = re.sub(r'`([^`]+)`', r'\1', text)
            rich_text_obj["text"]["content"] = text
        
        # Handle links
        link_match = self.markdown_link_pattern.search(text)
        if link_match:
            link_text = link_match.group(1)
            link_url = link_match.group(2)
            
            rich_text_obj["text"]["content"] = link_text
            rich_text_obj["href"] = link_url
        
        rich_text.append(rich_text_obj)
        
        return rich_text
    
    def _extract_wikilinks(self, text: str) -> List[str]:
        """Extract wikilinks from text"""
        return self.wikilink_pattern.findall(text)
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return self.tag_pattern.findall(text)

