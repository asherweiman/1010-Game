import socket
import sys
import os
import threading
import pickle
from struct import pack,unpack

file_dir = os.path.dirname("TechWTimTutorial-onlineGame")
sys.path.append(file_dir)
from game import Game, Block

default_x = 250
default_y = 450



def threaded_client2(conn, game: Game, block: Block, pos, player: int):
    
    # package info to send
    reply = [block.matrix,block.color, pos[0],pos[1],player]
    
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
                
                # turn has ended, player has placed block
                if data[2] == True:
                    
                    # valid block placement
                    if game.placeBlock((data[1]//45, data[0]//50), block.matrix): 
                        
                        game.player_turn = game.player_turn ^ 1
                        block.matrix = block.genblock()
                        block.color = game.pickColor() 
                       
                    pos[0],pos[1] = default_x, default_y

                # turn is ongoing
                else:
                    
                    # update pos of block so other player knows
                    if game.player_turn == player:
                        pos[0], pos[1] = data[0],data[1]
                
                # assemblying the reply to send       
                reply = [block.matrix, block.color, pos[0],pos[1], game.player_turn]

            print("recieved: ", data)
            print("sending: ", reply)
            print("to: ",player)
            
            # pad packet with length of reply    
            packet = pickle.dumps(reply)
            length = pack('!I',len(packet))
            packet = length + packet
             
            conn.sendall(packet)
            
            
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
 
 
     
def startServer():
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
    
    max_player = 3
    player_num = 0
    g = Game()

    pos = [default_x,default_y]

    block = Block(g.pickColor(), 0, 0)
    block.matrix = block.genblock()

    while True: 
        print("waiting to accept")
        print(threading.active_count())
        if threading.active_count() < max_player:
            conn, addr = s.accept()
            print("Connected to: ", addr)
        else:
            print("waiting to end")
            t.join()
            break
        
        t = threading.Thread(target=threaded_client2, args=(conn, g, block, pos, player_num))
        t.start()
        player_num += 1
        
        
    s.close()

startServer()