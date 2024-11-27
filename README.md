main - Prompts user for input and handles command
perodic_updates - Thread ran to send routing updates by the user given interval. Additionally, it checks to see if any servers can be dropped if they do not update 3 times consecutively.
read_topology - Reads a given .txt file assuming correct format and sets the known variables
initialize_routing_table - Set all costs and next hops to 0 for each server given in the topology file. Then, any neighbors are given costs since they are known.
send_routing_updates - Distance vector update format with information about the server's routing table is given to all neighbors
receive_routing_updates - After send_routing_updates is sent, this receives that message and calls function update_routing in order to update the routing table using the Bellman Ford equation
update_routing - Given a routing_update from receive_routing_updates, it evaluates if there is a smaller cost given the routing update to any of the destinations at the current routing table.

Routing table data structure is a python dictionary. It is in this format when processed:

destination_id : [next_hop_id, cost]

The data structure of the update message is a python dictionary. It is in this format when processed:

routing_update = {
        "Number of update fields" : len(routing_table),
        "Server port" : port,
        "Server IP" : server_ip,
        "Servers" : [] # Array of dictionaries
}

Key "Servers" contains an array of dictionaries. Each dictionary in "Servers" relate to the routing data of each server.

It is in this format:

 n_server = {
            "Server IP address" : servers.get(destination_id)[0],
            "Server port" : servers.get(destination_id)[1],
            "Server ID" : destination_id,
            "Cost" : routing_table[destination_id][1]
  }

