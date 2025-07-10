# Notion ↔ Obsidian Bidirectional Sync

🔄 **Invisible Intelligence**: Seamlessly sync your knowledge between Notion's powerful databases and Obsidian's knowledge graph.

## ✨ Features

### **Bidirectional Sync**
- **Notion → Obsidian**: Convert Notion pages to Markdown with preserved formatting
- **Obsidian → Notion**: Sync markdown files to Notion with metadata preservation
- **Real-time updates**: Changes in either platform automatically sync to the other

### **Smart Link Conversion**
- **Obsidian `[[links]]` → Notion page mentions**
- **Notion page references → Obsidian wikilinks**
- **Preserve knowledge graph connections across platforms**

### **Intelligent Content Mapping**
- **Database entries** → **Structured notes** with frontmatter
- **Tags and properties** preserved across platforms
- **Attachments and images** synced automatically

### **Conflict Resolution**
- **Smart merge** for simultaneous edits
- **Version history** preservation
- **User-defined priority** rules

## 🚀 Quick Start

1. **Configure your credentials**:
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit with your Notion token and Obsidian vault path
   ```

2. **Run the sync**:
   ```bash
   python sync_manager.py --initial-sync
   ```

3. **Enable continuous sync**:
   ```bash
   python sync_manager.py --watch
   ```

## 🛠️ Architecture

- **`sync_manager.py`**: Main orchestrator
- **`notion_client/`**: Notion API integration
- **`obsidian_client/`**: Obsidian vault management
- **`converters/`**: Content format conversion
- **`conflict_resolver/`**: Smart merge logic
- **`watchers/`**: Real-time change detection

## 🎯 Your Experience

**Just work naturally in either platform** - the sync happens invisibly in the background, maintaining your knowledge graph connections across both systems.

