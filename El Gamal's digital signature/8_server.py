import json
import socketserver
import time
from sha import *  
from ElGamal import *


block_size = 128

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        
        ######################################## ответ от клиента ###################################
        # Чтение длины запроса 
        length_bytes = self.request.recv(4)

        request_length = int.from_bytes(length_bytes, 'big')

        # Чтение самого запроса
        request_data = b""
        while len(request_data) < request_length:
            chunk = self.request.recv(min(1024, request_length - len(request_data)))
            request_data += chunk

        # Декодирование и парсинг запроса
        request_str = request_data.decode('utf-8')
        request = json.loads(request_str)
        print("получен запрос:", request)

        signatura = request["signatura"]  # Подпись в байтах
        message = request["message"].encode('utf-8')  # Сообщение в байтах
        hash_algorithm = request["hash_algorithm"]
        pub_key = request["pub_key"]
        r, s = signatura
        p, alpha, b = pub_key
        # Проверка хеша
        hash = int.from_bytes(bytes.fromhex(sha256(message)), 'big')
        print(hash)
        p1 = fast_exp_mod(alpha, hash, p)
        p2 = (fast_exp_mod(b, r, p) * fast_exp_mod(r, s, p)) % p
        print(p1)
        print(p2)
        if p1 == p2:
            print("подпись верна ")
        else:
            raise ValueError("подпись не верна")
        
        ######################################## ответ клиенту #######################################

        p_serv, a_serv, alpha_serv, b_serv = generate(1024)

        pub_key_tsa = (p_serv, alpha_serv, b_serv)
        priv_key_tsa = (a_serv)
     
        # save_public_key(pub_key_tsa, 'tsa_public_key.json')
        # save_private_key(priv_key_tsa, 'tsa_private_key.json')

        timestamp = time.strftime("%y%m%d%H%M%SZ", time.gmtime())  # UTC время
        print("временная метка:", timestamp)

        hash_m = sha256(message)
        print("hash_m: ", hash_m)
        p_minus_1 = p_serv - 1
        while True:
            k = random.randint(1, p_minus_1)
            g, _, _ = euclidean_algorithm(k, p_minus_1)
            if g == 1:
                break
        # Хеш сообщения
        hash_m_1 = int.from_bytes(bytes.fromhex(hash_m), 'big')
        
        # Вычисление r = alpha^k mod p
        r_serv = fast_exp_mod(alpha_serv, k, p_serv)
    
        # Вычисление мультипликативного обратного k по модулю p-1
        g, x, _ = euclidean_algorithm(k, p_minus_1)
        if g != 1:
            raise ValueError("Обратное число не существует")

        # Вычисление s = k^(-1) * (H(m) - a * r) mod (p-1)
        k_inv_serv =  x % p_minus_1

        s_serv = (k_inv_serv * (hash_m_1 - a_serv * r_serv)) % (p_serv - 1)
        tsa_signature = (r_serv, s_serv)
    

        response = {
            "hash": hash_m,
            "timestamp": str(timestamp),
            "tsa_signature": [int(r_serv), int(s_serv)],
            "tsa_key": [int(p_serv), int(alpha_serv), int(b_serv)]
        }
        print(response)
        response_b = json.dumps(response).encode('utf-8')

        # Отправка ответа
        response_length = len(response_b)
        response_length_bytes = response_length.to_bytes(4, 'big')
        self.request.sendall(response_length_bytes)
        self.request.sendall(response_b)
        print("Сервер: Ответ отправлен успешно: ")

def main():
    server = socketserver.TCPServer(('127.0.0.1', 4567), MyTCPHandler)
    print("Сервер запущен")
    server.serve_forever()

if __name__ == "__main__":
    main()