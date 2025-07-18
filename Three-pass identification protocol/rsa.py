import random
import json

def euclidean_algorithm(x, y):
    a_2 = 1; a_1 = 0
    b_2 = 0; b_1 = 1
    while y != 0:
        q = x // y
        r = x - q * y
        a = a_2 - q * a_1
        b = b_2 - q * b_1
        x = y; y = r
        a_2 = a_1; a_1 = a
        b_2 = b_1; b_1 = b
    m = x; a = a_2; b = b_2
    return m, a, b

def miller_rabin(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(5):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_p(k):
    while True:
        p = random.getrandbits(k)
        p = p | (1 << k - 1)
        p = p | 1
        if miller_rabin(p):
            return p

def pudding(message, block_size):
    last_block = message[-1]
    pad_len = block_size - len(last_block)
    if pad_len == 0:
        pad = bytes([block_size] * block_size)
        message.append(pad)
    else:
        pad = bytes([pad_len] * pad_len)
        message[-1] = last_block + pad
    return message

def fast_exp_mod(a, n, m):
    x = 1
    while n > 0:
        if n & 1:
            x = (x * a) % m
        a = (a * a) % m
        n = n >> 1
    return x

def remove_padding(message, block_size):
    last_block = message[-1]
    pad_len = last_block[-1]
    last_block_unpadded = last_block[:-pad_len]
    message[-1] = last_block_unpadded
    return message

def rsa(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    while True:
        e = random.randint(2, phi - 1)
        g, _, _ = euclidean_algorithm(e, phi)
        if g == 1:
            break
    a, _, _ = euclidean_algorithm(e, phi)
    while a != 1:
        e += 2
    while True:
        g, a, _ = euclidean_algorithm(e, phi)
        if g == 1:
            d = a % phi
            break
        e += 2
    pub_key = (e, n)
    priv_key = (d, n)  
    return pub_key, priv_key

def encrypt(message, pub_key):
    e, n = pub_key
    message_int = int.from_bytes(message, 'big')
    encrypted_int = fast_exp_mod(message_int, e, n)
    return encrypted_int

def decrypt(encrypted_int, priv_key):
    d, n = priv_key  
    decrypted_int = fast_exp_mod(encrypted_int, d, n)
    decrypted_message = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, 'big')
    return decrypted_message

def split_into_blocks(message, block_size):
    return [message[i:i+block_size] for i in range(0, len(message), block_size)]

def encrypt_message(message, pub_key, block_size):
    message_by = message.encode('utf-8')
    split = split_into_blocks(message_by, block_size)
    msg_pud = pudding(split, block_size)
    encrypted_blocks = [encrypt(block, pub_key) for block in msg_pud]
    return encrypted_blocks

def decrypt_message(encrypted_blocks, priv_key, block_size):
    decrypted_blocks = [decrypt(block, priv_key) for block in encrypted_blocks]
    decrypted_bytes = b''.join(decrypted_blocks)
    split_blocks = split_into_blocks(decrypted_bytes, block_size)
    del_pud = remove_padding(split_blocks, block_size)
    decrypted_message = b''.join(del_pud).decode('utf-8', errors='replace')
    return decrypted_message

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(str(data))

def read_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        return int(content)

def save_encrypted_message(ciphertext, filename):
    encrypted_message = {
        "Version": 0,
        "EncryptedContentInfo": {
            "ContentType": "text",
            "ContentEncryptionAlgorithmIdentifier": "RSAEncryption",
            "encryptedContent": ciphertext,
            "OPTIONAL": {}
        }
    }
    with open(filename, 'w') as file:
        json.dump(encrypted_message, file, indent=4)

def load_encrypted_message(filename):
    with open(filename, 'r') as file:
        encrypted_message = json.load(file)
    ciphertext = encrypted_message["EncryptedContentInfo"]["encryptedContent"]
    return ciphertext

def save_private_key(priv_key, filename):
    d, n = priv_key
    key = {
        "RSAPrivateKey": {
            "privateExponent": d,
            "modulus": n
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)

def save_public_key(pub_key, filename):
    e, n = pub_key
    key = {
        "RSAPublicKey": {
            "publicExponent": e,
            "modulus": n
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)

def load_private_key(filename):
    with open(filename, 'r') as file:
        key = json.load(file)
    priv_key = (key["RSAPrivateKey"]["privateExponent"], 
                key["RSAPrivateKey"]["modulus"])
    return priv_key

def load_public_key(filename):
    with open(filename, 'r') as file:
        key = json.load(file)
    pub_key = (key["RSAPublicKey"]["publicExponent"], 
               key["RSAPublicKey"]["modulus"])
    return pub_key