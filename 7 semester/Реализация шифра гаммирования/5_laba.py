def vernam_enc(path_file, gamma, len_gamma):
    with open(path_file, 'rb') as f:
        data = f.read()
    res = bytearray()
    for i in range(len(data)):
        j = i % len_gamma
        c = (data[i] + gamma[j]) % 256
        res.append(c)
    
    enc_file = path_file + '.enc'
    with open (enc_file, 'wb') as file:
        file.write(res)

def vernam_dec(path_file2, gamma, len_gamma):
    with open(path_file2, 'rb') as f:
        data = f.read()
    res = bytearray()
    for i in range(len(data)):
        j = i % len_gamma
        m = (data[i] - gamma[j]) % 256
        res.append(m)
    dec_file = path_file2[:-4]
    with open (dec_file, 'wb') as file:
        file.write(res)



def main():
    path_file = 'C:\\Users\\chere\\PyProjects\\Cryptography\\Crypt_2\\5_laba\\Fortnite.mp4'
    path_file2 = 'C:\\Users\\chere\\PyProjects\\Cryptography\\Crypt_2\\5_laba\\Fortnite.mp4.enc'
    
    print("1: Шифрование")
    print("2: Расшифрование")
    c = input("Выбери операцию: ")
    
    gamma = input("Введите ключ: ")
    len_gamma = len(gamma)
    gamma_b = gamma.encode('ascii')
    
    if c == '1':
        vernam_enc(path_file, gamma_b, len_gamma)
    elif c == '2':
        vernam_dec(path_file2, gamma_b, len_gamma)
if __name__ == "__main__":
    main()