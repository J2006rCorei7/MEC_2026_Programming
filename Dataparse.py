class Poi:
    def __init__(self, id, name, kind, node, latitude, longitude, address):
        self.id = id
        self.name = name
        self.kind = kind
        self.node = node
        self.latitude = latitude
        self.longitude = longitude
        self.address = address


    def __str__(self):
        return f"""POI: ID{self.id}, Name: {self.name}, Latitude: {self.latitude}, 
                Longitude: {self.longitude}, Kind: {self.kind},
                Node: {self.node}, Address: {self.address}"""


class Edge:
    def __init__(self, id, a, b, km, w, street, hwy, terrain):
        self.id = id
        self.node1 = a
        self.node2 = b
        self.km = km
        self.w = w
        self.street = street
        self.hwy = hwy
        self.terrain = terrain        


    def __str__(self):
        return f"""Edge: ID{self.id}, Street: {self.street}, Highway: {self.hwy},
            Node1: {self.node1}, Node2: {self.node2}, Distance: {self.km} km,
            Weight: {self.w}, Terrain: {self.terrain}"""


