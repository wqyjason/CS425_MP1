import socket
import threading
import sys
import time
import argparse
from random import randint
from threading import Lock

# each node build one server for other nodes and holds n-1 sockets to connect other servers
# server-client is build based on TCP and it naturally formed a all-to-all scheme and when
# any node failed, it will send EOF to all other nodes in the chat group, which every nodes
# will detect its failure. 

# TO DO !important: implement a reliable multicast and a causal ordering


# hard-coded IP addresses for VM
all = [ "sp19-cs425-g04-01.cs.illinois.edu", "sp19-cs425-g04-02.cs.illinois.edu", "sp19-cs425-g04-03.cs.illinois.edu",
        "sp19-cs425-g04-04.cs.illinois.edu", "sp19-cs425-g04-05.cs.illinois.edu", "sp19-cs425-g04-06.cs.illinois.edu", 
        "sp19-cs425-g04-07.cs.illinois.edu", "sp19-cs425-g04-08.cs.illinois.edu", "sp19-cs425-g04-09.cs.illinois.edu", 
        "sp19-cs425-g04-10.cs.illinois.edu" ]

# checker for when to print READY
server_checked = False
client_checked = False

# holds all the connection of server
connections = []

# hold all the socket to send message
sockForSend = []

# received message from all nodes
received = []

# dictionary for host names
hostName = {}

# lock for handle received message
mutex = Lock()


# build server for other nodes
def buildServer(port, num):
    # set up sock for listening one node
    sockForListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockForListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # create server
    host = socket.gethostname();
    sockForListen.bind((host, port))
    sockForListen.listen(num)
    print("server running....")

    # count number of connection
    count = 0

    while True:
        c, a = sockForListen.accept()
        # create thread for this connection listening
        cThread = threading.Thread(target=handler, args = (c,a))
        cThread.daemon = True
        cThread.start()
        connections.append(c)
        count += 1
        # break out the loop if all is connected
        if (count == num):
            global server_checked
            server_checked = True
            break


# handler for receiving messages from one node
# TO DO: adding multicast & causal ordering here?
def handler(c, a):
    global received
    # name of this node
    hostName = ""

    # receiving messages from this node
    while True:
        data = c.recv(1024)
        msg = str(data, 'utf-8')

        # failure detector using EOF
        if not data:
            # print fail message
            fail = hostName + " has left"
            print(fail)
            c.close()
            break

        # get the name from each node and store them
        if "NAME&" in msg:
            print("adding name...")
            hostName = msg.split('&')[1]
            continue
        # send the message
        elif msg not in received:
            # mutex to keep received thread-safe
            # add message to received
            mutex.acquire()
            received.append(msg)
            mutex.release()

            # B-multicast to any other nodes
            sendMsg(msg)

            # avoid left bug
            if msg != '':
                print(hostName + ': ' + msg)
            # mutex to keep received thread-safe
            # remove handled info from received
            mutex.acquire()
            received.remove(msg)
            mutex.release()



# multicast group should be all the
# clients on the current server thus
# no need to keep track of multicast
# group

# message that one process has received


# send message to all other nodes in the group
def sendMsg(msg):
    for sock in sockForSend:
        sock.send(bytes(msg, 'utf-8'))



# this should be run when other clients
# received the message
def receiver(m, sender):
    # for integrity
    if (m not in received):
        received.append(m)
        # sender don't have to send to others again
        if (name != sender):
            # forward message to other clients
            sendMsg(m)
        # deliver the message to node's dispaly
        deliver(m)


# connect to other nodes' server using (n-1) sockets
def connectServer(port, num, name):
    # initialize num sockets for sending
    for i in range(num):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockForSend.append(sock)

    # count how many server connected
    count = 0
    # store the server that don't need to connect again
    connected = [socket.gethostname()]
    # loop until connect all the servers
    while True:
        for i in all:
            if i not in connected:
                try:
                    # connect each socket to each server
                    host = socket.gethostbyname(i)
                    sockForSend[count].connect((host, port))
                    # add the server to the array
                    connected.append(i)
                except Exception as e:
                    # continue to next loop if connect failed
                    continue
                
                count += 1

                # break if all nodes are connected
                if count == num:
                    break
        # break out while loop
        if count == num:
            global client_checked
            client_checked = True
            break

    # send the name of this node to every server
    msg = "NAME&" + name
    for sock in sockForSend:
        sock.send(bytes(msg, 'utf-8'))

    # sending message to the socket
    while True:
        msg = input("")
        global received
        # append message to received when sender send it
        mutex.acquire()
        received.append(msg)
        mutex.release()
        sendMsg(msg)


def main():
    # parse the command line
    parser = argparse.ArgumentParser(description = 'Distributed Chat')
    parser.add_argument('name', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('number', type=int)
    args = parser.parse_args()
    name = args.name
    port = args.port
    num  = args.number - 1

    server = threading.Thread(target=buildServer, args=(port, num))
    client = threading.Thread(target=connectServer, args=(port, num), kwargs={"name": name})

    # start server and client
    server.start()
    client.start()

    while True:
        if server_checked and client_checked:
            print("READY")
            break

    
    # a signal handler here?


# entry point for application
if __name__ == '__main__':
    main()

