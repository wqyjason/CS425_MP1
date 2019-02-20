import socket
import threading
import sys
import time
import argparse
from random import randint

all = [ "sp19-cs425-g04-01.cs.illinois.edu", "sp19-cs425-g04-02.cs.illinois.edu", "sp19-cs425-g04-03.cs.illinois.edu" ]
            # "sp19-cs425-g04-04.cs.illinois.edu", "sp19-cs425-g04-05.cs.illinois.edu", "sp19-cs425-g04-06.cs.illinois.edu", 
            # "sp19-cs425-g04-06.cs.illinois.edu", "sp19-cs425-g04-08.cs.illinois.edu", "sp19-cs425-g04-09.cs.illinois.edu", 
            # "sp19-cs425-g04-10.cs.illinois.edu" ]


servers = []

class Server:
    # peers = []
    def __init__(self, port):
        # set up sock for listening one node
        sockForListen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockForListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # create server
        host = socket.gethostname();
        sockForListen.bind((host, port))
        sockForListen.listen(1)
        print("server running....")
                # while True:

        # since only bind with one client, not need for while loop
        c, a = sockForListen.accept()
                        # cThread = threading.Thread(target=self.handler, args = (c,a))
                        # cThread.daemon = True
                        # cThread.start()
                        # self.connections.append(c)
                        # self.peers.append(a[0])
        print(str(a[0]) + ':' + str(a[1]), "connected")
        self.handler(c, a)
                        # self.sendPeers()
                        # 
                        # if (len(self.connections) == num):
                        #     print("Ready")
    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            # multicast sender here
            # for connection in self.connections:
            #         connection.send(bytes(data))
            print(str(data,'utf-8'))
            if not data:
                # print fail message
                fail = str(a[0]) + ':' + str(a[1]) + "disconnected"
                print(fail)
                c.close()
                break


        # def sendPeers(self):
        #         p = ""
        #         for peer in self.peers:
        #                 p = p + peer + ","
        #         for connection in self.connections:
        #                 connection.send(b'\x11' + bytes(p, "utf-8"))

# class Client:
    
#     def sendMsg(self, sock):
#             while True:
#                     sock.send(bytes(input(""), 'utf-8'))
#     def __init__(self, host, port):
#             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#             # connect to the target server
#             sock.connect((host, port))
#             iThread = threading.Thread(target=self.sendMsg, args = (sock,))
#             iThread.daemon = True
#             iThread.start()
#             while True:
#                     # multicast receiver here
#                     data = sock.recv(1024)
#                     if not data:
#                             break;
#                     if data[0:1] == b'\x11':
#                             self.updatePeers(data[1:])
#                     else:
#                     print(str(data,'utf-8'))


#     def updatePeers(self, peerData):
#             p2p.peers = str(peerData, "utf-8").split(",")[:-1]

# class p2p:
#         peers = ['127.0.0.1']



# send message to target socket
def sendMsg(sock):
    while True:
        sock.send(bytes(input(""), 'utf-8'))

# connect to other nodes' server
def connectOther(port, num):
    # set up the socket for sending message
    sockForSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockForSend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # count how many server connected
    count = 0
    local = socket.gethostname()
    # loop until connect all the servers
    while True:
        for i in all:
            if i != local:
                try:
                    sockForSend.connect((host, port))
                except Exception as e:
                    # continue to next loop is connect failed
                    continue
                
                count += 1

                # break if all nodes are connected
                if count == num:
                    break
        # break out while loop
        if count == num:
            break

    # start sending message to the socket
    sendMsg(sockForSend)


# start server for other node
def startServer(port):
    # create one server and one client for each node
    sThread = threading.Thread(target=Server, args=(port,))
    # append the threads to array 
    servers.append(sThread)
    # start the thread
    sThread.start()


def main():
    # parse the command line
    parser = argparse.ArgumentParser(description = 'Distributed Chat')
    # parser.add_argument('name', type=str)
    parser.add_argument('port', type=int)
    # parser.add_argument('number', type=int)
    args = parser.parse_args()
    # name = args.name
    port = args.port
    # num  = args.number
    num = 3

    local = socket.gethostname()
    for i in all:
        if i != local:
            startServer(port)

    client = threading.Thread(target = connectOther, args=(port, num))


# entry point for application
if __name__ == '__main__':
    main()



# # multicast group should be all the
# # clients on the current server thus
# # no need to keep track of multicast
# # group

# # message that one process has received
# received = []

# # this should be run when other clients
# # received the message
# def receiver(m, sender):
#     # for integrity
#     if (m not in received):
#         received.append(m)
#         # sender don't have to send to others again
#         if (name != sender):
#             # forward message to other clients
#             sendMsg(m)
#         # deliver the message to node's dispaly
#         deliver(m)
