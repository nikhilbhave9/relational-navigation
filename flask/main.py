# IMPORTS
# Example: from my_module import my_function
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

from generator import generate_starting_instructions
from generator import generate_instructions
from generator import generate_floor_change_instruction
from generator import generate_dest_instructions

from shortestPath import calculate_shortest_path
from shortestPath import dijkstra_modified
from shortestPath import dijkstra


# --------------------------------------------------------------------------------------------
# DELETE LATER

 # Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = "mongodb+srv://admin:adminpassword@serverlessinstance0.xphpq.mongodb.net/?retryWrites=true&w=majority"

# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(CONNECTION_STRING)
db = client['main_db']

# --------------------------------------------------------------------------------------------
# HELPER OPERATIONS TO INSERT, MODIFY AND DELETE DATA FROM DATABASE
# --------------------------------------------------------------------------------------------
# INSERT OPERATIONS

def create_adj_list(client, database, collection):
  db = client[database]
  col = db[collection]
  adj_list = {"type": "adjacency_list"}
  col.insert_one(adj_list)

def insert_node(client, database, collection, node):
  db = client[database]
  col = db[collection]
  obj = col.insert_one(node)
  id = obj.inserted_id
  new_node = {str(id): []}
  col.find_one_and_update(
    {"type": "adjacency_list"},
    {"$set": new_node}
   )

def reverse(direction):
  if direction == "north":
    return "south"
  elif direction == "south":
    return "north"
  elif direction == "east":
    return "west"
  elif direction == "west":
    return "east"
  else:
    return "error"

def insert_edge(client, database, collection, primary_node_number, secondary_node_number, distance, direction):

  # Fetch primary node from collection
  db = client[database]
  col = db[collection]

  # Create the edge from the primary node to the secondary node
  col.find_one_and_update(
    {"_id": ObjectId(primary_node_number)},
    {"$push": {"edges": {
      "_id": secondary_node_number,
      "distance": distance,
      "direction": direction,
      "destination": [],
    }}}
  )

  # Reverse the edge from the secondary node to the primary node
  col.find_one_and_update(
    {"_id": ObjectId(secondary_node_number)},
    {"$push": {"edges": {
      "_id": primary_node_number,
      "distance": distance,
      "direction": reverse(direction),
      "destination": []
    }}}
  )

  # Add edge to the adjacency list
  tuple1 = (distance, secondary_node_number)
  col.find_one_and_update(
    {"type": "adjacency_list"},
    {"$push": {primary_node_number: tuple1}}
  )


  # Add edge to the adjacency list
  tuple2 = (distance, primary_node_number)
  col.find_one_and_update(
    {"type": "adjacency_list"},
    {"$push": {secondary_node_number: tuple2}}
  )



def insert_dest(client, database, floor, primary_node_id, secondary_node_id, direction1, count1, direction2, count2):
  
  db = client[database]
  col = db[floor]

  # Create new object id for the destination node
  new_dest_id = ObjectId()


  # Search for primary node AND secondary node in the edges array in the same document and push the new destination node
  filter1 = {"_id": ObjectId(primary_node_id)}
  filter2 = {"edges": {"$elemMatch": {"_id": secondary_node_id}}}
  query = {"$and": [filter1, filter2]}
  update = {"$push": {"edges.$.destination": {
    "_id": new_dest_id,
    "id": secondary_node_id,
    "sub_direction": direction1,
    "count": count1
  }}}


  # filter1 = {"_id": ObjectId(primary_node_id)}
  # filter2 = {"edge": {"$elemMatch": {"_id": secondary_node_id}}}
  # query = {"$and": [filter1, filter2]}
  # update = {"$push": {"edge": {"destination": {
  #   "_id": new_dest_id,
  #   "id": secondary_node_id,
  #   "sub_direction": direction1,
  #   "count": count1
  # }}}}

  col.find_one_and_update(query, update)

  # filter3 = {"_id": ObjectId(secondary_node_id)}
  # filter4 = {"edge": {"$elemMatch": {"_id": primary_node_id}}}
  # query2 = {"$and": [filter3, filter4]}
  # update2 = {"$push": {"edge": {"destination": {
  #   "_id": new_dest_id,
  #   "id": primary_node_id,
  #   "sub_direction": direction2,
  #   "count": count2
  # }}}}

  filter3 = {"_id": ObjectId(secondary_node_id)}
  filter4 = {"edges": {"$elemMatch": {"_id": primary_node_id}}}
  query2 = {"$and": [filter3, filter4]}
  update2 = {"$push": {"edges.$.destination": {
    "_id": new_dest_id,
    "id": primary_node_id,
    "sub_direction": direction2,
    "count": count2
  }}}


  col.find_one_and_update(query2, update2)
  

# --------------------------------------------------------------------------------------------
# GET OPERATIONS

def get_id(client, database, collection, node_name):
  db = client[database]
  col = db[collection]
  node = col.find_one({"name" : node_name})
  return node["id"], node["floor"]

def get_floor_graph_collection_name(client, database, collection, floor):
  db = client[database]
  col = db[collection]
  ret = col.find_one({"floor": floor})
  return ret['collection_name']

def get_floor_graph(client, database, collection):
  db = client[database]
  col = db[collection]
  nodes = []
  floor_graph = {}
  nodes = col.find_one({"type": "adjacency_list"})

  # Nodes is a list of dictionaries
  # Each dictionary has a key and a value
  # We want the key and the value both and we want to add it to the floor_graph dictionary

  # Value is an array of arrays

  for key, value in nodes.items():
    array_to_be_pushed = []
    if key != "_id" and key != "type":
      for i in range(len(value)):
        array_to_be_pushed.append(tuple(value[i]))
      floor_graph[key] = array_to_be_pushed
  return floor_graph

def get_dp_nodes(client, database, source_id, source_floor):
  db = client[database]

  if source_floor == 0:
    collection = "ground_floor_main"
  else: 
    collection = "first_floor_AC02"
  col = db[collection]
  dp_nodes = []
  # Get the DP nodes
  # Filter by going to an edge, going to destination, and then getting the id of the destination
  for node in col.find({"edges": {"$elemMatch": {"destination": {"$elemMatch": {"_id": ObjectId(source_id)}}}}}):
    for edge in node["edges"]:
      for dest in edge["destination"]:
        if dest["_id"] == ObjectId(source_id):
          dp_nodes.append(dest["id"])
     
  return dp_nodes

def find_gateways(client, database, collection, source_floor):
  db = client[database]
  col = db[collection]
  gateway = []
  for node in col.find({"floor": source_floor}):
    gateway.append(node["id"])
  return gateway

def get_destination_floor_source(client, database, collection, gateway_node):
  db = client[database]
  col = db[collection]
  dest_floor_source = col.find_one({"_id": ObjectId(gateway_node)})
  return dest_floor_source["id"]

def get_destination_floor_source(client, db, gateway_map, gateway_node): 
  db = client[db]
  col = db[gateway_map]
  dest_floor_source = col.find_one({"id": gateway_node})
  return dest_floor_source["connects_to"]

# --------------------------------------------------------------------------------------------
# MAIN

def main(client, db, source, destination, additional_params):   

  instructions = []

  # Step 1: Get the source and destination dest node ids (nested within the DP nodes)
  source_id, source_floor = get_id(client, db, "location_map", source)
  destination_id, destination_floor = get_id(client, db, "location_map", destination)
  print(source_id, source_floor)
  print(destination_id, destination_floor)

  # Step 2: Get the floor graph(s) of the source and destination nodes
  floor_graph = []
  if (source_floor == destination_floor):
    floor_graph_name = get_floor_graph_collection_name(client, db, "location_map", source_floor)
    floor_graph.append(get_floor_graph(client, db, floor_graph_name))
  else:
    floor_graph_name1 = get_floor_graph_collection_name(client, db, "location_map", source_floor)
    floor_graph_name2 = get_floor_graph_collection_name(client, db, "location_map", destination_floor)
    floor_graph.append(get_floor_graph(client, db, floor_graph_name1))
    floor_graph.append(get_floor_graph(client, db, floor_graph_name2))
    # Step 3: Get the nodes on who's edges the source and destination nodes are present
    source_edges = get_dp_nodes(client, db, source_id, source_floor)
    destination_edges = get_dp_nodes(client, db, destination_id, destination_floor)
    print(source_edges)
    print(destination_edges)
    # Now we have the source and destination edges
    
    
    # FOR NOW ASSUMED EVERYTHING IS FOR MULTI FLOOR THEN HANDLE TWO CASES DEPENDING ON WHETHER IT IS MULTI FLOOR OR NOT

    # Step 4: Find gateway node using Dijkstra's algorithm by using both edges in source_edges 
    if (source_floor != destination_floor):
      gateway_array = find_gateways(client, db, "gateway_map", source_floor)
      print(floor_graph[0])
      print(source)
      print(gateway_array)
      print("----------This is what I'm sending to dijkstra----------")
      gateway_node, previous_gateway = dijkstra_modified(floor_graph[0], source_edges[0], gateway_array)
      print(gateway_node)

    
    # Step 5.1: Run shortest path twice, once from one source and once from the other source
    # Step 5.2: Find out which is more efficient and return that path

      # ================= SOURCE FLOOR =================
      efficient_path = []
      path1 = []
      path2 = []
      node1, prev1 = dijkstra_modified(floor_graph[0], source_edges[0], gateway_array)
      node2, prev2 = dijkstra_modified(floor_graph[0], source_edges[1], gateway_array)

      # from list of previuos nodes, construct the path
      # path1 = construct_path(path1, source_edges[0])
      # path2 = construct_path(path2, source_edges[1])


      # Use source_edges[0] and path1 to get the path from source to gateway
      cur = gateway_node
      for i in range(len(prev1)):
        if (cur == source_edges[0]):
          break
        print(cur)
        path1.append(cur)
        cur = prev1[cur]
      path1.append(source_edges[0])
      path1.reverse()

      # Use source_edges[1] and path2 to get the path from source to gateway
      cur = gateway_node
      for i in range(len(prev2)):
        if (cur == source_edges[1]):
          break
        print(cur)
        path2.append(cur)
        cur = prev2[cur]
      path2.append(source_edges[1])
      path2.reverse()

      inefficient_instruction = ""
      efficient_instruction = ""
      if (len(path1) > len(path2)):
        efficient_path = path1
        efficient_instruction = source_edges[1]
        inefficient_instruction = source_edges[0]

      else:
        efficient_path = path2
        efficient_instruction = source_edges[0]
        inefficient_instruction = source_edges[1]
      
      print(efficient_path)

      print("----------------------This is what I'm sending to generate instructions----------------------")

      # Starting Instruction 
      # Go from starting node to first node in efficient path
      instructions.append(generate_starting_instructions(client, "main_db", floor_graph_name1, efficient_instruction, inefficient_instruction))

      # Middle Instructions
      temp_instructions = generate_instructions(client, "main_db", floor_graph_name1, efficient_path)
      for instruction in temp_instructions:
        instructions.append(instruction)

      # Ending Instruction
      # Append instruction to change floor
      instructions.append(generate_floor_change_instruction(source_floor, destination_floor))
      
      
     

      print(instructions)

      # # ================= DESTINATION FLOOR =================
      # print("----------------------Destination Floor----------------------")
      # path1 = []
      # path2 = []
      # efficient_path = []
      # print(gateway_node)
      # destination_floor_source = get_destination_floor_source(client, db, "gateway_map", gateway_node)
      # print(destination_floor_source)
      # node3, previous_gateway1 = dijkstra_modified(floor_graph[1], destination_floor_source, destination_edges[0])
      # node4, previous_gateway2 = dijkstra_modified(floor_graph[1], destination_floor_source, destination_edges[1])
      
      # # =======
      # print("======")
      # print(source_edges[0])
      # print(destination_floor_source)


      # # Use source_edges[0] and path1 to get the path from source to gateway
      # cur = destination_edges[0]
      # print(cur)
      # for i in range(len(previous_gateway1)):
      #   if (cur == destination_floor_source):
      #     break
      #   path1.append(cur)
      #   cur = previous_gateway1[cur]
      # path1.append(destination_floor_source)
      # path1.reverse()
      # print(path1)
      # cur = destination_edges
      # for i in range(len(previous_gateway2)):
      #   if (cur == destination_floor_source):
      #     break
      #   print(cur)
      #   path2.append(cur)
      #   cur = previous_gateway2[cur]
      # path2.append(destination_floor_source)
      # path2.reverse()
      # print(path2)
     
      # inefficient_instruction = ""
      # efficient_instruction = ""
      # if (len(path1) > len(path2)):
      #   efficient_path = path1
      #   efficient_instruction = source_edges[1]
      #   inefficient_instruction = source_edges[0]

      # else:
      #   efficient_path = path2
      #   efficient_instruction = source_edges[0]
      #   inefficient_instruction = source_edges[1]

    return instructions

      # Starting Instruction 
      # Go from starting node to first node in efficient path

      # Middle Instructions
      # temp_instructions = generate_instructions(client, "main_db", floor_graph_name2, efficient_path)
      # for instruction in temp_instructions:
      #   instructions.append(instruction)

      # # Ending Instruction
      # # Locate the destination node and append instructions accordingly
      # instructions.append(generate_dest_instructions(source_floor, destination_floor))




  


  






  # Insert a node into the database ---------- DONE
  


  # Add a new node then a new edge ---------- DONE
  # node = {
  #   "name": "AC04 Library Cafe Exit",
  #   "number": 4,
  #   "edges": []
  # }

  # insert_node(db, "AC04 Ground Floor", node)

  # edge = {
  #   "_id": "63982b55fb45b2a1b29fecba",
  #   "distance": 20,
  #   "direction": "west"
  # }

  # insert_edge(client, 'test_nodes', 'AC04 Ground Floor', "63982b56fb45b2a1b29fecbb", edge)


  # Calculate the shortest path between two nodes 
  # calculate_shortest_path(client, "AC04 Ground Floor", 'A', 'B')

  # print(generate_instructions(node["edges"][0], node["edges"][1]))

  # create_adj_list(client, 'main_db', 'ground_floor_main')
  # create_adj_list(client, 'main_db', 'first_floor_AC02')

  # =========== CREATION PIPELINE ===========
  # REMEMBER TO ADD ELEVATOR NODES ALSO AND EDGES
  # node1 = {
  #   "category": "DP00",
  #   "name": "",
  #   "edges": [],
  #   "landmarks": {}    
  # }

  # node2 = {
  #   "category": "GW00",
  #   "name": "Media Lab Crossroad",
  #   "edges": [],
  #   "landmarks": {}    
  # }

  # node3 = {
  #   "category": "DP00",
  #   "name": "2nd MR Crossroad near lift main",
  #   "edges": [],
  #   "landmarks": {}    
  # }

  # insert_node(client, 'main_db', 'first_floor_AC02', node1)
  # insert_node(client, 'main_db', 'first_floor_AC02', node2)
  # insert_node(client, 'main_db', 'first_floor_AC02', node3)

  # insert_edge(client, 'main_db', 'first_floor_AC02', '639a488bf331279bc868f423', '639a488bf331279bc868f424', 15, 'south')
  # insert_edge(client, 'main_db', 'first_floor_AC02', '639a488bf331279bc868f424', '63997db1dc2cb10ee3299019', 2, 'south')
  # insert_edge(client, 'main_db', 'first_floor_AC02', '63997db1dc2cb10ee3299019', '639a44c2673728d6d4198168', 4, 'south')
  # insert_edge(client, 'main_db', 'first_floor_AC02', '639a488bf331279bc868f424', '639a44c2673728d6d419816a', 11, 'west')



  # insert_dest(client, 'main_db', 'first_floor_AC02', '639a44c2673728d6d4198168', '639a44c2673728d6d4198169', 'right', 1, 'left', 2)
  # insert_dest(client, 'main_db', 'first_floor_AC02', '639a44c2673728d6d4198168', '639a44c2673728d6d4198169', 'right', 2, 'left', 1)
  # insert_dest(client, 'main_db', 'first_floor_AC02', '639a44c2673728d6d419816a', '639a488bf331279bc868f422', 'right', 1, 'left', 2)
  # insert_dest(client, 'main_db', 'first_floor_AC02', '639a44c2673728d6d419816a', '639a488bf331279bc868f422', 'right', 2, 'left', 1)
  # insert_dest(client, 'main_db', 'first_floor_AC02', '639a488bf331279bc868f423', '639a488bf331279bc868f424', 'left', 1, 'right', 1)


# Run the main function when the program starts
if __name__ == "__main__":
  main(client, 'main_db', 'AC02 010', 'AC02 110', None)