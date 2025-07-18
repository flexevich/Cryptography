import json
import socket
import time
import random
from sha import *
from rsa import *

def A():
    block_size = 128
    k = 1024
    p = generate_p(k)
    q = generate_p(k)
    
    while p == q:
        q = generate_p(k)
    
    pub_key_a, priv_key_a = rsa(p, q)
    k_random = str(random.getrandbits(256))
    timestamp = time.strftime("%y%m%d%H%M%SZ", time.gmtime())
    
    # Создание подписи
    data_to_sign = "AGENT007" + k_random + timestamp
    signature_ = sha256(data_to_sign.encode('utf-8'))
    signature = encrypt_message(signature_, priv_key_a, block_size)
    
    # Установка соединения с сервером
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 5000))
        
        # Получение публичного ключа сервера
        len_bytes = s.recv(4)
        if len(len_bytes) != 4:
            raise Exception("Не удалось прочитать длину ответа")
        key_length = int.from_bytes(len_bytes, 'big')
        
        # Чтение данных ключа
        key_data = b""
        while len(key_data) < key_length:
            chunk_ = s.recv(min(1024, key_length - len(key_data)))
            if not chunk_:
                raise Exception("Соединение прервано сервером")
            key_data += chunk_
        
        # Декодирование и разбор ключа
        key_str = key_data.decode('utf-8')
        key_json = json.loads(key_str)
        pub_key_b = tuple(int(x) for x in key_json["tsa_key"])
        
        # Подготовка сообщения для шифрования
        msg_for_encrypt = {
            "k": k_random,
            "timestamp": timestamp,
            "signature": signature,
            "pub_key_a": pub_key_a
        }
        ciphertext = encrypt_message(json.dumps(msg_for_encrypt), pub_key_b, block_size)
        
        # Отправка зашифрованного сообщения серверу
        data = {
            "ciphertext": ciphertext
        }
        data_json = json.dumps(data)
        data_bytes = data_json.encode('utf-8')
        data_length = len(data_bytes)
        data_length_bytes = data_length.to_bytes(4, 'big')
        
        s.sendall(data_length_bytes)
        s.sendall(data_bytes)
        print("Данные успешно отправлены!")

if __name__ == "__main__":
    A()