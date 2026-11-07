import heapq
import math

from Dataparse import parse_json_file

(g_id, g_name, g_zoom, g_center, nodes, pois, edges, trucks, hubs) = parse_json_file()

# Create a list of node objects, addressable by node ID
nodes_by_id = {}
for node in nodes:
    nodes_by_id[node.id] = node

# Neighbours is a list of a list of neighbours
neighbours = {}

# Create an index for each node
for node in nodes:
    neighbours[node.id] = []

# Go through the entire list of edges,
# and for each edge, set node1 and node2 as neighbours
# and append to list of neighbours
for edge in edges:
    # edge.node1 returns the Node ID of the first node in the edge
    # edge.node2 returns the Node ID of the second node in the edge
    neighbours[edge.node1].append((edge.node2, edge.km, edge))
    neighbours[edge.node2].append((edge.node1, edge.km, edge))  # roads go both ways

def heuristic(node_a, node_b):
    """Straight-line distance in km between two Node objects (haversine)."""
    earth_radius_km = 6371

    lat_a = math.radians(node_a.lat)
    lat_b = math.radians(node_b.lat)
    lat_difference = lat_b - lat_a
    lng_difference = math.radians(node_b.lng - node_a.lng)

    haversine_value = (math.sin(lat_difference / 2) ** 2
                       + math.cos(lat_a) * math.cos(lat_b)
                       * math.sin(lng_difference / 2) ** 2)

    return 2 * earth_radius_km * math.asin(math.sqrt(haversine_value))


def a_star(start, goal):
    """A* search between two node ids.

    Returns (path, edges_used, total_km):
      path       - list of node ids from start to goal
      edges_used - list of Edge objects, in order, one for each hop along the path
      total_km   - total distance of the route
    Returns (None, None, None) if there is no route.
    """
    # Check if start and goal nodes are valid nodes
    if start not in nodes_by_id or goal not in nodes_by_id:
        raise ValueError("start and goal must both be node ids in the dataset")

    # Goal node object
    goal_node = nodes_by_id[goal]

    # The score of the start is typically f = g + h, since this is the start, g = 0, so f = h
    start_score = heuristic(nodes_by_id[start], goal_node)

    # The open list is the list of nodes we've discovered but not explored yet
    # Each entry is (total_score, cost_so_far, node_id).
    # So far, we've discovered the start node
    open_list = [(start_score, 0, start)]

    # came_from[node_id] = (the node we stepped from, the Edge we used to get here)
    # The nodes we've visited (in reverse order of exploration)
    came_from = {}

    # The cheapest km found so far to reach each node from the start
    # Formatted as {Node ID: Cost (in km)   }
    cheapest_cost_to_reach = {start: 0}

    # While the length of open_list > 0
    while open_list:
        # Since tuples (which are the items in open_list) are ordered left to right,
        # heapq.heappop pops the element with the lowest value in the first index of the tuple (leftmost)
        # Pick the most promising node in the open list
        total_score, cost_so_far, current_id = heapq.heappop(open_list)

        # If we reached the goal, walk backward through came_from to rebuild the route
        if current_id == goal:
            path = [current_id]
            edges_used = []
            while current_id in came_from:
                previous_id, edge_used = came_from[current_id]
                path.append(previous_id)
                edges_used.append(edge_used)
                current_id = previous_id
            path.reverse()
            edges_used.reverse()
            path = [nodes_by_id[node_id] for node_id in path]
            return path, edges_used, cost_so_far

        # Skip outdated entries: we already found a cheaper way to this node
        if cost_so_far > cheapest_cost_to_reach[current_id]:
            continue

        # Look at every road leaving this node
        # Grab all the data from neighbours
        for neighbour_id, edge_km, edge in neighbours[current_id]:
            new_cost = cost_so_far + edge_km

            # If a cost for a neighbour exists, save it in known_cost
            # If a cost for a neighbour does not exist yet, give it infinite cost
            known_cost = cheapest_cost_to_reach.get(neighbour_id, float("inf"))
            if new_cost < known_cost:
                # Found a cheaper way to this neighbour: remember it and the edge we used
                cheapest_cost_to_reach[neighbour_id] = new_cost
                came_from[neighbour_id] = (current_id, edge)

                guess_to_goal = heuristic(nodes_by_id[neighbour_id], goal_node)
                new_total_score = new_cost + guess_to_goal
                # Pushes a new tuple with the new total score, the new cost, and the ID of the neighbour node
                # to the open_list
                heapq.heappush(open_list, (new_total_score, new_cost, neighbour_id))

    return None, None, None  # open_list ran out, so the goal can't be reached

if __name__ == "__main__":
    path, edges_used, total_km = a_star(4, 28)   # Yonge & Front -> Yonge & Dundas

    if path is None:
        print("No path found")
    else:
        print("Nodes:")
        for node in path:
           print(f"Node {node.id}: {node.name}")

        print("Edges:")
        for edge in edges_used:
           print(f"Edge {edge.id}: {edge.street}, {edge.km} km "
                 f"({edge.node1} <-> {edge.node2})")

        print(f"\nTotal distance: {total_km:.2f} km")