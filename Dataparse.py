# Defined variables 
zoom = 0
center = (0,0)
name = ""
id = ""


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

class truck:
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
    

