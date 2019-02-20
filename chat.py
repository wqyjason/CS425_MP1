import socket
import threading
import sys
import time
import argparse
from random import randint
class Server:
        connections = []
        peers = []
        def __init__(self, port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # create server
                host = socket.gethostname();
                sock.bind((host, port))
                sock.listen(1)
                print("server running....")
                while True:
                        c, a = sock.accept()
                        cThread = threading.Thread(target=self.handler, args = (c,a))
                        cThread.daemon = True
                        cThread.start()
                        self.connections.append(c)
                        # self.peers.append(a[0])
                        print(str(a[0]) + ':' + str(a[1]), "connected")
                        # self.sendPeers()
                        # 
                        # if (len(self.connections) == num):
                        #     print("Ready")
        def handler(self, c, a):
                while True:
                        data = c.recv(1024)
                        # multicast sender here
                        for connection in self.connections:
                                connection.send(bytes(data))
                        if not data:
                                # send failure info to every node
                                for connection in self.connections:
                                    fail = str(a[0]) + ':' + str(a[1]) + "disconnected"
                                    connection.send(fail.encode())
                                # remove the connection
                                self.connections.remove(c)
                                # self.peers.remove(a[0])
                                c.close()
                                # self.sendPeers()
                                break


        # def sendPeers(self):
        #         p = ""
        #         for peer in self.peers:
        #                 p = p + peer + ","
        #         for connection in self.connections:
        #                 connection.send(b'\x11' + bytes(p, "utf-8"))

class Client:
    
    def sendMsg(self, sock):
            while True:
                    sock.send(bytes(input(""), 'utf-8'))
    def __init__(self, host, port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # connect to the target server
            sock.connect((host, port))
            iThread = threading.Thread(target=self.sendMsg, args = (sock,))
            iThread.daemon = True
            iThread.start()
            while True:
                    # multicast receiver here
                    data = sock.recv(1024)
                    if not data:
                            break;
                    # if data[0:1] == b'\x11':
                    #         self.updatePeers(data[1:])
                    # else:
                    print(str(data,'utf-8'))


#     def updatePeers(self, peerData):
#             p2p.peers = str(peerData, "utf-8").split(",")[:-1]

# class p2p:
#         peers = ['127.0.0.1']


# # exit the app if Ctrl+C
# def signal_handler(sig, frame):
#         # print("here")
#         # sThread.join()
#         sys.exit(0)

def start(ip, port):

    host = socket.gethostbyname(ip)
    # create one server and one client for each node
    sThread = threading.Thread(target=Server, args=(port,))
    cThread = threading.Thread(target=Client, args=(host, port))
    # append the threads to array 
    servers.append(sThread)
    clients.append(cThread)

    # start the thread
    sThread.start()
    time.sleep(5)
    cThread.start()



    # while True:
    #         try:
    #                 print("Tring to connect ...")
    #                 time.sleep(randint(1, 5))
    #                 for peer in p2p.peers:
    #                         try:
    #                                 client = Client(peer)
    #                         except KeyboardInterrupt:
    #                                 sys.exit(0)
    #                         except:
    #                                 pass
    #                         try:
    #                                 # Thread for server so current node could be client as well
    #                                 sThread = threading.Thread(target = Server, args = ())
    #                                 sThread.start()
    #                                 # signal.signal(signal.SIGINT, signal_handler)

    #                         except KeyboardInterrupt:
    #                                 sys.exit(0)
    #                         except:
    #                                 print("Couldn't start the server ...")
    #         except KeyboardInterrupt:
    #                 sys.exit(0)


servers = []
clients = []

def main():
    # parse the command line
    # parser = argparse.ArgumentParser(description = 'Distributed Chat')
    # parser.add_argument('name', type=str)
    # parser.add_argument('port', type=int)
    # parser.add_argument('number', type=int)
    # args = parser.parse_args()
    # name = args.name
    # port = args.port
    # num  = args.number
    # all = []
    all = [ "sp19-cs425-g04-01.cs.illinois.edu", "sp19-cs425-g04-02.cs.illinois.edu", "sp19-cs425-g04-03.cs.illinois.edu" ]
            # "sp19-cs425-g04-04.cs.illinois.edu", "sp19-cs425-g04-05.cs.illinois.edu", "sp19-cs425-g04-06.cs.illinois.edu", 
            # "sp19-cs425-g04-06.cs.illinois.edu", "sp19-cs425-g04-08.cs.illinois.edu", "sp19-cs425-g04-09.cs.illinois.edu", 
            # "sp19-cs425-g04-10.cs.illinois.edu" ]
    local = socket.gethostname()
    for i in all:
        if i != local:
            start(i, 10006)
        else:
            print(socket.gethostbyname(local))




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
