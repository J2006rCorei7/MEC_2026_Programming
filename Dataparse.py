import json




def parse_json_file(toronto-downtown.json):
    with open(toronto-downtown.json, 'r') as f:
        data = json.load(f)

    # Defined variables 
    g_zoom = 0
    g_center = (0,0)
    g_name = ""
    g_id = ""


    nodes = []
    pois = []
    edges = []
    trucks = []
    hubs = []


    g_id = data['id']
    g_name = data['name']
    g_zoom = data['zoom']
    g_center = tuple(data['center'])


    for item in data['nodes']:
        node = Node(item['id'], item['name'], item['lat'], item['lng'])
        nodes.append(node)

    for item in data['pois']:
        poi = Poi(item['id'], item['name'], item['kind'], item['node'], item['lat'], item['lng'], item['address'])
        pois.append(poi)

    for item in data['edges']:
        edge = Edge(item['id'], item['a'], item['b'], item['km'], item['w'], item['street'], item['hwy'], item['terrain'])
        edges.append(edge)

    for item in data['trucks']:
        truck = Truck(item['id'], item['name'], item['home'], item['refrigerated'], item['capacity'], item['fuel'])
        trucks.append(truck)

    for item in data['hubs']:
        hub = Hub(item['poiId'], item['normal'], item['cold'])
        hubs.append(hub)

    return g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs


    











# Classes for the data structures
class Poi:
    def __init__(self, id, name, kind, node, lat, lng, address):
        self.id = id
        self.name = name
        self.kind = kind
        self.node = node
        self.lat = lat
        self.lng = lng
        self.address = address


    def __str__(self):
        return f"""POI: ID{self.id}, Name: {self.name}, Latitude: {self.lat}, 
                Longitude: {self.lng}, Kind: {self.kind},
                Node: {self.node}, Address: {self.address}"""


class Edge:
    def __init__(self, id, a, b, km, w, street, hwy: bool, terrain):
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

class Node:
    def __init__(self, id, name, lat, lng):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return f"""Node: ID{self.id}, Name: {self.name}, Latitude: {self.lat}, Longitude: {self.lng}"""

class Truck:
    def __init__(self, id, name, home, refrigerated: bool, capacity, fuel):
        self.id = id
        self.name = name
        self.home = home
        self.refrigerated = refrigerated
        self.capacity = capacity
        self.fuel = fuel

    def __str__(self):
        return f"""Truck: ID{self.id}, Name: {self.name}, Home: {self.home}, Refrigerated: {self.refrigerated},
            Capacity: {self.capacity}, Fuel: {self.fuel}"""
    
class Hub:
    def __init__(self, poiId, normal, cold):
        self.poiId = poiId
        self.normal = normal
        self.cold = cold

    def __str__(self):
        return f"""Hub: POI ID{self.poiId}, Normal Capacity: {self.normal}, Cold Capacity: {self.cold}"""


