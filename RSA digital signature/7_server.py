import json
import socketserver
import time
from sha import *  
from RSA import *  


block_size = 128

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
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

        

        signature = request["signature"]  # Подпись в байтах
        message = request["message"].encode('utf-8')  # Сообщение в байтах
        hash_algorithm = request["hash_algorithm"]
        pub_key = request["pub_key"]



        s_byte = [s_byt.to_bytes((s_byt.bit_length() + 7) // 8, 'big') for s_byt in signature]
        s_bytes = b''.join(s_byte)
        comb = message+s_bytes
        combo = comb
        hash_m_ = sha256(combo)
        
        
        # Проверка хеша
        signature_dec = decrypt_message(signature, pub_key, block_size)
        hash_calculated = sha256(message)
        if hash_calculated != signature_dec:
            print("xeш не совпадает")
            return
        
        
        ######################################## ответ клиенту #######################################
        
        p_tsa = generate_p(1024)
        q_tsa = generate_p(1024)
        while q_tsa == p_tsa:
            q_tsa = generate_p(1024)
        pub_key_tsa, priv_key_tsa = rsa(p_tsa, q_tsa)

     
        save_public_key(pub_key_tsa, 'tsa_public_key.json')
        save_private_key(priv_key_tsa, 'tsa_private_key.json')

        timestamp = time.strftime("%y%m%d%H%M%SZ", time.gmtime())  # UTC время
        print("временная метка:", timestamp)

        data_to_sign = (hash_m_ + timestamp).encode('utf-8')
        hash_to_sign = sha256(data_to_sign)
        tsa_signature = encrypt_message(hash_to_sign, priv_key_tsa, block_size)
    

        response = {
            "timestamp": str(timestamp),
            "tsa_signature": tsa_signature,
            "tsa_key": pub_key_tsa
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