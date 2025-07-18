import json
import socket
import time
from sha import * 
from ElGamal import *

def main():

    message = "Helli world".encode('utf-8')
    k = 1024  
    block_size = 128
    p, a, alpha, b = generate(k)
    pub_key = (p, alpha, b)
    priv_key = (a)
    
    # save_encrypted_PublicKey(pub_key, 'public_key_el.json')
    # save_encrypted_PrivateKey(priv_key, 'p rivate_key_el.json')
    
    
    hash_m = sha256(message)
    print("hash_m: ", hash_m)
    p_minus_1 = p - 1
    while True:
        k = random.randint(1, p_minus_1)
        g, _, _ = euclidean_algorithm(k, p_minus_1)
        if g == 1:
            break
    # Хеш сообщения
    hash_m = int.from_bytes(bytes.fromhex(sha256(message)), 'big')
    
    # Вычисление r = alpha^k mod p
    r = fast_exp_mod(alpha, k, p)
    
    # Вычисление мультипликативного обратного k по модулю p-1
    g, x, _ = euclidean_algorithm(k, p_minus_1)
    if g != 1:
        raise ValueError("Обратное число не существует")
    
    # Вычисление s = k^(-1) * (H(m) - a * r) mod (p-1)
    k_inv =  x % p_minus_1

    s = (k_inv * (hash_m - a * r)) % (p - 1)
    signatira = (r, s)
    print(signatira)
    
    # s_byte = [c_byt.to_bytes((c_byt.bit_length() + 7) // 8, 'big') for c_byt in c]
    # s_bytes = b''.join(s_byte)
    # byte_array = b''
    # for inner_tuple in c:  # Итерируемся по внешнему кортежу
    #     for num in inner_tuple:  # Итерируемся по числам во вложенном кортеже
    #         # Определяем минимальную длину байтов
    #         byte_length = (num.bit_length() + 7) // 8
    #         # Преобразуем число в байты (big-endian)
    #         byte_array += num.to_bytes(byte_length, byteorder='big')

    # print("byte_array: ", byte_array)
    # print("s_bytes: ",byte_array)
    # comb = message+byte_array
    # combo = comb
    # hash_m_ = sha256(combo)
    # print("hash_m_: ",hash_m_)

    Client = {
        "CMSVersion": "1",
        "DigestAlgorithmIdentifiers": "SHA-256",
        "EncapsulatedContentInfo": {
            "ContentType": "text/plain",
            "OCTET STRING":str(message.decode('utf-8', errors='replace'))
        },
        "SignerInfos": {
            "CMSVersion": "1",
            "SignerIdentifier": "Cherenkov",
            "DigestAlgorithmIdentifiers": "SHA-256",
            "SignatureAlgorithmIdentifier": "Elgamal",
            "SignatureValue": str(signatira),
            "SubjectPublicKeyInfo": {
                "p": str(pub_key[0]),  
                "alpha": str(pub_key[1]),
                "b": str(pub_key[2])  
            },
            "UnsignedAttributes": {
                "ObjectIdentifier": "signature-time-stamp",
                "SET_OF_AttributeValue": ''
            }
        }
    }
    with open("client_8.json", "w") as file:
        json.dump(Client, file, indent=4)
    
    # c_bytes_hex = byte_array.hex   ()
    message_str = message.decode('utf-8')
    # print(message_str)
    request = {
        "signatura": signatira,
        "message": message_str,
        "hash_algorithm": "SHA-256",
        "pub_key": pub_key
    }
    
    request_b = json.dumps(request).encode('utf-8')
    
    print(request_b) 
     
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
        stream.settimeout(5.0)
        try:
            stream.connect(('127.0.0.1', 4567))
            # Отправка запроса
            request_length = len(request_b)
            request_length_bytes = request_length.to_bytes(4, 'big')
            stream.sendall(request_length_bytes)
            stream.sendall(request_b)
            print("запрос отправлен успешно")
            # Чтение ответа от сервера
            # Читаем длину ответа (4 байта)
            length_bytes = stream.recv(4)
            if len(length_bytes) != 4:
                raise Exception("не удалось прочитать длину ответа")
            response_length = int.from_bytes(length_bytes, 'big')
            # Читаем сам ответ
            response_data = b""
            while len(response_data) < response_length:
                chunk = stream.recv(min(1024, response_length - len(response_data)))
                response_data += chunk
            # Декодируем и парсим ответ
            response_str = response_data.decode('utf-8')
            response = json.loads(response_str)
            print("ответ от TSA:", response)
            
            hash_from_serv = response["hash"]
            timestamp = response["timestamp"]
            r_serv, s_serv = response["tsa_signature"]
            p_serv, alpha_serv, b_serv = response["tsa_key"]

            # print(tsa_key)
            hash_m_1 = int.from_bytes(bytes.fromhex(hash_from_serv), 'big')
            # print(hash_m_1)
            print("timestamp: ", timestamp)
            p1 = fast_exp_mod(alpha_serv, hash_m_1, p_serv)
            p2 = (fast_exp_mod(b_serv, r_serv, p_serv) * fast_exp_mod(r_serv, s_serv, p_serv)) % p_serv
            # print(p1)
            # print(p2)
            if p1 == p2:
                print("подпись верна ")
            else:
                raise ValueError("подпись не верна")
            
            
            
            # Обновляем Client
            Client["SignerInfos"]["UnsignedAttributes"]["SET_OF_AttributeValue"] = {
                "hash": response["hash"],
                "timestamp": response["timestamp"],
                "tsa_signature": response["tsa_signature"],
                "tsa_key": response["tsa_key"]
            }
            # Сохраняем обновленный Client
            with open("client_8.json", "w", encoding="utf-8") as file:
                json.dump(Client, file, indent=4)
            print("структура Client обновлена и сохранена")
        except Exception as e:
            print(f"ошибка: {e}")
            raise

if __name__ == "__main__":
    main()