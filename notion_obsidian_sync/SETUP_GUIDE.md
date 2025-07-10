# 🚀 Quick Setup Guide

## Step 1: Get Your Notion Integration Token

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New Integration"
3. Name it "Obsidian Sync" 
4. Copy the **Internal Integration Secret** (this is your token)

## Step 2: Share Databases with Integration

1. Open each Notion database you want to sync
2. Click the "..." menu → "Add connections"
3. Select your "Obsidian Sync" integration

## Step 3: Get Database IDs

1. Open your Notion database in browser
2. Copy the ID from the URL: `https://notion.so/your-workspace/DATABASE_ID?v=...`
3. The DATABASE_ID is the long string of letters/numbers

## Step 4: Configure the Sync

1. Copy `config/config.example.yaml` to `config/config.yaml`
2. Fill in your details:
   ```yaml
   notion:
     token: "secret_your_token_here"
     database_ids:
       - "your_database_id_here"
   
   obsidian:
     vault_path: "/path/to/your/obsidian/vault"
   ```

## Step 5: Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run initial sync
python sync_manager.py --initial-sync

# Start continuous sync
python sync_manager.py --watch
```

## 🎯 Your Experience

- **Write naturally** in either Notion or Obsidian
- **Links automatically convert**: `[[Obsidian links]]` ↔ Notion page mentions
- **Properties sync**: Frontmatter ↔ Notion database properties  
- **Real-time updates**: Changes sync within 30 seconds
- **Conflict resolution**: Smart merging when both sides change

## 🔧 Customization

Edit `config/config.yaml` to:
- Change sync frequency
- Customize property mappings
- Set conflict resolution strategy
- Configure file naming patterns

## 🆘 Troubleshooting

**Sync not working?**
- Check your Notion token is correct
- Verify database IDs are right
- Ensure integration has access to databases
- Check file paths are correct

**Conflicts?**
- Check the conflict files created in your vault
- Adjust conflict resolution strategy in config
- Review the logs for details

Ready to experience invisible intelligence! 🧠✨

