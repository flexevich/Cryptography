import struct

def rotr(x, n, bits):

    right_shift = x >> n
    left_shift = x << (bits - n)
    combined = right_shift | left_shift
    mask = (1 << bits) - 1
    result = combined & mask
    return result

def sha256_padding(message):
    message = bytearray(message)  
    orig_len = len(message) * 8
    message.append(0x80)
    while (len(message) * 8 + 64) % 512 != 0:
        message.append(0)
    message += struct.pack('>Q', orig_len)
    return message

def sha512_padding(message):
    message = bytearray(message)
    orig_len = len(message) * 8
    message.append(0x80)
    while (len(message) * 8 + 128) % 1024 != 0:
        message.append(0)
    message += struct.pack('>QQ', orig_len >> 64, orig_len & 0xFFFFFFFFFFFFFFFF)
    return message

def sha256(message):

    H = [
        0x6a09e667, 0xbb67ae85,
        0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c,
        0x1f83d9ab, 0x5be0cd19
    ]
    K256 = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]
    message = sha256_padding(message)

    for i in range(0, len(message), 64):
        w = list(struct.unpack('>16L', message[i:i+64]))
        for j in range(16, 64):
            s0 = rotr(w[j-15], 7, 32) ^ rotr(w[j-15], 18, 32) ^ (w[j-15] >> 3)
            s1 = rotr(w[j-2], 17, 32) ^ rotr(w[j-2], 19, 32) ^ (w[j-2] >> 10)
            w.append((w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF)

        a, b, c, d, e, f, g, h = H

        for j in range(64):
            S1 = rotr(e, 6, 32) ^ rotr(e, 11, 32) ^ rotr(e, 25, 32)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h + S1 + ch + K256[j] + w[j]) & 0xFFFFFFFF
            S0 = rotr(a, 2, 32) ^ rotr(a, 13, 32) ^ rotr(a, 22, 32)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFF

        H = [(x + y) & 0xFFFFFFFF for x, y in zip(H, [a, b, c, d, e, f, g, h])]

    return ''.join(f'{h:08x}' for h in H)

def sha512(message):
    H = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f, 
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]
    K = [
        0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817,
    ]

    message = sha512_padding(message)
    
    for i in range(0, len(message), 128):
        w = list(struct.unpack('>16Q', message[i:i+128]))
        for j in range(16, 80):
            s0 = rotr(w[j-15], 1, 64) ^ rotr(w[j-15], 8, 64) ^ (w[j-15] >> 7)
            s1 = rotr(w[j-2], 19, 64) ^ rotr(w[j-2], 61, 64) ^ (w[j-2] >> 6)
            w.append((w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFFFFFFFFFF)
        a, b, c, d, e, f, g, h = H
    
        for j in range(80):
            S1 = rotr(e, 14, 64) ^ rotr(e, 18, 64) ^ rotr(e, 41, 64)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (h + S1 + ch + K[j] + w[j]) & 0xFFFFFFFFFFFFFFFF
            S0 = rotr(a, 28, 64) ^ rotr(a, 34, 64) ^ rotr(a, 39, 64)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFFFFFFFFFF

            h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFFFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFFFFFFFFFF
        H = [(x + y) & 0xFFFFFFFFFFFFFFFF for x, y in zip(H, [a, b, c, d, e, f, g, h])]
    return ''.join(f'{h:016x}' for h in H)
    
def main():
    print("Выберите алгоритм:")
    print("1 - SHA-256")
    print("2 - SHA-512")
    algo = input(">>> ")
    data = input("Введите строку: ")

    if algo == '1':
        print("SHA-256: ", sha256(data.encode('utf-8')))
    else:
        print("SHA-512: ", sha512(data.encode('utf-8')))

        

if __name__ == "__main__":
    main()
