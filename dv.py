import socket
import threading
import sys

num_servers = -1
num_neighbors = -1

# Data entered should be like this:
# server id # : [IP, port]
servers = {}

# Data entered should be like this:
# neighbor id # : cost
costs = {}

server_id = -1
port = -1

routing_update_interval = -1

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
            print_vars()
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
        elif cmd == "crash":
            print("Closing all connections")


def read_topology(fileDirectory):
    global num_servers, num_neighbors, server_id, port
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
        
        server_id = information[0]
        
        costs[information[1]] = information[2]
    
    port = servers[server_id][1]

    f.close()

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
    print("Port:")
    print(port)

if __name__ == "__main__":
    main()