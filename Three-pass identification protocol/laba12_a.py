import socket
import json
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from rsa import *

# Константы
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

def start_client():
    #Запускает клиентскую часть протокола идентификации
    # Генерация случайного ключа
    key = ''.join([str(random.randint(0, 1)) for _ in range(128)])
    msg1 = input("Enter mess1: ")
    value_a = generate_p(512)

    Data = {
        "message": msg1,
        "key": key,
        "valueA": value_a,
        "ID1": ID_A
    }
    
    print("\nОтправляемые данные:")
    print(f"Ключ: {key}")
    print(f"сообщение: {msg1}")
    print(f"ID1: {ID_A}")
    print(f"Значение: {value_a}")
    
    # Отправка данных и получение ответа
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(Data).encode('utf-8'))
        
        response = s.recv(4096)
        if not response:
            print("Ответ не получен")
            return
        
        try:
            result = json.loads(response.decode('utf-8'))
            print("\nПолучен ответ от сервера:")
            print(f"Открытое сообщение: {result['open message4']}")
            
            if 'encode message3' in result:
                decrypted = aes_decrypt(key, result['encode message3'])
                decrypted_data = json.loads(decrypted)
                msg3 = decrypted_data['message 3']
                id2 = decrypted_data['ID2']
                value_a_ = decrypted_data['value_a']
                value_b_ = decrypted_data['value_b']
                print("Расшифрованные данные ответа:")
                print(f"Сообщение 3: {msg3}")
                print(f"ID отправителя: {id2}")
                print(f"Значение: {value_a_}")
                print(f"Значение: {value_b_}")
                if value_a_ != value_a and id2 != ID_B:
                    print("\nневерное velue или id_b")
                #3
                msg5 = input("Введите mess5 (открытый текст): ")
                msg4 = input("Введите mess4 (шифротекст): ")
                temp_data = {
                    "message 4": msg4,
                    "ID1": ID_A,
                    "valueA": value_a,
                    "valueB": value_b_
                }
                encoded_data = aes_encrypt(key, json.dumps(temp_data))
                data_to_send = {
                    "open message5": msg5,
                    "encode message4": encoded_data
                }
                
                # Отправка третьей части
                s.sendall(json.dumps(data_to_send).encode('utf-8'))
                print("Третья часть данных успешно отправлена")
                print("\nИдентификация прошла успешно!")
        except Exception as e:
            print(f"Ошибка обработки ответа: {e}")

if __name__ == "__main__":
    start_client()