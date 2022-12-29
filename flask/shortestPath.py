# IMPORTS 
from pymongo import MongoClient 
from queue import PriorityQueue
import heapq

def get_adj_list(client, collection_name):
  #  Connect to a specific database and get adjacency list
  return (
  {
    'A': [(4, 'B'), (2, 'C')],
    'B': [(4,'A'), (1, 'C'), (3, 'D')],
    'C': [(2, 'A'), (1, 'B'), (1, 'D')],
    'D': [(3, 'B'), (1, 'C')]
  }
)

def get_source_and_dest_nodes(client, collection_name):
  #  Connect to a specific database and get source and destination nodes
  return ('A', 'B')


def compare_tuples(tuple1, tuple2):
  # Define a custom comparison function that compares the first element of each tuple
  if tuple1[1] > tuple2[1]:
    return 1
  elif tuple1[1] <= tuple2[1]:
    return -1
  else:
    return 0




def dijkstra(graph, source):
    # initialize an array to keep track of the distances from the source to each node
    distances = {}

    # initialize the distances to the source node
    distances[source] = 0

    # initialize an array to keep track of the visited nodes
    visited = {}

    # initialize an array to keep track of the previous node in the shortest path
    previous = {}

    minheap = [(0, source)]
    heapq.heapify(minheap)

    # loop until the heap is empty
    while minheap:
        # print(minheap, end=" ")
        # get the node with the minimum distance from the heap
        node = heapq.heappop(minheap)
        # print (node, end=" ")
        # mark the node as visited
        visited[node] = True
        
        # loop through the neighbors of the node
        for neighbor in graph[node[1]]:
            # extract the neighbor node and the edge weight
            weight, neighbor_node = neighbor
            # print (weight, end=" ")
            # print (neighbor_node, end=" ")
            if neighbor_node in visited:
                continue
            
            # calculate the distance to the neighbor
            distance = distances[node[1]] + weight
            
            # if the neighbor is not in the distances dictionary or the distance to the neighbor is shorter than the current distance, update it
            if neighbor_node not in distances or distance < distances[neighbor_node]:
                distances[neighbor_node] = distance
                previous[neighbor_node] = node[1]
                heapq.heappush(minheap, (distance, neighbor_node))
        # print(distances)

    # return the distances and previous nodes dictionaries
    return distances, previous

# Modify Dijkstra's algorithm to stop when a particular node is reached
def dijkstra_modified(graph, source, destination):
    # initialize an array to keep track of the distances from the source to each node
    distances = {}

    # initialize the distances to the source node
    distances[source] = 0

    # initialize an array to keep track of the visited nodes
    visited = {}

    # initialize an array to keep track of the previous node in the shortest path
    previous = {}

    minheap = [(0, source)]
    heapq.heapify(minheap)

    # loop until the heap is empty
    while minheap:
        # print(minheap, end=" ")
        # get the node with the minimum distance from the heap
        node = heapq.heappop(minheap)
        # print (node, end=" ")
        # mark the node as visited
        visited[node] = True
        
        # loop through the neighbors of the node
        for neighbor in graph[node[1]]:
            # extract the neighbor node and the edge weight
            weight, neighbor_node = neighbor
            # print (weight, end=" ")
            # print (neighbor_node, end=" ")
            if neighbor_node in visited:
                continue
            
            # calculate the distance to the neighbor
            distance = distances[node[1]] + weight
            
            # if the neighbor is not in the distances dictionary or the distance to the neighbor is shorter than the current distance, update it
            if neighbor_node not in distances or distance < distances[neighbor_node]:
                distances[neighbor_node] = distance
                # previous.append(node[1])
                previous[neighbor_node] = node[1]
                heapq.heappush(minheap, (distance, neighbor_node))
        # print(distances)

        # if the destination node is reached, stop the algorithm
        if node[1] in destination:
            return node[1], previous

    # return the distances and previous nodes dictionaries
    return distances, previous

    # # loop until the heap is empty
    # while heap:
    #     print(heap, end=" ")
    #     # get the node with the minimum distance from the heap
    #     node = heap.pop(heap.index(min(heap)))
    #     print (node)
    #     # mark the node as visited
    #     visited[node] = True

    #     # loop through the neighbors of the node
    #     for neighbor in graph[node]:
    #         # extract the neighbor node and the edge weight
    #         neighbor_node, weight = neighbor

    #         if neighbor_node in visited:
    #             continue

    #         # calculate the distance to the neighbor
    #         distance = distances[node] + weight

    #         # if the neighbor is not in the distances dictionary or the distance to the neighbor is shorter than the current distance, update it
    #         if neighbor_node not in distances or distance < distances[neighbor_node]:
    #             distances[neighbor_node] = distance
    #             previous[neighbor_node] = node
    #             # previous.append(node)
    #             heap.append(neighbor_node)

    # # return the distances and previous nodes dictionaries
    # return distances, previous

# define an adjacency list for a graph with 4 nodes
adj_list = {
    'A': [(4, 'B'), (2, 'C')],
    'B': [(4,'A'), (1, 'C'), (3, 'D')],
    'C': [(2, 'A'), (1, 'B'), (1, 'D')],
    'D': [(3, 'B'), (1, 'C')]
}

# adj_list = {
#     'A': [(2, 'B'), (2, 'C')],
#     'B': [(2,'A'), (2, 'C'), (2, 'D')],
#     'C': [(2, 'A'), (2, 'B'), (2, 'D')],
#     'D': [(2, 'B'), (2, 'C')]
# }


# find the shortest path from node 'A' to all other nodes
distances, previous = dijkstra(adj_list, 'A')

# print the distances from the source to each node
# print(distances)

# print the previous nodes in the shortest path from the source to each node
# print(previous)

def convert_previousdict_to_path(previous, source, dest):
    # initialize the path with the destination node
    path = [dest]

    # loop until the source node is reached
    while path[-1] != source:
        # get the previous node in the path
        prev_node = previous[path[-1]]

        # add the previous node to the path
        path.append(prev_node)

    # reverse the path
    path.reverse()

    # return the path
    return path

# print the shortest path from node 'A' to node 'D' 
# print(convert_previousdict_to_path(previous, 'A', 'D'))

# ======================================================================
# COMBINE ALL STEPS INTO A SINGLE SHORTEST PATH FUNCTION
# Step 1: Get the adjacency list from a specific collection from mongodb database 
# Step 2: Get the source and destination nodes from the adjacency list
# Step 3: Find the shortest path from source to destination using Dijkstra's algorithm
# Step 4: Convert the previous dictionary to a path
# Step 5: Return the path 
# ======================================================================

def calculate_shortest_path(client, collection_name, source, dest):
    # Get the adjacency list
    adj_list = get_adj_list(client, collection_name)

    # Get the source and destination nodes
    source, dest = get_source_and_dest_nodes(client, collection_name)

    # Find the shortest path from source to destination using Dijkstra's algorithm
    distances, previous = dijkstra(adj_list, source)

    # Convert the previous dictionary to a path
    path = convert_previousdict_to_path(previous, source, dest)

    # Return the path
    return path

# ======================================================================

print(calculate_shortest_path("mock client", 'adj_list', 'A', 'B'))
