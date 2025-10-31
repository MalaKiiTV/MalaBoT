# Role Connections Backup and Recovery System

## Problem
Role connections were lost, possibly due to:
- Database reset/deletion
- Database corruption
- Settings table cleared
- Migration issues

## Solution: Add Backup System

### 1. Automatic Backup on Save
Every time role connections are saved, create a backup file.

### 2. Manual Export Command
Add `/roleconnections export` command to save connections to a file.

### 3. Manual Import Command
Add `/roleconnections import` command to restore from backup.

### 4. Backup File Format
```json
{
  "guild_id": 123456789,
  "timestamp": "2024-10-30T12:00:00",
  "connections": [
    {
      "id": "conn_1",
      "target_role_id": 123456789,
      "action": "give",
      "conditions": [
        {"role_id": 987654321, "type": "has"}
      ],
      "logic": "AND",
      "enabled": true
    }
  ],
  "protected_roles": [123456789, 987654321]
}
```

## Implementation Plan

### File: `cogs/role_connections.py`

Add these methods to RoleConnectionManager:

```python
async def backup_connections(self, guild_id: int):
    """Create backup file of connections"""
    import os
    from datetime import datetime
    
    connections = self.connections_cache.get(guild_id, [])
    protected = self.protected_roles_cache.get(guild_id, [])
    
    backup_data = {
        "guild_id": guild_id,
        "timestamp": datetime.now().isoformat(),
        "connections": [conn.to_dict() for conn in connections],
        "protected_roles": protected
    }
    
    # Create backups directory if it doesn't exist
    os.makedirs("data/backups", exist_ok=True)
    
    # Save backup file
    filename = f"data/backups/role_connections_{guild_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    log_system(f"[ROLE_CONNECTION] Backup created: {filename}")
    return filename

async def restore_connections(self, guild_id: int, backup_file: str):
    """Restore connections from backup file"""
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Verify guild_id matches
        if backup_data["guild_id"] != guild_id:
            raise ValueError("Backup file is for a different guild")
        
        # Restore connections
        self.connections_cache[guild_id] = [
            RoleConnection(
                connection_id=conn["id"],
                guild_id=guild_id,
                target_role_id=conn["target_role_id"],
                action=conn["action"],
                conditions=conn["conditions"],
                logic=conn.get("logic", "AND"),
                enabled=conn.get("enabled", True)
            )
            for conn in backup_data["connections"]
        ]
        
        # Restore protected roles
        self.protected_roles_cache[guild_id] = backup_data["protected_roles"]
        
        # Save to database
        await self.save_connections(guild_id)
        await self.save_protected_roles(guild_id)
        
        log_system(f"[ROLE_CONNECTION] Restored from backup: {backup_file}")
        return True
    except Exception as e:
        log_system(f"[ROLE_CONNECTION] Error restoring backup: {e}", level="error")
        return False
```

Modify save_connections to auto-backup:

```python
async def save_connections(self, guild_id: int):
    """Save connections to database with automatic backup"""
    connections = self.connections_cache.get(guild_id, [])
    data = [conn.to_dict() for conn in connections]
    await self.db.set_setting(f"role_connections_{guild_id}", json.dumps(data))
    
    # Auto-backup if connections exist
    if connections:
        try:
            await self.backup_connections(guild_id)
        except Exception as e:
            log_system(f"[ROLE_CONNECTION] Auto-backup failed: {e}", level="warning")
```

### Add Commands

```python
@app_commands.command(name="export", description="Export role connections to backup file")
async def export_connections(self, interaction: discord.Interaction):
    """Export role connections"""
    await interaction.response.defer(ephemeral=True)
    
    role_conn_cog = interaction.client.get_cog("RoleConnections")
    if not role_conn_cog:
        await interaction.followup.send("Role Connections system not loaded", ephemeral=True)
        return
    
    manager = role_conn_cog.manager
    await manager.load_connections(interaction.guild.id)
    
    filename = await manager.backup_connections(interaction.guild.id)
    
    # Send file to user
    await interaction.followup.send(
        "Role connections exported!",
        file=discord.File(filename),
        ephemeral=True
    )

@app_commands.command(name="import", description="Import role connections from backup file")
async def import_connections(self, interaction: discord.Interaction, file: discord.Attachment):
    """Import role connections"""
    await interaction.response.defer(ephemeral=True)
    
    # Download file
    backup_path = f"data/backups/temp_{interaction.user.id}.json"
    await file.save(backup_path)
    
    role_conn_cog = interaction.client.get_cog("RoleConnections")
    if not role_conn_cog:
        await interaction.followup.send("Role Connections system not loaded", ephemeral=True)
        return
    
    manager = role_conn_cog.manager
    success = await manager.restore_connections(interaction.guild.id, backup_path)
    
    if success:
        await interaction.followup.send("✅ Role connections restored!", ephemeral=True)
    else:
        await interaction.followup.send("❌ Failed to restore connections", ephemeral=True)
```

## Usage

### Export Connections
```
/roleconnections export
```
Downloads a JSON file with all your role connections.

### Import Connections
```
/roleconnections import [file]
```
Upload the backup JSON file to restore connections.

## Benefits

1. **Automatic Backups** - Every save creates a backup
2. **Manual Export** - Download connections anytime
3. **Easy Recovery** - Restore from backup file
4. **Version History** - Timestamped backups
5. **Portable** - Move connections between servers

## Backup Location

```
data/backups/role_connections_{guild_id}_{timestamp}.json
```

Example:
```
data/backups/role_connections_542004156513255445_20241030_120000.json
```

## Recovery Steps

If role connections are lost:

1. Check `data/backups/` folder
2. Find most recent backup for your guild
3. Use `/roleconnections import` to restore
4. OR manually copy JSON to database

## Prevention

- Regular exports (weekly recommended)
- Keep backups in safe location
- Monitor database file size
- Check logs for errors