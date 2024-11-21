import socket
import threading
import sys
import math

# Values initialized after reading the toplogy file
num_servers = -1
num_neighbors = -1
server_id = -1
server_ip = -1
port = -1

# Initialized after running the server command on startup
routing_update_interval = -1

# Data entered should be like this:
# server id # : [IP, port]
servers = {}

# Data entered should be like this:
# [server id, neighbor id, cost]
costs = []

# Data entered should be like this:
# destination id : [next_hop id, cost]
routing_table = {}

packets_received = 0


def main():
    global routing_update_interval

    while True:
        command = input("Enter command: ").strip().split()

        if not command:
            continue

        cmd = command[0].lower()

        if cmd == "server":
            if len(command) != 5:
                print("server ERROR, correct usage: server -t <topology-file-name> -i <routing-update-interval>")
                continue

            if command[1] != "-t" or command[3] != "-i":
                print("server ERROR, correct usage: server -t <topology-file-name> -i <routing-update-interval>")
                continue

            read_topology(command[2]) # command[2] should be the topology file name
            routing_update_interval = int(command[4])

            initialize_routing_table()

            print_vars() # for debugging
        elif cmd == "update":
            if len(command) != 4:
                print("update ERROR, correct usage: update <server-ID1> <server-ID2> <Link Cost>")
                continue
        elif cmd == "step":
            print("Sending routing update to neighbors")
        elif cmd == "packets":
            print("Displaying # of distance vector packets this server has received since last invocation")
        elif cmd == "display":
            print("Displaying the current routing table")
        elif cmd == "disable":
            if len(command) != 2:
                print("disable ERROR, correct usage: disable <server-ID>")
                continue
        elif cmd == "crash":
            print("Closing all connections")

def read_topology(fileDirectory):
    global num_servers, num_neighbors, server_id, port, server_ip
    f = open(fileDirectory)

    num_servers = int(f.readline())
    num_neighbors = int(f.readline())

    for i in range(num_servers):
        information = f.readline().split()
        # format of information should be: [server_id, ip, port_pair]

        if len(information) != 3:
            print("Topology file is written wrong, it should be in this format: server-id # and corresponding IP, port pair")

        servers[information[0]] = [information[1], information[2]]
    
    for i in range(num_neighbors):
        information = f.readline().split()
        # format of information should be: [server_id, neighbor_id, cost]

        if len(information) != 3:
            print("Topology file is written wrong, it should be in this format: server-id # and neighbor id and cost")
        
        costs.append([information[0], information[1], information[2]])

        server_id = information[0]
    
    port = servers[server_id][1]

    # get the server ip from the given server id
    server_ip = servers.get(server_id)[0]

    f.close()

def initialize_routing_table():
    # Result in this format:
    # destination-server id : [next hop server id, cost of path]

    # First, add all server id into the dictionary and set values to none
    global routing_table, server_id, costs

    # key of servers is the server id
    for id in servers:
        routing_table[id] = [None, math.inf]
    
    # destination to own server has cost of 0
    routing_table[server_id] = [server_id, 0]

    # initially, the best known costs is directly to the neighbor (next hop is same as destination hop)
    for _, neighbor, cost in costs:
        routing_table[neighbor] = [neighbor, cost]

def send_routing_updates():
    routing_update = {
        "Number of update fields" : len(routing_table),
        "Server port" : port,
        "Server IP" : server_ip,
        "Servers" : [] # Array of dictionaries
    }

    for destination_id in routing_table:
        # Routing table format was this: destination id : [next_hop id, cost]

        n_server = {
            "Server IP address" : servers.get(destination_id)[0], # get server ip from given server id
            "Server port" : servers.get(destination_id)[1],
            "Server ID" : destination_id,
            "Cost" : routing_table[destination_id][1]
        }

        routing_update["Servers"].append(n_server)

# For debug purposes
def print_vars():
    print("Printing all variables:")
    print("Num servers:")
    print(num_servers)
    print("Num neighbors:")
    print(num_neighbors)
    print("Servers:")
    print(servers)
    print("Costs:")
    print(costs)
    print("Routing update interval:")
    print(routing_update_interval)
    print("Server id:")
    print(server_id)
    print("Server ip:")
    print(server_ip)
    print("Port:")
    print(port)
    print("Routing Table:")
    print(routing_table)

if __name__ == "__main__":
    main()