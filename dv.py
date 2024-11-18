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

def main():
    # read_topology("topology_init.txt")
    while True:
        command = input("Enter command: ").strip().split()

def read_topology(fileDirectory):
    # f = open("topology_init.txt")
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
        
        costs[information[1]] = information[2]

    f.close()

    # print("Printing results:")
    # print(num_servers)
    # print(num_neighbors)
    # print(servers)
    # print(costs)


if __name__ == "__main__":
    main()