"""
Each request gets a score that determines its priority in the queue.
Requests get processed based on their position in the queue.
"""
from Dataparse import parse_json_file
from routing import a_star
from datetime import datetime

# PRIORITY FACTORS
PEOPLE_BASE = 1.01
PEOPLE_FACTOR = 0.5

HOT_FOOD_FACTOR = 0.8
COLD_FOOD_FACTOR = 1.2

DEADLINE_BASE = 1.01
DEADLINE_FACTOR = -0.5

URGENCY_FACTOR = 1

(g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs) = parse_json_file()

nodes_by_id = {node.id: node for node in nodes}
pois_by_name = {poi.name: poi for poi in pois}
pois_by_poiID = {poi.id: poi for poi in pois}

def calculate_score(request):
    def time_diff(time1, time2):
        hour1 = time1.hour
        minute1 = time1.minute
        second1 = time1.second

        hour2 = time2.hour
        minute2 = time2.minute
        second2 = time2.second

        return (hour1 - hour2)*60*60 + (minute1 - minute2)*60 + (second1 - second2)

    dest_name, dest_type, num_people, address, hot_food_needed, hot_food_available, cold_food_needed, cold_food_available, delivery_deadline, urgency_level = request.get_data()

    priority_score = (PEOPLE_FACTOR*(PEOPLE_BASE**num_people) + (hot_food_needed - hot_food_available)*HOT_FOOD_FACTOR
                      + (cold_food_needed - cold_food_available)*COLD_FOOD_FACTOR + DEADLINE_FACTOR*(DEADLINE_BASE**time_diff(delivery_deadline, datetime.now()))
                      + urgency_level*URGENCY_FACTOR)

    return priority_score

def closest_hub(name):
    global path

    def hub_to_node_id(hub):
        return pois_by_poiID[hub.poiId].node

    closest_distance = float('inf')
    closest_path = None
    closest_edges = None
    closest_hub = None
    for hub in hubs:
        path, edges, cost = a_star(pois_by_name[name].id, hub_to_node_id(hub))
        if cost < closest_distance:
            closest_path = path
            closest_edges = edges
            closest_distance = cost
            closest_hub = hub

    if path:
        return closest_path, closest_edges, closest_distance, closest_hub
    else:
        return None

class Request:
    def __init__(self, dest_name, dest_type, num_people, address,
                 hot_food_needed, hot_food_available, cold_food_needed, cold_food_available,
                 delivery_deadline, urgency_level):
        self.dest_name = dest_name
        self.dest_type = dest_type
        self.num_people = num_people
        self.address = address
        self.hot_food_needed = hot_food_needed
        self.hot_food_available = hot_food_available
        self.cold_food_needed = cold_food_needed
        self.cold_food_available = cold_food_available
        self.delivery_deadline = delivery_deadline
        self.urgency_level = urgency_level

    def get_data(self):
        return (self.dest_name, self.dest_type, self.num_people, self.address,
                self.hot_food_needed, self.hot_food_available,
                self.cold_food_needed, self.cold_food_available,
                self.delivery_deadline, self.urgency_level)

if __name__ == '__main__':
    path, edges_used, total_km, hub = closest_hub("Spadina Ave & Front St")
    if path is None:
        print("No path found")
    else:
        print(f"Hub: {nodes_by_id[pois_by_poiID[hub.poiId].node].name}")

        print("Nodes:")
        for node in path:
           print(f"Node {node.id}: {node.name}")

        print("Edges:")
        for edge in edges_used:
           print(f"Edge {edge.id}: {edge.street}, {edge.km} km "
                 f"({edge.node1} <-> {edge.node2})")

        print(f"Total distance: {total_km:.2f} km")