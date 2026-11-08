"""
Each request gets a score that determines its priority in the queue.
Requests get processed based on their position in the queue.
Resource matching is greedy: each request, in priority order, takes the best
hub + truck pair that is available at that moment.
"""
import heapq
from itertools import count
from Dataparse import parse_json_file
from routing import a_star, closest_hub
from databaseInfo import *
from datetime import datetime
import crisis_state
from crisis_state import CrisisState
from main import nodes, pois, trucks, hubs

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

KM_PER_LITRE = 8  # same assumption Truck.drive() uses

nodes_by_id = {node.id: node for node in nodes}
pois_by_name = {poi.name: poi for poi in pois}
pois_by_poiID = {poi.id: poi for poi in pois}

request_queue = []

# RESOURCE TRACKING
# Trucks currently reserved for a request (truck.id). Prevents double-booking.
trucks_in_use = set()
# request_id -> assignment record (what was reserved for it)
assignments = {}

tie_breaker = count()


def handle_requests():
    requests = get_all_requests()

    # Populating Priority Queue should be somewhere else
    for r in requests:
        request = get_request_by_id(r['id'])
        if request is not None:
            crisis_state.register(request['id'])
            heapq.heappush(request_queue, (-calculate_priority_score(request), next(tie_breaker), request['id']))
            crisis_state.transition(request['id'], CrisisState.PRIORITIZED,
                                    f"Scored {calculate_priority_score(request)} and added to the priority queue")


def handle_next_request():
    """Pop the highest-priority request and try to match it with a hub and a truck.

    Returns the assignment record on success, or None if nothing could be assigned
    (the state machine records why).
    """
    if not request_queue:
        return None

    request_id = heapq.heappop(request_queue)[2]
    request = get_request_by_id(request_id)
    if request is None:
        return None

    # How much food is still missing at the destination
    hot_short = max(0, request['hot_food_needed'] - request['hot_food_available'])
    cold_short = max(0, request['cold_food_needed'] - request['cold_food_available'])

    if hot_short == 0 and cold_short == 0:
        crisis_state.transition(request_id, CrisisState.RESOLVED, "No food shortage, nothing to deliver")
        return None

    match, failure = find_best_match(request, hot_short, cold_short)

    if match is None:
        if failure == "no_route":
            crisis_state.transition(request_id, CrisisState.FAILED,
                                    "No usable route exists between any hub and the destination")
        else:
            crisis_state.transition(request_id, CrisisState.DELAYED,
                                    "No truck/hub combination with enough stock, fuel or "
                                    "refrigeration is free right now")
        return None

    # Reserve the resources so the next request cannot take them
    match["hub"].cold -= match["cold_load"]
    match["hub"].normal -= match["hot_load"]
    trucks_in_use.add(match["truck"].id)
    assignments[request_id] = match

    crisis_state.transition(
        request_id, CrisisState.RESOURCE_ASSIGNED,
        f"Truck {match['truck'].name} loads {match['hot_load']} hot / {match['cold_load']} cold "
        f"at hub POI {match['hub'].poiId}, route {match['total_km']:.2f} km")
    return match


def find_best_match(request, hot_short, cold_short):
    """Greedy choice: the hub/truck pair that delivers the most food, then the shortest trip.

    Rules:
      - A truck can only carry as much as its capacity.
      - Only refrigerated trucks can carry cold food.
      - A hub can only give what it has in stock.
      - The truck needs enough fuel for truck -> hub -> destination.
      - Both legs must have a route (closed roads are skipped inside a_star).

    Returns (match_dict, None) or (None, "no_route" | "no_resources").
    """
    dest_node = pois_by_name[request['dest_name']].node
    best = None
    best_key = None
    any_route = False

    for hub in hubs:
        if hub.normal <= 0 and hub.cold <= 0:
            continue

        hub_node = pois_by_poiID[hub.poiId].node
        to_dest, _, km_to_dest = a_star(hub_node, dest_node)
        if to_dest is None:
            continue

        for truck in trucks:
            if truck.id in trucks_in_use:
                continue

            start_node = truck_start_node(truck)
            if start_node is None:
                continue

            to_hub, _, km_to_hub = a_star(start_node, hub_node)
            if to_hub is None:
                continue
            any_route = True

            # Fill cold first (more perishable and weighted higher), then hot
            cold_load = min(cold_short, hub.cold, truck.capacity) if truck.refrigerated else 0
            hot_load = min(hot_short, hub.normal, truck.capacity - cold_load)
            if cold_load + hot_load == 0:
                continue

            total_km = km_to_hub + km_to_dest
            if truck.fuel < total_km / KM_PER_LITRE:
                continue

            key = (-(cold_load + hot_load), total_km)  # most food first, then shortest trip
            if best_key is None or key < best_key:
                best_key = key
                best = {
                    "request_id": request['id'],
                    "truck": truck,
                    "hub": hub,
                    "hot_load": hot_load,
                    "cold_load": cold_load,
                    "total_km": total_km,
                    "path_to_hub": to_hub,
                    "path_to_dest": to_dest,
                }

    if best is not None:
        return best, None
    return None, ("no_resources" if any_route else "no_route")


def truck_start_node(truck):
    """Node a truck starts from. ASSUMPTION: truck.home is a POI id; falls back to a node id."""
    if truck.home in pois_by_poiID:
        return pois_by_poiID[truck.home].node
    if truck.home in nodes_by_id:
        return truck.home
    return None


def start_delivery(request_id):
    """Truck leaves the hub."""
    crisis_state.transition(request_id, CrisisState.IN_PROGRESS, "Truck departed")


def complete_delivery(request_id):
    """Truck arrived: update the database, free the truck, close the request."""
    a = assignments.pop(request_id)
    crisis_state.transition(request_id, CrisisState.DELIVERED,
                            f"Delivered {a['hot_load']} hot / {a['cold_load']} cold")
    request = get_request_by_id(request_id)
    update_request(request_id, {
        "hot_food_available": request['hot_food_available'] + a['hot_load'],
        "cold_food_available": request['cold_food_available'] + a['cold_load'],
    })
    trucks_in_use.discard(a['truck'].id)
    crisis_state.transition(request_id, CrisisState.RESOLVED, "Request resolved after delivery")


def release_resources(request_id, reason, return_stock=True):
    """Undo a reservation (e.g. vehicle breakdown). Stock goes back to the hub unless
    return_stock is False. Afterwards call requeue_delayed() to try again."""
    a = assignments.pop(request_id, None)
    if a is None:
        return
    if return_stock:
        a["hub"].cold += a["cold_load"]
        a["hub"].normal += a["hot_load"]
    trucks_in_use.discard(a["truck"].id)
    crisis_state.transition(request_id, CrisisState.DELAYED, reason)


def requeue_delayed(request_id):
    """Put a DELAYED request back in the priority queue."""
    request = get_request_by_id(request_id)
    heapq.heappush(request_queue, (-calculate_priority_score(request), next(tie_breaker), request_id))
    crisis_state.transition(request_id, CrisisState.PRIORITIZED, "Re-queued after delay")


def calculate_priority_score(request):
    score = 0
    score += PEOPLE_FACTOR * (PEOPLE_BASE ** request['num_people'])
    score += HOT_FOOD_FACTOR * (request['hot_food_needed'] - request['hot_food_available'])
    score += COLD_FOOD_FACTOR * (request['cold_food_needed'] - request['cold_food_available'])
    score += DISTANCE_FACTOR * (closest_hub(request['dest_name'])[2])

    match request['urgency_level']:
        case 'unknown':
            score += URGENCY_FACTOR * 0
        case 'low':
            score += URGENCY_FACTOR * 1
        case 'medium':
            score += URGENCY_FACTOR * 2
        case 'high':
            score += URGENCY_FACTOR * 3
        case 'critical':
            score += URGENCY_FACTOR * 4

    match request['dest_type']:
        case 'hospital':
            score *= HOSPITAL_FACTOR
        case 'shelter':
            score *= SHELTER_FACTOR
        case 'community':
            score *= COMMUNITY_FACTOR

    return round(score, 2)


# Test Case
if __name__ == '__main__':
    handle_requests()
    while request_queue:
        result = handle_next_request()

    for r in get_all_requests():
        print(f"\nRequest {r['id']} ({r['dest_name']}):")
        for h in crisis_state.get_history(r['id']):
            print(f"  {h['time']}  {h['state'].value:<18} {h['reason']}")