import socket
import sys
import os
import threading
import pickle
from struct import pack,unpack

file_dir = os.path.dirname("TechWTimTutorial-onlineGame")
sys.path.append(file_dir)
from game import Game, Block

server = "127.0.0.1" #"192.168.1.202" #"127.0.0.1" #"192.168.48.1"
port = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

print(socket.gethostbyname(server))


try:
    s.bind((socket.gethostbyname(server),port))
    print(f"binded {server} and {port}")
except socket.error as e: 
    print(str(e))
    sys.exit()

s.listen(2)
print("waiting for client, server started")

default_x = 250
default_y = 450
pos = [default_x,default_y]

turn = 1

block = Block((0,0,0),0,0)
block.matrix = block.genblock()

def threaded_client2(conn, game: Game, pos ,player: int):
    
    # temp green
    color = (0,255,0)
    
    # package info to send
    reply = [block.matrix,color, pos[0],pos[1],player]
    
    for i in block.matrix:
        print(i)
    print("sent: ", reply)
    packet = pickle.dumps(reply)
    length = pack('!I',len(packet))
    packet = length + packet
    conn.send(packet)
    
    reply = ""
    
    while True:
        
        try: 
            print("waiting to receive from: ", player)
            
            data = recv_buf(conn)
            
            if not data:
                print("disconnect")
                break
            else:    
                print(pos)
                
                if data[2] == True:
                    if game.placeBlock((data[1]//45, data[0]//50), block.matrix): 
                        
                        game.player_turn = game.player_turn ^ 1
                        block.matrix = block.genblock()
                        
                    pos[0],pos[1] = default_x, default_y

                else:
                    if game.player_turn == player:
                        pos[0], pos[1] = data[0],data[1]
                         
                reply = [block.matrix, color, pos[0],pos[1], game.player_turn]

                print("recieved: ", data)
                print("sending: ", reply)
                print("to: ",player)
                
                
            packet = pickle.dumps(reply)
            length = pack('!I',len(packet))
            packet = length + packet
                    
            conn.sendall(packet)
            
            # set up for next turn
            
            
        except socket.error as e:
            print(e)
            break 
        
    print("lost connection")
    conn.close()
    sys.exit()
        
def recv_buf(s: socket.socket):

    buf = b''
    while len(buf) < 4:
        buf += s.recv(4 - len(buf))
    length = unpack('!I',buf)[0]
    
    data = s.recv(length)
    
    return pickle.loads(data)
     
max_player = 3
player_num = 0
g = Game()

while True: 
    print("waiting to accept")
    
    if threading.active_count() < max_player:
        conn, addr = s.accept()
        print("Connected to: ", addr)
    else:
        print("waiting to end")
        t.join()
        break
    p = player_num
    t = threading.Thread(target=threaded_client2, args=(conn, g,pos, p))
    t.start()
    player_num += 1
    
    
s.close()