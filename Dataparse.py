import json
from pathlib import Path

folder = Path(__file__).parent / "dataset"

def parse_json_file():
    try:
        json_file = next(folder.glob("*.json"))

        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

    except StopIteration:
        print(f"Could not find any JSON files inside the folder: {folder}")
    except FileNotFoundError:
        print(f"The subfolder '{folder.name}' does not exist next to this script.")

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
    """Represent a point of interest on the map."""

    def __init__(self, id, name, kind, node, lat, lng, address, aval=True):
        """Initialize a point of interest with its map and address data."""
        self.id = id
        self.name = name
        self.kind = kind
        self.node = node
        self.lat = lat
        self.lng = lng
        self.address = address
        self.aval = aval


    def __str__(self):
        """Return a readable description of the point of interest."""
        return f"""POI: ID {self.id}, Name: {self.name}, Latitude: {self.lat}, 
                Longitude: {self.lng}, Kind: {self.kind},
                Node: {self.node}, Address: {self.address}, Available: {self.aval}"""



class Edge:
    """Represent a connection between two nodes."""
    
    def __init__(self, id, a, b, km, w, street, hwy: bool, terrain, aval=True):
        """Initialize an edge with its nodes, distance, and road data."""
        self.id = id
        self.node1 = a
        self.node2 = b
        self.km = km
        self.w = w
        self.street = street
        self.hwy = hwy
        self.terrain = terrain
        self.aval = aval


    def __str__(self):
        """Return a readable description of the edge."""
        return f"""Edge: ID {self.id}, Street: {self.street}, Highway: {self.hwy},
            Node1: {self.node1}, Node2: {self.node2}, Distance: {self.km} km,
            Weight: {self.w}, Terrain: {self.terrain}, Available: {self.aval}"""

class Node:
    """Represent a location node on the map."""

    def __init__(self, id, name, lat, lng):
        """Initialize a node with its identifier, name, and coordinates."""
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng

    def __str__(self):
        """Return a readable description of the node."""
        return f"""Node: ID {self.id}, Name: {self.name}, Latitude: {self.lat}, Longitude: {self.lng}"""

class Truck:
    """Represent a delivery truck."""

    def __init__(self, id, name, home, refrigerated: bool, capacity, fuel):
        """Initialize a truck with its home, storage, and fuel details."""
        self.id = id
        self.name = name
        self.home = home
        self.refrigerated = refrigerated
        self.capacity = capacity
        self.fuel = fuel

    def __str__(self):
        """Return a readable description of the truck."""
        return f"""Truck: ID {self.id}, Name: {self.name}, Home: {self.home}, Refrigerated: {self.refrigerated},
            Capacity: {self.capacity}, Fuel: {self.fuel}"""
    
class Hub:
    """Represent a delivery hub associated with a point of interest."""

    def __init__(self, poiId, normal, cold):
        """Initialize a hub with normal and refrigerated capacities."""
        self.poiId = poiId
        self.normal = normal
        self.cold = cold

    def __str__(self):
        """Return a readable description of the hub."""
        return f"""Hub: POI ID {self.poiId}, Normal Capacity: {self.normal}, Cold Capacity: {self.cold}"""

