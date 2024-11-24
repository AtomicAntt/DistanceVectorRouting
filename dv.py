import socket
import threading
import sys
import math
import time
import json

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

lock = threading.Lock() # so shared memory can be altered with threads safely

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

            receive_routing_thread = threading.Thread(target=receive_routing_updates)
            receive_routing_thread.daemon = True
            receive_routing_thread.start()

            periodic_update_thread = threading.Thread(target=periodic_updates)
            periodic_update_thread.daemon = True
            periodic_update_thread.start()

            print_vars() # for debugging
        elif cmd == "update":
            if len(command) != 4:
                print("update ERROR, correct usage: update <server-ID1> <server-ID2> <Link Cost>")
                continue
        elif cmd == "step":
            print("Sending routing update to neighbors")
            send_routing_updates()
        elif cmd == "packets":
            global packets_received
            print("Displaying # of distance vector packets this server has received since last invocation:")
            print(packets_received)
            packets_received = 0
        elif cmd == "display":
            print("Current routing table:")
            print("<destination-server-ID> <next-hop-server-ID> <cost-of-path>")
            # print(routing_table)
            # Routing table format (python dictionary) - destination id : [next hop, cost]
            for key, value in routing_table.items():
                print(key + " " + str(value[0]) + " " + str(value[1]))
        elif cmd == "disable":
            if len(command) != 2:
                print("disable ERROR, correct usage: disable <server-ID>")
                continue
        elif cmd == "crash":
            print("Closing all connections")

def periodic_updates():
    while True:
        time.sleep(routing_update_interval)
        send_routing_updates()

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

        servers[information[0]] = [information[1], int(information[2])]
    
    for i in range(num_neighbors):
        information = f.readline().split()
        # format of information should be: [server_id, neighbor_id, cost]

        if len(information) != 3:
            print("Topology file is written wrong, it should be in this format: server-id # and neighbor id and cost")
        
        costs.append([information[0], information[1], int(information[2])])

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
    # Initially, all servers are shown as unreachable (with infinite cost) and next hop is unknown
    for id in servers:
        routing_table[id] = [None, math.inf]
    
    # destination to own server has cost of 0
    routing_table[server_id] = [server_id, 0]

    # Initially, the best known costs is just the link directly to the neighbor (next hop will be same as destination hop)
    for _, neighbor, cost in costs:
        routing_table[neighbor] = [neighbor, cost]

# This function should be called by the step command to send updates right away and every routing update interval.
def send_routing_updates():
    routing_update = {
        "Number of update fields" : len(routing_table),
        "Server port" : port,
        "Server IP" : server_ip,
        "Servers" : [] # Array of dictionaries
    }

    for destination_id in routing_table:
        # Routing table format was this: destination id : [next_hop id, cost]
        # Servers dictionary format was this: server id # : [IP, port]

        n_server = {
            "Server IP address" : servers.get(destination_id)[0], # get server ip from given server id
            "Server port" : servers.get(destination_id)[1],
            "Server ID" : destination_id,
            "Cost" : routing_table[destination_id][1]
        }

        routing_update["Servers"].append(n_server)

    # Value of costs (array) is in this format: [server id, neighbor id, cost]
    # Now send this routing update to all of the neighboring servers
    for _, neighbor, _ in costs:
        neighbor_ip = servers.get(neighbor)[0] # get server ip from given server id
        neighbor_port = servers.get(neighbor)[1] # get server port from given server id

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(json.dumps(routing_update).encode(), (neighbor_ip, int(neighbor_port)))

# This is a thread ran in the main function to read updates + use Bellman Ford equation to determine best routing
def receive_routing_updates():
    global packets_received
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, int(port)))

    while True:
        message, address = server_socket.recvfrom(1024)
        with lock:
            packets_received += 1
            # bellman ford equation to update routing table
            update_routing(json.loads(message.decode()))

# Checks if a better cost is found after processing the routing update given
def update_routing(routing_update):
    num_updates = routing_update["Number of update fields"]
    sender_ip = routing_update["Server IP"]
    sender_port = routing_update["Server port"]
    sender_id = -1

    # value is in format [IP, port]
    # I have to find sender id this way because routing_update does not contain a key for Server ID, but it does have the IP
    for id, value in servers.items():
        if value[0] == sender_ip and value[1] == sender_port:
            sender_id = id
    
    if sender_id == -1:
        print("Sender id was not found when updating routing")
    # else:
    #     print("Got packet from sender id: " + sender_id)
    
    # go through all the destination cost information given by the routing update from this server
    for i in range(num_updates):
        n_server = routing_update["Servers"][i]
        n_dest_id = n_server["Server ID"]
        n_cost = n_server["Cost"] # Cost to go from the server with sender id to the server with dest id

        # Cost for THIS server to go to the server with sender id + n_cost
        new_cost = routing_table[sender_id][1] + n_cost

        # print("New cost coming from server id " + sender_id + " towards destination "  + n_dest_id + ":")
        # print(new_cost)

        # If the cost, according to the current routing table, to the destination improves, change it
        if new_cost < routing_table[n_dest_id][1]:
            # The sender id gets to be the next hop of the routing table
            routing_table[n_dest_id] = [sender_id, new_cost]


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