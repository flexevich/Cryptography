import socket
import random
from laba6 import *
from sha import *
# k alpha x p g
def A():
    
    passwd = 'asd'
    
    p, _, _, _, = generate(512)
    h = int(sha256(passwd.encode("utf-8")))
    g = h % p
    x = random.randint(2, p - 1)
    
    alpha = fast_exp_mod(g, x, p)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 5000))
        data = {
            "alpha": alpha,
            "p": p,
            "g": g
        }
        data_json = json.dumps(data)
        data_bytes = data_json.encode('utf-8')
        data_length = len(data_bytes)
        data_length_bytes = data_length.to_bytes(4, 'big')
        
        s.sendall(data_length_bytes)
        s.sendall(data_bytes)
        
        
        len_bytes = s.recv(4)
        if len(len_bytes) != 4:
            raise Exception("Не удалось прочитать длину ответа")
        length = int.from_bytes(len_bytes, 'big')
        
        # Чтение данных ключа
        data = b""
        while len(data) < length:
            chunk_ = s.recv(min(1024, length - len(data)))
            if not chunk_:
                raise Exception("Соединение прервано сервером")
            data += chunk_
        
        # Декодирование и разбор ключа
        str = data.decode('utf-8')
        json_ = json.loads(str)
        beta = json_["beta"]
        k = fast_exp_mod(beta, x, p)
        
        with open('18_A.txt', 'w') as f:
            f.write(f"p: {p}\n")
            f.write(f"g: {g}\n")
            f.write(f"X: {x}\n")
            f.write(f"Alpha: {alpha}\n")
            f.write(f"K: {k}\n")
            
if __name__ == "__main__":
    A()