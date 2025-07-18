import socket
import json
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from rsa import *

# Constants
ID_A = 123784
ID_B = 543217
HOST = "127.0.0.1"
PORT = 65432

def aes_encrypt(bit_key, plaintext):
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    padded_data = pad(plaintext, AES.block_size)
    cipher = AES.new(byte_key, AES.MODE_ECB)
    return cipher.encrypt(padded_data).hex()

def aes_decrypt(bit_key, ciphertext_hex):
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    cipher = AES.new(byte_key, AES.MODE_ECB)
    ciphertext = bytes.fromhex(ciphertext_hex)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size).decode('utf-8')

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Сервер ожидает подключения...")
        
        conn, addr = s.accept()
        with conn:
            print(f"Подключено: {addr}")
            data = conn.recv(4096)
            if not data:
                print("Данные не получены")
                return
            
            try:
                received_data = json.loads(data.decode('utf-8'))
                msg1 = received_data['message']
                key = received_data['key']
                value_a = received_data['valueA']
                id1 = received_data['ID1']
                
                print("\nПолученные данные:")
                print(f"Key: {key}")
                print(f"Open message1: {msg1}")
                print(f"ValueA: {value_a}")
                print(f"ID1: {id1}")
                
                # Проверка ID отправителя
                if id1 != ID_A:
                    print("Неверный ID1")
                    return
                
                # Подготовка ответа
                msg2 = input("Введите message2 (шифротекст): ")
                msg3 = input("Введите message3 (открытый текст): ")
                value_b = generate_p(512)
                temp_data = {
                    "message 2": msg2,
                    "ID2": ID_B,
                    "value_a": value_a,
                    "value_b": value_b
                }
                encoded_data = aes_encrypt(key, json.dumps(temp_data))
                
                data_to_send = {
                    "open message4": msg3,
                    "encode message3": encoded_data
                }
                
                # Отправка ответа
                conn.sendall(json.dumps(data_to_send).encode('utf-8'))
                print("Ответ успешно отправлен")
                print("\n Идентификация успешна")
                
                
                #3
                response = conn.recv(4096)
                if not response:
                    print("Третья часть не получена")
                    return
                
                result = json.loads(response.decode('utf-8'))
                print("\nПолучена третья часть от клиента:")
                print(f"Открытое сообщение: {result['open message5']}")
                
                if 'encode message4' in result:
                    decrypted = aes_decrypt(key, result['encode message4'])
                    decrypted_data = json.loads(decrypted)
                    
                    print("Расшифрованные данные третьей части:")
                    print(f"Сообщение 4: {decrypted_data['message 4']}")
                    print(f"ID1: {decrypted_data['ID1']}")
                    print(f"Значение valueA: {decrypted_data['value_a']}")
                    print(f"Значение valueB: {decrypted_data['value_b']}")
                    
                    # Проверка valueA, valueB и ID1
                    if decrypted_data['value_a'] == value_a and decrypted_data['value_b'] == value_b and decrypted_data['ID1'] == ID_A:
                        print("\nИдентификация прошла успешно!")
                    else:
                        print("\nОшибка идентификации!")
                        if decrypted_data['value_a'] != value_a:
                            print("Неверное значение valueA")
                        if decrypted_data['value_b'] != value_b:
                            print("Неверное значение valueB")
                        if decrypted_data['ID1'] != ID_A:
                            print("Неверный ID1")
                
                
            except Exception as e:
                print(f"Ошибка обработки данных: {e}")

if __name__ == "__main__":
    start_server()