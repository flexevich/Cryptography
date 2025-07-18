import json
import socket
from sha import * 
from RSA import *

def main():

    message = "Helli world".encode('utf-8')
    k = 1024  
    block_size = 128

    p = generate_p(k)
    q = generate_p(k)
    while q == p:
        q = generate_p(k)
    pub_key, priv_key = rsa(p, q)
    
    
    save_public_key(pub_key, 'public_key.json')
    save_private_key(priv_key, 'private_key.json')
    
    
    hash_m = sha256(message)
    print(hash_m)
    signatura = encrypt_message(hash_m, priv_key, block_size)
    print('s = ', signatura) #SignatureValue
    # s_dec = decrypt_message(s, pub_key, block_size)
    # print('s_dec = ', s_dec)
    s_byte = [s_byt.to_bytes((s_byt.bit_length() + 7) // 8, 'big') for s_byt in signatura]
    s_bytes = b''.join(s_byte)
    #print(s_bytes)
    comb = message+s_bytes
    combo = comb
    hash_m_ = sha256(combo)
    print(hash_m_)

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
            "SignatureAlgorithmIdentifier": "RSA",
            "SignatureValue": str(signatura),
            "SubjectPublicKeyInfo": {
                "e": str(pub_key[0]),  
                "n": str(pub_key[1])   
            },
            "UnsignedAttributes": {
                "ObjectIdentifier": "signature-time-stamp",
                "SET_OF_AttributeValue": ''
            }
        }
    }
    with open("client.json", "w") as file:
        json.dump(Client, file, indent=4)
    
    # s_bytes_hex = s_bytes.hex()
    message_str = message.decode('utf-8')
    # print(message_str)
    request = {
        "signature": signatura,
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
            
            timestamp = response["timestamp"]
            tsa_signature = response["tsa_signature"]
            tsa_key = response["tsa_key"]
            # print(tsa_key)
            tsa_dec = decrypt_message(tsa_signature, tsa_key, block_size)
            
            print("hash_m_: ", hash_m_)
            print("timestamp: ", timestamp)
            
            check_sign = (hash_m_ + timestamp).encode('utf-8')
            check_sign_hash = sha256(check_sign)
            
            
            if  tsa_dec != check_sign_hash:
                raise Exception("хеш в ответе не совпадает c отправленным")
            
            
            Client["SignerInfos"]["UnsignedAttributes"]["SET_OF_AttributeValue"] = {
                "timestamp": response["timestamp"],
                "tsa_signature": response["tsa_signature"],
                "tsa_key": response["tsa_key"]
            }
            # Сохраняем обновленный Client
            with open("client.json", "w", encoding="utf-8") as file:
                json.dump(Client, file, indent=4)
            print("структура Client обновлена и сохранена")
        except Exception as e:
            print(f"ошибка: {e}")
            raise

if __name__ == "__main__":
    main()