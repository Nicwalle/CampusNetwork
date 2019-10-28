class Router:
    def __init__(self, name, id, ip, subnet, interfaces):
        self.interfaces = interfaces
        self.subnet = subnet
        self.ip = ip
        self.links = []
        self.id = id
        self.name = name

    @staticmethod
    def from_json(source):
        return Router(
            name=source.get("name"),
            id=source.get("id"),
            ip=source.get("ip"),
            subnet=source.get("subnet"),
            interfaces=source.get("interfaces")
        )