import socket
import sys
import os
import threading
import pickle
from selectors import DefaultSelector, EVENT_READ
from struct import pack,unpack
from game import Game, Block

default_x = 250
default_y = 450
CLIENT_MSG_SIZE = 2048 # change later


def client_thread(conn: socket.socket, game: Game, block: Block, pos, player: int, num_max_players: int):
    
    
    # send game board
    send_game_board(game,conn)
    
    # send block and player number
    reply = [block.matrix,block.color, pos[0],pos[1], player]
    
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
                
                # turn has possibly ended, player has tried to placed block
                if data[2] == True:
                    
                    # valid block placement
                    if game.placeBlock((data[1]//45, data[0]//50), block): 
                        game.endTurn(block)
                        # switch player turn and gen new block and color
                        game.player_turn = (game.player_turn % num_max_players) + 1
                        block.color = game.pickColor() 
                        block.matrix = block.genblock()
                    
                    pos[0], pos[1] = default_x, default_y
                    print("pos reset:", pos)
                    
                
                # turn is ongoing
                else:
                    
                    # update pos of block so other player knows
                    if game.player_turn == player:
                        pos[0], pos[1] = data[0], data[1]
                
                # what to send to client      
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

# handles receiving packets with len of msg encoded at start    
def recv_buf(s: socket.socket):

    buf = b''
    while len(buf) < 4:
        buf += s.recv(4 - len(buf))
    length = unpack('!I',buf)[0]
    
    data = s.recv(length)
    
    return pickle.loads(data)
 
def send_game_board(g: Game, conn: socket.socket):
    
    packet = pickle.dumps(g.board)
    length = pack('!I', len(packet))
    packet = length + packet
    conn.sendall(packet)

# handles replyies to broadcasts over LAN
def lan_reply(broadcats_socket: socket.socket, mask):
    
    client_msg, client_addr = broadcats_socket.recvfrom(CLIENT_MSG_SIZE)

    #TODO check client msg here 
    
    # reply
    reply = b'salutations!'
    
    broadcats_socket.sendto(reply, client_addr)

# start server for LAN 
def start_server():
    server = "127.0.0.1" #"192.168.1.202" #"127.0.0.1" #"192.168.48.1"
    broadcast_port = 9090
    port = 8080

    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    
    # Enable broadcasting mode
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    


    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    print("GET HOST BY NAME: ", socket.gethostbyname(socket.gethostname()))

    

    try:
        tcp_socket.bind(("",port))
        print(f"binded on {port}")
    except socket.error as e: 
        print(str(e))
        sys.exit()

    try:
        broadcast_socket.bind(("",broadcast_port))
        print(f"BROADCAST binded on {broadcast_port}")
    except socket.error as e: 
        print(str(e))
        sys.exit()
    
    
    tcp_socket.listen(2)
    print("waiting for client, server started")
    
    max_player = 2
    player_num = 1
    g = Game()

    pos = [default_x,default_y]

    block = Block(g.pickColor(), 0, 0)
    block.matrix = block.genblock()
    threads = []

    
    sel = DefaultSelector()
    sel.register(broadcast_socket, EVENT_READ, lan_reply)
    sel.register(tcp_socket, EVENT_READ, None)
    
    # get players into game and handle connections 
    while True: 
        
        print("waiting to accept")
        print(threading.active_count())
        
        if player_num <= max_player:
            events = sel.select()
            for key, mask in events:
                
                # connect players to server 
                if key.fileobj.fileno()== tcp_socket.fileno():
                    
                    conn, addr = tcp_socket.accept()
                    print("Connected to: ", addr)
                    threads.append(threading.Thread(target=client_thread, args=(conn, g, block, pos, player_num, max_player)))
                    threads[-1].start()
                    player_num += 1
            
                else: # handle broadcast
                    func = key.data
                    func(key.fileobj, mask)
                         
        else:
            print("waiting to end")
            threads[0].join()
            break
        
        
        
    broadcast_socket.close()
    tcp_socket.close()

start_server()