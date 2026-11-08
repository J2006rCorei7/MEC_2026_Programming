"""
Each request gets a score that determines its priority in the queue.
Requests get processed based on their position in the queue.
"""
import heapq
from itertools import count
from Dataparse import parse_json_file
from routing import a_star, closest_hub
from databaseInfo import *
from datetime import datetime

# PRIORITY FACTORS
PEOPLE_BASE = 1.01
PEOPLE_FACTOR = 0.5

HOT_FOOD_FACTOR = 0.8
COLD_FOOD_FACTOR = 1.2

DEADLINE_BASE = 1.01
DEADLINE_FACTOR = -0.5

URGENCY_FACTOR = 1

DISTANCE_FACTOR = 0.5

HOSPITAL_FACTOR = 1.7
SHELTER_FACTOR = 1.5
COMMUNITY_FACTOR = 1.1

(g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs) = parse_json_file()

nodes_by_id = {node.id: node for node in nodes}
pois_by_name = {poi.name: poi for poi in pois}
pois_by_poiID = {poi.id: poi for poi in pois}

request_queue = []

tie_breaker = count()
def handle_requests():
    requests = get_all_requests()

    # Populating Priority Queue should be somewhere else
    for r in requests:
        request = get_request_by_id(r['id'])
        if request is not None:
            # request_queue.append(request['id'], -calculate_priority_score(request))
            heapq.heappush(request_queue, (-calculate_priority_score(request), next(tie_breaker), request['id']))

def handle_request(request):
    pass

def calculate_priority_score(request):
    score = 0
    score += PEOPLE_FACTOR * (PEOPLE_BASE ** request['num_people'])
    score += HOT_FOOD_FACTOR * (request['hot_food_needed'] - request['hot_food_available'])
    score += COLD_FOOD_FACTOR * (request['cold_food_needed'] - request['cold_food_available'])
    score += URGENCY_FACTOR * (request['urgency_level'])
    score += DISTANCE_FACTOR * (closest_hub(request['dest_name'])[2])

    match request['dest_type']:
        case 'hospital':
            score *= HOSPITAL_FACTOR
        case 'shelter':
            score *= SHELTER_FACTOR
        case 'community':
            score *= COMMUNITY_FACTOR

    return round(score, 2)

def recalculatePriorities():
    requests = get_all_requests()

    highest = float('-inf')
    highest_id = None

    for r in requests:
        score = calculate_priority_score(r)

        if score > highest:
            highest = score
            highest_id = r['id']

    if highest_id is not None:
        update_request(highest_id, {"status": 2})

    return highest_id


# Test Case
if __name__ == '__main__':
    request = [{'id': 1, 'dest_name': 'Moss Park delivery site (scenario)', 'dest_type': 'shelter', 'num_people': 150, 'address': '123 Queen Street West, Toronto, ON', 'hot_food_needed': 120, 'hot_food_available': 30, 'cold_food_needed': 80, 'cold_food_available': 50, 'delivery_deadline': 3, 'urgency_level': 4, 'person_id': None}]
    print(f"Priority Score: {calculate_priority_score(request[0])}")