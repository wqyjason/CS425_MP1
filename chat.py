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

server_checked = False
client_checked = False

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


        while True:
            c, a = sockForListen.accept()
            # create thread for this connection listening
            cThread = threading.Thread(target=self.handler, args = (c,a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            print(str(a[0]) + ':' + str(a[1]), "connected")
            count += 1
            # break out the loop if all is connected
            if (count == num):
                server_checked = True
                print("server checked")
                break


    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            print(str(data,'utf-8'))
            if not data:
                # print fail message
                fail = str(a[0]) + ':' + str(a[1]) + "disconnected"
                print(fail)
                c.close()
                break


sockForSend = []

# connect to other nodes' server using (n-1) sockets
def connectOther(port, num):
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
            client_checked = True
            print("client checked")
            break

    # sending message to the socket
    while True:
        msg = input("")
        for sock in sockForSend:
            sock.send(bytes(msg, 'utf-8'))



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

    server = threading.Thread(target=Server, args=(port, num))
    client = threading.Thread(target=connectOther, args=(port, num))

    # start server and client
    server.start()
    client.start()

    # print READY if all is connected
    if server_checked and client_checked:
        print("READY")
    
    if server_checked == False and client_checked == False:
        print("WHAT???")

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
