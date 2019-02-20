import socket
import threading
import sys
import time
import argparse
import pickle
from random import randint
from threading import Lock

# each node build one server for other nodes and holds n-1 sockets to connect other servers
# server-client is build based on TCP and it naturally formed a all-to-all scheme and when
# any node failed, it will send EOF to all other nodes in the chat group, which every nodes
# will detect its failure. 


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

# hold-back queue for causal ordering
holdBack = []


# timestamp for current process
timestamp = []



# lock for handling received message
mutex_r = Lock()

# lock for hanlding hold-back queue
mutex_h = Lock()

# lock for handling timestamp
mutex_t = Lock()


# helper to get process number
def getN():
    host = socket.gethostname()
    ret = int(host.split('-')[3][1])
    if ret == 0:
        return 9
    else:
        return ret - 1

# condition checker for timestamp
def lessThan(senderStamp, receiverStamp, senderIndex):
    i = 0
    while i < len(senderStamp):
        # check for first condition
        if i == senderIndex:
            if senderStamp[i] != receiverStamp[i] + 1:
                return False
        else:
            # check for second condition
            if senderStamp[i] > receiverStamp[i]:
                return False
        i += 1
    return True


# build server for other nodes
def buildServer(port, num):
    # set up sock for listening one node
    sockForListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockForListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # create server
    host = socket.gethostname()
    sockForListen.bind((host, port))
    sockForListen.listen(num)
    print("server running....")

    # count number of connection
    count = 0

    global holdBack

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
def handler(c, a):
    global received
    # name of this node
    hostName = ""

    # receiving messages from this node
    while True:
        data = c.recv(1024)

        # failure detector using EOF
        if not data:
            # print fail message
            fail = hostName + " has left"
            print(fail)
            c.close()
            break

        # deserialize the data
        info= pickle.loads(data)

        # add to hold-back queue
        holdBack.append(info)

        # get the name from each node and store them
        if "NAME&" in info[1]:
            hostName = info[1].split('&')[1]
            continue

        # separate the info
        sender_stamp = info[0]
        msg          = info[1]
        sender_index = info[2]

        # send the message
        if info not in received:
            # mutex to keep received thread-safe
            # add message to received
            mutex_r.acquire()
            received.append(info)
            mutex_r.release()

            # B-multicast to any other nodes
            sendMsg(sender_stamp, msg, sender_index)

        # wait until condition meets for hold-back
        # while True:
        if lessThan(sender_stamp, timestamp, sender_index):

            # remove finished info from hold-back queue
            holdBack.remove(info)
             # avoid left bug
            if msg != '':
                print(msg)

            # update timestamp
            mutex_t.acquire()
            timestamp[sender_index] += 1
            mutex_t.release()

            # break
                


# send message to all other nodes in the group
def sendMsg(timestamp, msg, p_num):
    for sock in sockForSend:
        # serialize timestamp and message together 
        info = pickle.dumps([timestamp, msg, p_num])
        sock.send(info)


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

    # get the process number
    p_num = getN()

    # send the name of this node to every server
    msg = "NAME&" + name
    for sock in sockForSend:
        info = pickle.dumps([timestamp, msg, p_num])
        sock.send(info)

    # sending message to the socket
    while True:
        msg = name + ": " + input("")
        global received
        # append message to received when sender send it
        mutex_r.acquire()
        received.append(msg)
        mutex_r.release()

        # update timestamp
        mutex_t.acquire()
        timestamp[p_num] += 1
        mutex_t.release()

        # for p in timestamp: print(p)

        sendMsg(timestamp, msg, p_num)
        # for multicast test
        # sockForSend[0].send(bytes(msg, 'utf-8'))


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

    # initialize hold back queue
    global timestamp
    timestamp = [0] * (num + 1)

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
