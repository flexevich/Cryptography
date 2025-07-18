import json
import socket
import time
from sha import *
from rsa import *

def B():
    block_size = 128
    k = 1024
    p = generate_p(k)
    q = generate_p(k)
    
    while q == p:
        q = generate_p(k)
    
    pub_key_b, priv_key_b = rsa(p, q)
    
    # Set up server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
        s.bind(("localhost", 5000))
        s.listen(1)
        print("B запущен и ожидает подключения...")
        
        # Accept client connection
        conn, addr = s.accept()
        with conn:
            print(f"Подключен клиент: {addr}")
            
            # Send public key to client
            key = {
                "tsa_key": [str(pub_key_b[0]), str(pub_key_b[1])]
            }
            key_ = json.dumps(key).encode('utf-8')
            key_length = len(key_)
            key_length_bytes = key_length.to_bytes(4, 'big')
            conn.sendall(key_length_bytes)
            conn.sendall(key_)
            print("Сервер: ключи отправлены...")
            
            # Receive data from client
            len_bytes = conn.recv(4)
            if len(len_bytes) != 4:
                raise Exception("Не удалось прочитать длину ответа")
            data_length = int.from_bytes(len_bytes, 'big')
            
            # Read the response
            data = b""
            while len(data) < data_length:
                chunk_ = conn.recv(min(1024, data_length - len(data)))
                if not chunk_:
                    raise Exception("Соединение прервано клиентом")
                data += chunk_
            
            # Decode and parse response
            data_str = data.decode('utf-8')
            data_json = json.loads(data_str)
            ciphertext = data_json["ciphertext"]
            msg_str = decrypt_message(ciphertext, priv_key_b, block_size)
            try:
                msg = json.loads(msg_str)  # Преобразование строки в словарь
            except json.JSONDecodeError as e:
                raise Exception(f"Ошибка декодирования JSON: {e}")
            k = msg["k"]
            timestamp = msg["timestamp"]
            signature = msg["signature"]
            pub_key_a = msg["pub_key_a"]
            hash_user_msg = sha256(("AGENT007" + k + timestamp).encode('utf-8'))
            hash_for_verification = decrypt_message(signature, pub_key_a, block_size)
            
            if hash_user_msg == hash_for_verification:
                print("Подпись прошла проверку!")
            else:
                print("Проверка подписи не пройдена!")

if __name__ == "__main__":
    B()