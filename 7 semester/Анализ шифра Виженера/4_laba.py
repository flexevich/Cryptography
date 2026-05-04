import json

def rotate(coll, n):
    rot = coll[n:] + coll[:n]
    return rot


def chi_2(coll_1, coll_2):
    sum = 0
    for i in range(30):
        coll1 = coll_1[i]
        coll2 = coll_2[i]
        
        if coll2 > 0:
            sum += pow(coll1 - coll2, 2 ) / coll2
    return sum

# поиск сдвига относительно первого столбца
def find_rotr(data):

    all_rotate = [0]
    for j in range(2, 18):
        d = 0
        chi_min = 10000000000000000000
        for i in range(30):
            rot_data = rotate(data[f'{j}'], i)
            chi = chi_2(data['1'], rot_data)
            if chi < chi_min:
                chi_min = chi
                d = i
        all_rotate.append(d)

    return all_rotate


# нахождение абсолютного сдвига 
def find_true_rotate(data, list_alph, find_rotr):

    d = 0
    chi_min = 10000000000000000000
    
    for i in range(30):
        rot_data = rotate(data['1'], i)
        chi = chi_2(list_alph, rot_data)
        if chi < chi_min:
            chi_min = chi
            d = i
            
    gamma = []

    for i in range(17):
        y = (d + find_rotr[i]) % 30
        gamma.append(y)


    return gamma


# визуализация сдигов
def rotr_pms(gamma, pms):  

    rotr_pms = []
    print(f"")
    for i in range(1, 17):
        ro = pms[f'{i}']
        k = rotate(ro, gamma[i-1])
        rotr_pms.append(k)

    for i, j in enumerate(rotr_pms, 1):
        print(f"Столбец {i}: {j}")



# дешивровка
def dec(let_, letters, gamma):

    num_letters = []
    for i, r in enumerate(letters):
        for j, k in enumerate(let_):
            if r == k:
                num_letters.append(j)
                break

    p = []
    for i, t in enumerate(num_letters):
        # print(f"{i}: {t}")
        j = i % len(gamma)
        p_i = (t - gamma[j]) % 30
        p.append(p_i)
    # print(p)
    _letters = []

    for i, r in enumerate(p):
        for j, k in enumerate(let_):
            if r == j:
                _letters.append(k)
                break

    return _letters

def read_file(filename, alph):

    letters = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line_ = line.strip()
            for let in line_:
                if let.upper() in alph:   
                    letters.append(let.upper())
    return letters

    

def read_json(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def main():

    let_ = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ь', 'Ы', 'Э', 'Ю', 'Я']
    letters = read_file("C:\\Users\\chere\\PyProjects\\Cryptography\\Crypt_2\\4_laba\\2.TXT", let_)
    pms = read_json("C:\\Users\\chere\\PyProjects\\Cryptography\\Crypt_2\\4_laba\\PMS.json")
    list_alph  = [62, 14, 38, 13, 25, 72, 7, 16, 72, 28, 35, 26, 53, 90, 23, 40, 45, 53, 21, 2, 9, 4, 12, 6, 4, 14, 16, 3, 6, 18]    
    # print(letters[:55])
    # print("")
    # print(list_letters)


    # for i, j in data.items():
    #     print(f"Столбец {i}: {j}")
    # find_rotr(data)

    # res = chi_2(data['1'], data['2'])
    # print(res)

    res_ = find_rotr(pms)
    print(f" ")
    print("Сдвиг относительно первого столбца: ", res_)
    gamma = find_true_rotate(pms, list_alph, res_)
    print("Абсолютный сдвиг gamma:", gamma) 
    # print("Абсолютный сдвиг gamma_test: ", gamma_test)
    rotr_pms(gamma, pms)                                                     
    print(f" ")

    dec_ = dec(let_, letters, gamma)
    
    for i in range(0,500, 17):
        print(''.join(dec_[i:i+17]))
    # 4600
    # gamma2 = gamma_test * (len(letters) // 17)
    # print(gamma2)
    # print(rotate(pms['1'], 19))
    # print(rotate(pms['2'], 7))
        # print(data['1'])
    # print(rotate(data['2'], 18))

if __name__ == "__main__":

    main()