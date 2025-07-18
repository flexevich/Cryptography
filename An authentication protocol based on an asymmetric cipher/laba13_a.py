import socket
import json
import sys
from sha import *
from rsa import *

# Константы
IP = '127.0.0.1'
PORT = 65432
ID_A = 123784

def start_client():
    # Генерация случайного значения z
    z = str(generate_p(512))
    hash_z = sha256(z.encode())
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Подключение к серверу
            s.connect((IP, PORT))
            print("Подключено к серверу")
            
            # 1. Получение публичного ключа
            pubkey_data = s.recv(4096)
            if not pubkey_data:
                print("Публичный ключ не получен")
                sys.exit(1)
                
            
            pubkey_json = json.loads(pubkey_data.decode('utf-8'))
            pub_key = (int(pubkey_json['pub_key'][0]), int(pubkey_json['pub_key'][1]))
            print(f"Получен публичный ключ: {pub_key}")
            
            
            # 2. Шифрование (z || ID_A)
            temp_data = {
                "z": z,
                "IdA": str(ID_A)
            }
            temp_data_enc = json.dumps(temp_data)
            ciphertext = encrypt_message(temp_data_enc, pub_key, 32)
            
            # 3. Формирование и отправка данных
            data_to_send = {
                "hash": hash_z,
                "ID_A": str(ID_A),
                "cipher": ciphertext
            }
            
            print("\nОтправляемые данные:")
            print(f"Хэш z: {hash_z}")
            print(f"ID_A: {ID_A}")
            print(f"Шифротекст: {ciphertext}")
            
            s.sendall(json.dumps(data_to_send).encode('utf-8'))
            print("Данные успешно отправлены")
            
            # 4. Получение z обратно и проверка
            response = s.recv(4096)
            if not response:
                print("Ответ не получен")
                sys.exit(1)
            
            try:
                msg = json.loads(response.decode('utf-8'))
                if "error" in msg:
                    print(f"Ошибка сервера: {msg['error']}")
                    sys.exit(1)
                
                z_returned = msg.get("z")
                print(f"\nПолучено z от сервера: {z_returned}")
                
                if z_returned == z:
                    print("z совпадает. Идентификация успешна")
                else:
                    print("z не совпадает! Идентификация провалена")
                    
            except Exception as e:
                print(f"Ошибка обработки ответа: {e}")
                sys.exit(1)
                
        except Exception as e:
            print(f"Ошибка соединения: {e}")
            sys.exit(1)

if __name__ == "__main__":
    start_client()