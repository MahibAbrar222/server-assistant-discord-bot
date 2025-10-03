import json


class Guilds:
    """Manages Discord guild/server data persistence."""
    
    def __init__(self):
        self.servers = {}
        self.refresh_servers()
    
    def refresh_servers(self):
        """Reload server data from the JSON file."""
        self.servers = {}
        with open('servers.json', 'r') as f:
            self.servers = json.load(f)
    
    def save_server(self, server_id, server_name, system_channel_id=None, owner_id=None):
        """Save or update server information."""
        server_id = str(server_id)
        self.servers["servers"][server_id] = {
            "server_name": server_name,
            "system_channel_id": system_channel_id,
            "welcome_channel": None,
            "admins": [str(owner_id)] if owner_id else []
        }

        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refresh_servers()
    
    def remove_server(self, server_id):
        """Remove a server from the database."""
        del self.servers["servers"][str(server_id)]
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refresh_servers()
    
    def get_server(self, server_id):
        """Get server data by server ID."""
        server_id = str(server_id)
        return self.servers["servers"][server_id]
    
    def get_server_name(self, server_id):
        """Get server name by server ID."""
        server_id = str(server_id)
        return self.servers["servers"][server_id]["server_name"]
    
    def server_exists(self, server_id):
        """Check if a server exists in the database."""
        server_id = str(server_id)
        return server_id in self.servers["servers"]
    
    def set_welcome_channel(self, server_id, channel_id):
        """Set the welcome channel for a server."""
        server_id = str(server_id)
        self.servers["servers"][server_id]["welcome_channel"] = channel_id
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refresh_servers()
    
    def add_admin(self, server_id, user_id):
        """Add an admin to a server."""
        server_id = str(server_id)
        self.servers["servers"][server_id]["admins"].append(str(user_id))
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refresh_servers()
    
    def get_admins(self, server_id):
        """Get list of admins for a server."""
        server_id = str(server_id)
        return self.servers["servers"][server_id]["admins"]
    
    def remove_admin(self, server_id, user_id):
        """Remove an admin from a server."""
        server_id = str(server_id)
        self.servers["servers"][server_id]["admins"].remove(user_id)
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refresh_servers()
