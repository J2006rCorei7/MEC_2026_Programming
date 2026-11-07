"""
Each request gets a score that determines its priority in the queue.
Requests get processed based on their position in the queue.
"""
from Dataparse import parse_json_file

(g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs) = parse_json_file("toronto-downtown.json")

