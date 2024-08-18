import json

class Guilds:
    def __init__(self):
        self.servers = {}
        self.refeshServers()
    def refeshServers(self):
        self.servers = {}
        with open('servers.json', 'r') as f:
            self.servers = json.load(f)
    def saveServers(self, server_id, server_name, system_channel_id=None, owner_id=None):
        server_id = str(server_id)
        self.servers["servers"][server_id] = {}

        self.servers["servers"][server_id]["server_name"] = server_name

        if system_channel_id:
            self.servers["servers"][server_id]["system_channel_id"] = system_channel_id
        else:
            self.servers["servers"][server_id]["system_channel_id"] = None
        
        self.servers["servers"][server_id]["welcome_channel"] = None

        if owner_id:
            self.servers["servers"][server_id]["admins"] = [str(owner_id)]
        else:
            self.servers["servers"][server_id]["admins"] = []

        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refeshServers()
    def removeServer(self, server_id):
        del self.servers["servers"][str(server_id)]
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refeshServers()
    def getServer(self, server_id):
        server_id = str(server_id)

        return self.servers["servers"][server_id]
    def getServerName(self, server_id):
        server_id = str(server_id)

        return self.servers["servers"][server_id]["server_name"]
    def ifServerExists(self, server_id):
        server_id = str(server_id)

        if server_id in self.servers["servers"]:
            return True
        else:
            return False
    def setWelcomeChannel(self, server_id, channel_id):
        server_id = str(server_id)
        self.servers["servers"][server_id]["welcome_channel"] = channel_id
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refeshServers()
    
    # Admin
    def addAdmin(self, server_id, user_id):
        server_id = str(server_id)
        self.servers["servers"][server_id]["admins"].append(str(user_id))
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refeshServers()
    def getAdmins(self, server_id):
        server_id = str(server_id)
        return self.servers["servers"][server_id]["admins"]
    def removeAdmin(self, server_id, user_id):
        server_id = str(server_id)
        self.servers["servers"][server_id]["admins"].remove(user_id)
        with open('servers.json', 'w') as f:
            json.dump(self.servers, f, indent=4)
        self.refeshServers()
