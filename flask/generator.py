# IMPORTS
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId





# FUNCTION(S)
def generate_starting_instructions(client, database, collection_name, efficient_dp, inefficient_dp):

    db = client[database]
    col = db[collection_name]

    inefficient_instruction = col.find_one({"_id": ObjectId(inefficient_dp)}).get("name")
    efficient_instruction = col.find_one({"_id": ObjectId(efficient_dp)}).get("name")
    return "With your back to " + inefficient_instruction + ", go towards " + efficient_instruction 

    # first_dp_data = col.find_one({"_id": ObjectId(first_dp)})
    # print(first_dp_data)
    # for key, value in first_dp_data.items():
    #     if key == "edges":
    #         for edge in value:
    #             if edge["_id"] == start_dest:
    #                 direction = edge["direction"]
    #                 if direction == "north":
    #                     return "Go straight"
    #                 elif direction == "east":
    #                     return "Turn left"
    #                 elif direction == "west":
    #                     return "Turn right"
    #                 elif direction == "south":
    #                     return "Turn around"




def generate_instructions(client, database, collection_name, path): 

    instructions = []

    db = client[database]
    col = db[collection_name]

    for i in range(len(path)):
        if i == 0:
            # generate_starting_instructions(client, database, collection_name, path[i])
            continue
        if i == len(path) - 1:
            break
        else:
            current_node = path[i]
            previous_node = path[i-1]
            next_node = path[i+1]
            
            # I don't need to fetch previous and next node data, I just need to fetch the current node data
            # and then I can get the in and out edges from there


            current_node_data = col.find_one({"_id": ObjectId(current_node)})
            in_direction = ''
            out_direction = ''
            for key, value in current_node_data.items():
                if key == "edges":
                    for edge in value:
                        if edge["_id"] == previous_node:
                            in_direction = edge["direction"]
                        if edge["_id"] == next_node:
                            out_direction = edge["direction"]

            print(current_node_data)    
            print(in_direction)
            print(out_direction) 

            
            if in_direction == out_direction:
                instructions.append("Go straight")
            elif in_direction == "north" and out_direction == "east":
                instructions.append("Turn left")
            elif in_direction == "north" and out_direction == "west":
                instructions.append("Turn right")
            elif in_direction == "south" and out_direction == "east":
                instructions.append("Turn right")
            elif in_direction == "south" and out_direction == "west":
                instructions.append("Turn left")
            elif in_direction == "east" and out_direction == "north":
                instructions.append("Turn right")
            elif in_direction == "east" and out_direction == "south":
                instructions.append("Turn left")
            elif in_direction == "west" and out_direction == "north":
                instructions.append("Turn left")
            elif in_direction == "west" and out_direction == "south":
                instructions.append("Turn right")
            else:
                return "error"    

    return instructions                   


def generate_dest_instructions(client, database, collection_name):
    print("Hello")



def generate_gateway_instructions(in_edge, out_edge):
    print("Hello")

def generate_floor_change_instruction(source_floor, destination_floor):
    return "Take the elevator to floor " + str(destination_floor) + " from floor " + str(source_floor)