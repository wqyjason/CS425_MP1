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


connections = []

class Server:
    # peers = []
    def __init__(self, port, num):
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


        # since only bind with one client, not need for while loop
        while True:
            c, a = sockForListen.accept()
            cThread = threading.Thread(target=self.handler, args = (c,a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            print(str(a[0]) + ':' + str(a[1]), "connected")
            count += 1
            if (count == num):
                print("server set up")
                break


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
                    host = socket.gethostbyname(i)
                    sockForSend.connect((host, port))
                except Exception as e:
                    # continue to next loop if connect failed
                    continue
                
                count += 1

                if count == 2:
                    print("can do")

                # break if all nodes are connected
                if count == num:
                    print("all set inside")
                    break
        # break out while loop
        if count == num:
            print("all set")
            break

    # start sending message to the socket
    sendMsg(sockForSend)



def main():
    # parse the command line
    parser = argparse.ArgumentParser(description = 'Distributed Chat')
    # parser.add_argument('name', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('number', type=int)
    args = parser.parse_args()
    # name = args.name
    port = args.port
    num  = args.number - 1
    print(str(num))

    server = threading.Thread(target=Server, args=(port, num))
    client = threading.Thread(target=connectOther, args=(port, num))

    # start server and client
    server.start()
    client.start()

    # a signal handler here?


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
