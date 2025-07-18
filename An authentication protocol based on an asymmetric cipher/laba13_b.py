import socket
import json
import sys
from sha import *
from rsa import *

# Константы
IP = '127.0.0.1'
PORT = 65432
ID_A = 123784

def start_server():
    """Запускает серверную часть протокола идентификации"""
    # Генерация ключей RSA
    p = generate_p(512)
    q = generate_p(512)
    n = p * q
    pub_key, priv_key = rsa(p, q)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
        try:
            # Привязка и ожидание подключения
            stream.bind((IP, PORT))
            stream.listen()
            print("Сервер ожидает подключения...")
            
            conn, addr = stream.accept()
            with conn:
                print(f"Подключено: {addr}")
                
                # 1. Отправка публичного ключа
                request = {
                    "pub_key": [str(pub_key[0]), str(pub_key[1])]  # Преобразование чисел в строки для JSON
                }
                request_b = json.dumps(request).encode('utf-8')
                conn.sendall(request_b)
                print(f"Отправлен публичный ключ: {pub_key}")
                
                # 2. Получение данных от клиента
                data = conn.recv(8192)
                if not data:
                    print("Данные не получены")
                    return
                
                try:
                    msg = json.loads(data.decode('utf-8'))
                    hash_z_recv = msg["hash"]
                    id_a_open = str(msg["ID_A"])
                    ciphertext = msg["cipher"]
                    
                    print("\nПолученные данные:")
                    print(f"Хэш z: {hash_z_recv}")
                    print(f"ID_A (открытый): {id_a_open}")
                    print(f"Шифротекст: {ciphertext}")
                    
                    # 3. Расшифровка и проверка
                    z_a_str = decrypt_message(ciphertext, priv_key, 32)
                    z_a_dict = json.loads(z_a_str)
                    z_dec, id_a_enc = z_a_dict["z"], z_a_dict["IdA"]
                    
                    print(f"\nРасшифрованные данные:")
                    print(f"z: {z_dec}")
                    print(f"ID_A: {id_a_enc}")
                    
                    # Проверка ID
                    if id_a_open != id_a_enc or id_a_open != str(ID_A):
                        print("ID_A не совпадает")
                        return
                    
                    # Проверка хэша
                    if sha256(z_dec.encode()) == hash_z_recv:
                        print("Хэш z проверен. Отправка z обратно.")
                        conn.sendall(json.dumps({"z": z_dec}).encode('utf-8'))
                    else:
                        print("хэш z не совпадает")
                        
                except Exception as e:
                    print(f"Ошибка обработки данных: {e}")
                    
        except Exception as e:
            print(f"Ошибка сервера: {e}")

if __name__ == "__main__":
    start_server()