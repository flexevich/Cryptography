import random
import string
from sha import *
from streebog import *


def generate_key(block_size, filename='key.txt'):
    characters = string.ascii_letters + string.digits
    rand_len = random.randint(1, block_size)
    key = ''.join(random.choice(characters) for _ in range(rand_len))
    key_bytes = key.encode('utf-8')
    with open(filename, 'w') as f:
        f.write(key)
    return key_bytes

def read_key(filename='key.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return bytes.fromhex(f.read().strip())
    except (FileNotFoundError, ValueError):
        return generate_key(filename)
    
def hmac(key, message, hash_f, block_size): 
    if len(key) < block_size:
        key += b'\x00' * (block_size - len(key))      
    ipad = b'\x36' * block_size
    opad = b'\x5c' * block_size
    key_ipad = bytes(a ^ b for a, b in zip(key, ipad))
    key_opad = bytes(a ^ b for a, b in zip(key, opad))
    
    # hash(key_ipad || message)
    inner_hash = hash_f(key_ipad + message.encode('utf-8'))
    inner_hash_bytes = bytes.fromhex(inner_hash)

    outer_hash = hash_f(key_opad + inner_hash_bytes)
    return outer_hash

def main():
    print("Выберите алгоритм:")
    print("1 - SHA-256")
    print("2 - SHA-512")
    algo = input(">>> ")
    data = input("Введите строку: ")

    if algo == '1':
        key = generate_key(64, 'key.txt')
        print("SHA-256: ", sha256(data.encode('utf-8')))
        print("HMAC:", hmac(key, data, sha256, 64))
    else:
        key = generate_key(128, 'key.txt')
        print("SHA-512: ", sha512(data.encode('utf-8')))
        print("HMAC:", hmac(key, data, sha512, 128))
        

if __name__ == "__main__":
    main()