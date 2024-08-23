import socket
import pickle
from struct import pack, unpack

class Network:
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ""#"192.168.1.1" #"192.168.48.1"
        self.port = 8080
        self.buffer_size = 2048
        self.addr = (self.server, self.port)
        self.client.connect(self.addr)
        
    def connect(self):
        try:
            # get length data from buffer
            
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
    
    def getBlock(self):
        return self.connect()
    
    