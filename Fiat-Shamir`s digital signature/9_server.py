import json
import socketserver
import time
import random
from sha import sha256
from RSA import *

block_size = 128

def generate_fiat_shamir_keys(k, m):
    # Генерация n = p * q
    p = generate_p(k)
    q = generate_p(k)
    while q == p:
        q = generate_p(k)
    n = p * q
    # Генерация закрытого ключа
    a = [random.randint(2, n-1) for _ in range(m)]
    # Генерация открытого ключа
    b = [pow(pow(a_i, -1, n), 2, n) for a_i in a]
    return (b, n), (a, n)

def fiat_shamir_sign(message, priv_key, hash_f, m):
    
    a, n = priv_key
    r = random.randint(1, n-1)
    x = fast_exp_mod(r, 2, n)
    message_bytes = message.encode('utf-8')
    x_bytes = x.to_bytes((x.bit_length() + 7) // 8, 'big')
    s = hash_f(message_bytes + x_bytes)
    s_bits = [int(c) for c in bin(int(s, 16))[2:].zfill(m)]
    t = r
    for i in range(m):
        if s_bits[i] == 1:
            t = (t * a[i]) % n
    return t, s

def fiat_shamir_verify(message, signature, pub_key, hash_f, m):
    t, s = int(signature["t"]), signature["s"]
    b, n = [int(bi) for bi in pub_key["b"]], int(pub_key["n"])
    w = fast_exp_mod(t, 2, n)
    s_bits = [int(c) for c in bin(int(s, 16))[2:].zfill(m)]
    for i in range(m):
        if s_bits[i] == 1:
            w = (w * b[i]) % n
    message_bytes = message.encode('utf-8')
    w_bytes = w.to_bytes((w.bit_length() + 7) // 8, 'big')
    s_prime = hash_f(message_bytes + w_bytes)
    return s_prime == s

def save_public_key(pub_key, filename):
    b, n = pub_key
    with open(filename, 'w') as f:
        json.dump({'b': [str(bi) for bi in b], 'n': str(n)}, f)

def save_private_key(priv_key, filename):
    a, n = priv_key
    with open(filename, 'w') as f:
        json.dump({'a': [str(ai) for ai in a], 'n': str(n)}, f)

def main():
    class MyTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            try:
                # Получение длины запроса
                length_bytes = self.request.recv(4)
                if len(length_bytes) != 4:
                    raise Exception("Не удалось прочитать длину запроса")
                request_length = int.from_bytes(length_bytes, 'big')
                request_data = b""
                while len(request_data) < request_length:
                    chunk = self.request.recv(min(1024, request_length - len(request_data)))
                    if not chunk:
                        raise Exception("Соединение прервано")
                    request_data += chunk
                request = json.loads(request_data.decode('utf-8'))
                print("Получен запрос:", request)

                signature = request["signature"]
                message = request["message"]
                hash_algorithm = request["hash_algorithm"]
                pub_key = request["pub_key"]

                # Проверка подписи клиента
                m = 256
                if not fiat_shamir_verify(message, signature, pub_key, sha256, m):
                    print("Подпись клиента не верна")
                    response = {"error": "Invalid client signature"}
                    response_b = json.dumps(response).encode('utf-8')
                    response_length = len(response_b)
                    response_length_bytes = response_length.to_bytes(4, 'big')
                    self.request.sendall(response_length_bytes)
                    self.request.sendall(response_b)
                    return

                k = 1024
                tsa_pub_key, tsa_priv_key = generate_fiat_shamir_keys(k, m)
                save_public_key(tsa_pub_key, 'tsa_public_key_15.json')
                save_private_key(tsa_priv_key, 'tsa_private_key_15.json')

                # Вычисление хеша для TSA
                s_bytes = int(signature["t"]).to_bytes((int(signature["t"]).bit_length() + 7) // 8, 'big') + bytes.fromhex(signature["s"])
                comb = message.encode('utf-8') + s_bytes
                hash_m_ = sha256(comb)

                timestamp = time.strftime("%y%m%d%H%M%SZ", time.gmtime())
                print("Временная метка:", timestamp)

                # Формирование сообщения для подписи TSA
                data_to_sign = (hash_m_ + timestamp).encode('utf-8')
                t_tsa, s_tsa = fiat_shamir_sign(data_to_sign.decode('utf-8'), tsa_priv_key, sha256, m)
                response = {
                    "timestamp": timestamp,
                    "tsa_signature": {"t": str(t_tsa), "s": s_tsa},
                    "tsa_pub_key": {"b": [str(bi) for bi in tsa_pub_key[0]], "n": str(tsa_pub_key[1])},
                    "hash_m": hash_m_
                }
                response_b = json.dumps(response).encode('utf-8')
                response_length = len(response_b)
                response_length_bytes = response_length.to_bytes(4, 'big')
                self.request.sendall(response_length_bytes)
                self.request.sendall(response_b)
                print("Сервер: Ответ отправлен успешно")
            except Exception as e:
                print(f"Ошибка на сервере: {e}")
                response = {"error": str(e)}
                response_b = json.dumps(response).encode('utf-8')
                response_length = len(response_b)
                response_length_bytes = response_length.to_bytes(4, 'big')
                self.request.sendall(response_length_bytes)
                self.request.sendall(response_b)

    server = socketserver.TCPServer(('127.0.0.1', 9090), MyTCPHandler)
    print("Сервер запущен")
    server.serve_forever()

if __name__ == "__main__":
    main()