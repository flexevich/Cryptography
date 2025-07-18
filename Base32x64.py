
base64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
base32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
def MsgToBase64(message):
    bit_msg = ''.join(format(ord(char), '08b') for char in message)
    # print(bit_msg)
    count = 0
    while len(bit_msg) % 24 != 0:
        bit_msg += '0'
        count += 1 
    # print(bit_msg)
    # print(count)
    encoded = ''
    for i in range(0, len(bit_msg), 6):
        block = bit_msg[i:i+6]
        value = int(block, 2)
        if value < len(base64):
            encoded += base64[value]
    
    count2 = count // 8
    encoded += '=' * count2
    
    print('закодирование сообщение base64:', encoded)
    return encoded   
    
def Base64ToMsg(encoded):
    count = encoded.count('=')
    result = encoded.rstrip('=')
    # print(result)
    bit_msg = ''
    for i in result:
        if i in base64:
            index = base64.index(i)
            bit_block = format(index, '06b')
            bit_msg += bit_block        
    if count == 1:
        bit_msg = bit_msg[:-8]
    elif count == 2:
        bit_msg = bit_msg[:-16]
    dec_msg = ''
    for i in range(0, len(bit_msg), 8):
        block = bit_msg[i:i+8]
        if len(block)==8:
            dec_msg += chr(int(block, 2))
    print('исходное сообщение base64: ', dec_msg)
    return(dec_msg)

############################################################

def MsgToBase32(message):
    bit_msg = ''.join(format(ord(char), '08b') for char in message)
    bit_msg_pud = bit_msg
    # print(bit_msg)
    count = 0
    # print(bit_msg)
    while len(bit_msg) % 40 != 0:
        if len(bit_msg) % 5 != 0:
            bit_msg += '0'
            count += 1 
        else:
            break
    # print(bit_msg)
    # print(count)
    encoded = ''
    for i in range(0, len(bit_msg), 5):
        block = bit_msg[i:i+5]
        value = int(block, 2)
        if value < len(base32):
            encoded += base32[value]
    if len(bit_msg_pud) % 5 == 1:
        encoded += '=' * 4
    elif len(bit_msg_pud) % 5 == 2:
        encoded += '='
    elif len(bit_msg_pud) % 5 == 3:
        encoded += '=' * 2
    elif len(bit_msg_pud) % 5 == 4:
        encoded += '=' * 3    
    
    print('закодированное сообщение base32:', encoded)
    return encoded   

def Base32ToMsg(encoded):
    count = encoded.count('=')
    result = encoded.rstrip('=')
    # print(result)
    bit_msg = ''
    for i in result:
        if i in base32:
            index = base32.index(i)
            bit_block = format(index, '05b')
            bit_msg += bit_block        
    if count == 1:
        bit_msg = bit_msg[:-4]
    elif count == 2:
        bit_msg = bit_msg[:-1]
    elif count == 3:
        bit_msg = bit_msg[:-2]
    elif count == 4:
        bit_msg = bit_msg[:-3]
    dec_msg = ''
    for i in range(0, len(bit_msg), 8):
        block = bit_msg[i:i+8]
        if len(block)==8:
            dec_msg += chr(int(block, 2))
    print('исходное сообщение base32: ', dec_msg)
    return(dec_msg)
         
    


msg = input('введите сообещние: ') 
enc = MsgToBase64(msg)
Base64ToMsg(enc)
enc32 = MsgToBase32(msg)
Base32ToMsg(enc32)
# print(enc32)