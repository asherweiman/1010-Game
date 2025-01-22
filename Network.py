import socket
import pickle
#TODO timer for broadcast import time
from struct import pack, unpack

class Network:
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.broadcast_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        local_ip = self.get_address()
        self.buffer_size = 2048
        
        self.broadcast_port = 9090
        print(f"broadcast binding to: {local_ip}, {self.broadcast_port}")
        try:
            self.broadcast_socket.bind((local_ip, 8080))
        
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.broadcast_socket.settimeout(1)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as e:
            print(e)
        
        
        """try:
        
            self.client.connect(self.addr)
        except socket.error as e:
            print(e)"""
        
    # broadcast for LAN discovery returns the server addr
    def LAN_discovery(self):
        
        broadcast_addr = ("255.255.255.255", self.broadcast_port)
        msg = b'this is a msg'
        broadcasting = True
        while broadcasting:
            try:
                print("Sending broadcast")
                self.broadcast_socket.sendto(msg,broadcast_addr)
                print("after broadcast")
                data, addr = self.broadcast_socket.recvfrom(self.buffer_size)
                print(f"got a reply from: {addr} saying: {data}")
                
                
                #TODO check data integrity
                return addr
            except socket.error as e:
                print("error in broadcasting: ", e)
            
            except socket.timeout:
                print("timeout")
                continue
    
    def connect_LAN_server(self):
        
        server_addr = self.LAN_discovery()
        connection_addr = (server_addr[0], 8080)
        print(connection_addr) 
        try:
            self.client.connect(connection_addr)
            
        except socket.error as e:
            print(e)
     
    def recv_msg(self):
        try:
            # get length of data from buffer
            buf = b''
            while len(buf) < 4:
                buf += self.client.recv(4 - len(buf))
            length = unpack('!I',buf)[0]
            
            data = self.client.recv(length)
            
            return pickle.loads(data)   
        except socket.error as e:
            print(e)
            
    def send(self, data):
        try: 
            # pad buffer w/ length of data
            packet = pickle.dumps(data)
            length = pack('!I', len(packet))
            packet = length + packet
            self.client.sendall(packet)
        except socket.error as e:
            print(e)
    
    def get_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        addr = s.getsockname()[0]
        return addr