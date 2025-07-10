"""
Notion to Obsidian Converter
Converts Notion pages to Obsidian-compatible markdown with intelligent formatting
"""

import re
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class NotionToObsidianConverter:
    """Converts Notion pages to Obsidian markdown format"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Mapping for Notion block types to markdown
        self.block_converters = {
            'paragraph': self._convert_paragraph,
            'heading_1': self._convert_heading_1,
            'heading_2': self._convert_heading_2,
            'heading_3': self._convert_heading_3,
            'bulleted_list_item': self._convert_bulleted_list,
            'numbered_list_item': self._convert_numbered_list,
            'to_do': self._convert_todo,
            'toggle': self._convert_toggle,
            'quote': self._convert_quote,
            'code': self._convert_code_block,
            'callout': self._convert_callout,
            'divider': self._convert_divider,
            'image': self._convert_image,
            'file': self._convert_file,
            'bookmark': self._convert_bookmark,
            'link_preview': self._convert_link_preview,
            'table': self._convert_table,
            'column_list': self._convert_columns,
            'embed': self._convert_embed
        }
    
    async def convert(self, notion_page: Dict) -> str:
        """Convert a Notion page to Obsidian markdown"""
        try:
            # Extract metadata
            metadata = self._extract_metadata(notion_page)
            
            # Convert content blocks
            content_blocks = notion_page.get('blocks', [])
            markdown_content = await self._convert_blocks(content_blocks)
            
            # Build final markdown with frontmatter
            frontmatter = self._build_frontmatter(metadata)
            
            if frontmatter:
                return f"{frontmatter}\n{markdown_content}"
            else:
                return markdown_content
                
        except Exception as e:
            self.logger.error(f"Failed to convert Notion page: {e}")
            raise
    
    def _extract_metadata(self, notion_page: Dict) -> Dict:
        """Extract metadata from Notion page properties"""
        metadata = {
            'notion_id': notion_page.get('id'),
            'created_time': notion_page.get('created_time'),
            'last_edited_time': notion_page.get('last_edited_time'),
            'url': notion_page.get('url')
        }
        
        # Extract properties
        properties = notion_page.get('properties', {})
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type')
            
            if prop_type == 'title':
                # Already handled as page title
                continue
            elif prop_type == 'rich_text':
                text_content = self._extract_rich_text(prop_data.get('rich_text', []))
                if text_content:
                    metadata[prop_name.lower().replace(' ', '_')] = text_content
            elif prop_type == 'number':
                number_value = prop_data.get('number')
                if number_value is not None:
                    metadata[prop_name.lower().replace(' ', '_')] = number_value
            elif prop_type == 'select':
                select_value = prop_data.get('select')
                if select_value:
                    metadata[prop_name.lower().replace(' ', '_')] = select_value.get('name')
            elif prop_type == 'multi_select':
                multi_select_values = prop_data.get('multi_select', [])
                if multi_select_values:
                    metadata[prop_name.lower().replace(' ', '_')] = [item.get('name') for item in multi_select_values]
            elif prop_type == 'date':
                date_value = prop_data.get('date')
                if date_value:
                    metadata[prop_name.lower().replace(' ', '_')] = date_value.get('start')
            elif prop_type == 'checkbox':
                checkbox_value = prop_data.get('checkbox')
                if checkbox_value is not None:
                    metadata[prop_name.lower().replace(' ', '_')] = checkbox_value
            elif prop_type == 'url':
                url_value = prop_data.get('url')
                if url_value:
                    metadata[prop_name.lower().replace(' ', '_')] = url_value
            elif prop_type == 'email':
                email_value = prop_data.get('email')
                if email_value:
                    metadata[prop_name.lower().replace(' ', '_')] = email_value
            elif prop_type == 'phone_number':
                phone_value = prop_data.get('phone_number')
                if phone_value:
                    metadata[prop_name.lower().replace(' ', '_')] = phone_value
        
        return metadata
    
    def _build_frontmatter(self, metadata: Dict) -> str:
        """Build YAML frontmatter from metadata"""
        if not metadata:
            return ""
        
        import yaml
        
        # Clean up metadata for YAML
        clean_metadata = {}
        for key, value in metadata.items():
            if value is not None and value != "":
                clean_metadata[key] = value
        
        if not clean_metadata:
            return ""
        
        try:
            yaml_content = yaml.dump(clean_metadata, default_flow_style=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
        except Exception as e:
            self.logger.warning(f"Failed to generate frontmatter: {e}")
            return ""
    
    async def _convert_blocks(self, blocks: List[Dict]) -> str:
        """Convert a list of Notion blocks to markdown"""
        markdown_lines = []
        
        for block in blocks:
            try:
                block_type = block.get('type')
                converter = self.block_converters.get(block_type, self._convert_unsupported)
                
                markdown = await converter(block)
                if markdown:
                    markdown_lines.append(markdown)
                    
            except Exception as e:
                self.logger.warning(f"Failed to convert block {block.get('id', 'unknown')}: {e}")
                # Add a placeholder for failed blocks
                markdown_lines.append(f"<!-- Failed to convert {block_type} block -->")
        
        return "\n\n".join(markdown_lines)
    
    async def _convert_paragraph(self, block: Dict) -> str:
        """Convert paragraph block"""
        paragraph_data = block.get('paragraph', {})
        rich_text = paragraph_data.get('rich_text', [])
        
        text = self._convert_rich_text(rich_text)
        
        # Handle children (nested content)
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                text += f"\n\n{child_content}"
        
        return text
    
    async def _convert_heading_1(self, block: Dict) -> str:
        """Convert heading 1 block"""
        heading_data = block.get('heading_1', {})
        rich_text = heading_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        return f"# {text}"
    
    async def _convert_heading_2(self, block: Dict) -> str:
        """Convert heading 2 block"""
        heading_data = block.get('heading_2', {})
        rich_text = heading_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        return f"## {text}"
    
    async def _convert_heading_3(self, block: Dict) -> str:
        """Convert heading 3 block"""
        heading_data = block.get('heading_3', {})
        rich_text = heading_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        return f"### {text}"
    
    async def _convert_bulleted_list(self, block: Dict) -> str:
        """Convert bulleted list item"""
        list_data = block.get('bulleted_list_item', {})
        rich_text = list_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        
        result = f"- {text}"
        
        # Handle nested items
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                # Indent child content
                indented_content = "\n".join(f"  {line}" for line in child_content.split("\n"))
                result += f"\n{indented_content}"
        
        return result
    
    async def _convert_numbered_list(self, block: Dict) -> str:
        """Convert numbered list item"""
        list_data = block.get('numbered_list_item', {})
        rich_text = list_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        
        result = f"1. {text}"
        
        # Handle nested items
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                # Indent child content
                indented_content = "\n".join(f"   {line}" for line in child_content.split("\n"))
                result += f"\n{indented_content}"
        
        return result
    
    async def _convert_todo(self, block: Dict) -> str:
        """Convert to-do block"""
        todo_data = block.get('to_do', {})
        rich_text = todo_data.get('rich_text', [])
        checked = todo_data.get('checked', False)
        
        text = self._convert_rich_text(rich_text)
        checkbox = "[x]" if checked else "[ ]"
        
        result = f"- {checkbox} {text}"
        
        # Handle nested items
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                indented_content = "\n".join(f"  {line}" for line in child_content.split("\n"))
                result += f"\n{indented_content}"
        
        return result
    
    async def _convert_toggle(self, block: Dict) -> str:
        """Convert toggle block"""
        toggle_data = block.get('toggle', {})
        rich_text = toggle_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        
        result = f"<details>\n<summary>{text}</summary>\n"
        
        # Handle children
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                result += f"\n{child_content}\n"
        
        result += "</details>"
        return result
    
    async def _convert_quote(self, block: Dict) -> str:
        """Convert quote block"""
        quote_data = block.get('quote', {})
        rich_text = quote_data.get('rich_text', [])
        text = self._convert_rich_text(rich_text)
        
        # Convert to blockquote
        lines = text.split('\n')
        quoted_lines = [f"> {line}" for line in lines]
        
        result = "\n".join(quoted_lines)
        
        # Handle children
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                child_lines = child_content.split('\n')
                quoted_child_lines = [f"> {line}" for line in child_lines]
                result += "\n" + "\n".join(quoted_child_lines)
        
        return result
    
    async def _convert_code_block(self, block: Dict) -> str:
        """Convert code block"""
        code_data = block.get('code', {})
        rich_text = code_data.get('rich_text', [])
        language = code_data.get('language', '')
        
        code_content = self._extract_rich_text(rich_text)
        
        return f"```{language}\n{code_content}\n```"
    
    async def _convert_callout(self, block: Dict) -> str:
        """Convert callout block"""
        callout_data = block.get('callout', {})
        rich_text = callout_data.get('rich_text', [])
        icon = callout_data.get('icon', {})
        
        text = self._convert_rich_text(rich_text)
        
        # Extract icon
        icon_text = ""
        if icon.get('type') == 'emoji':
            icon_text = icon.get('emoji', '')
        
        result = f"> {icon_text} {text}"
        
        # Handle children
        children = block.get('children', [])
        if children:
            child_content = await self._convert_blocks(children)
            if child_content:
                child_lines = child_content.split('\n')
                quoted_child_lines = [f"> {line}" for line in child_lines]
                result += "\n" + "\n".join(quoted_child_lines)
        
        return result
    
    async def _convert_divider(self, block: Dict) -> str:
        """Convert divider block"""
        return "---"
    
    async def _convert_image(self, block: Dict) -> str:
        """Convert image block"""
        image_data = block.get('image', {})
        
        # Get image URL
        image_url = ""
        if image_data.get('type') == 'external':
            image_url = image_data.get('external', {}).get('url', '')
        elif image_data.get('type') == 'file':
            image_url = image_data.get('file', {}).get('url', '')
        
        # Get caption
        caption_text = ""
        caption = image_data.get('caption', [])
        if caption:
            caption_text = self._extract_rich_text(caption)
        
        if caption_text:
            return f"![{caption_text}]({image_url})"
        else:
            return f"![]({image_url})"
    
    async def _convert_file(self, block: Dict) -> str:
        """Convert file block"""
        file_data = block.get('file', {})
        
        # Get file URL and name
        file_url = ""
        file_name = "file"
        
        if file_data.get('type') == 'external':
            file_url = file_data.get('external', {}).get('url', '')
        elif file_data.get('type') == 'file':
            file_url = file_data.get('file', {}).get('url', '')
        
        # Try to get filename from caption or URL
        caption = file_data.get('caption', [])
        if caption:
            file_name = self._extract_rich_text(caption)
        elif file_url:
            file_name = file_url.split('/')[-1]
        
        return f"[{file_name}]({file_url})"
    
    async def _convert_bookmark(self, block: Dict) -> str:
        """Convert bookmark block"""
        bookmark_data = block.get('bookmark', {})
        url = bookmark_data.get('url', '')
        
        caption = bookmark_data.get('caption', [])
        if caption:
            caption_text = self._extract_rich_text(caption)
            return f"[{caption_text}]({url})"
        else:
            return f"<{url}>"
    
    async def _convert_link_preview(self, block: Dict) -> str:
        """Convert link preview block"""
        link_data = block.get('link_preview', {})
        url = link_data.get('url', '')
        return f"<{url}>"
    
    async def _convert_table(self, block: Dict) -> str:
        """Convert table block (simplified)"""
        # Table conversion is complex and would require getting child rows
        # For now, return a placeholder
        return "<!-- Table content - manual conversion required -->"
    
    async def _convert_columns(self, block: Dict) -> str:
        """Convert column list block"""
        # Column layout doesn't translate well to markdown
        # Convert children as regular content
        children = block.get('children', [])
        if children:
            return await self._convert_blocks(children)
        return ""
    
    async def _convert_embed(self, block: Dict) -> str:
        """Convert embed block"""
        embed_data = block.get('embed', {})
        url = embed_data.get('url', '')
        
        caption = embed_data.get('caption', [])
        if caption:
            caption_text = self._extract_rich_text(caption)
            return f"[{caption_text}]({url})"
        else:
            return f"<{url}>"
    
    async def _convert_unsupported(self, block: Dict) -> str:
        """Handle unsupported block types"""
        block_type = block.get('type', 'unknown')
        return f"<!-- Unsupported block type: {block_type} -->"
    
    def _convert_rich_text(self, rich_text_array: List[Dict]) -> str:
        """Convert Notion rich text to markdown"""
        if not rich_text_array:
            return ""
        
        result = []
        
        for text_obj in rich_text_array:
            text_content = text_obj.get('plain_text', '')
            annotations = text_obj.get('annotations', {})
            
            # Apply formatting
            if annotations.get('bold'):
                text_content = f"**{text_content}**"
            if annotations.get('italic'):
                text_content = f"*{text_content}*"
            if annotations.get('strikethrough'):
                text_content = f"~~{text_content}~~"
            if annotations.get('code'):
                text_content = f"`{text_content}`"
            
            # Handle links
            if text_obj.get('href'):
                href = text_obj.get('href')
                text_content = f"[{text_content}]({href})"
            
            # Handle mentions (convert to wikilinks for Obsidian)
            if text_obj.get('type') == 'mention':
                mention = text_obj.get('mention', {})
                if mention.get('type') == 'page':
                    # This would require looking up the page title
                    # For now, use the plain text
                    text_content = f"[[{text_content}]]"
            
            result.append(text_content)
        
        return "".join(result)
    
    def _extract_rich_text(self, rich_text_array: List[Dict]) -> str:
        """Extract plain text from rich text array"""
        if not rich_text_array:
            return ""
        
        return "".join([text_obj.get('plain_text', '') for text_obj in rich_text_array])

