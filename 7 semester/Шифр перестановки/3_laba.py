import numpy as np

def zapretgram(lett_T, list):
    res = {}
    for i in range(len(lett_T)):
        res[i] = []
        for j in range(len(lett_T)):
            if i != j:         
                for k in range(len(lett_T[0])):
                    bigram = lett_T[i][k] + lett_T[j][k]
                    if bigram in list:
                        res[i].append(j)
                        break 

    return res

def truegram(res, lett_T):
    num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11, 12 , 13, 14]
    res_ = {}
    # вывод очереди после какого столбика идет какой столбик   
    for i, j in res.items():
        res_[i] = []
        for k in num:
            if k not in j:
                if i == k:
                    continue
                else:
                    res_[i].append(k)
    print(f"res_: {res_}")
    order = []
    for i, j in res_.items():              
        for k in j:
            order.append(k)       
    print(f"oreder: {order}")
    # поиск первого столбца
    for i in order:
        for k in num:
            if k not in order:
                start = k
                print(f"k = {k}")
        break
    # составление правильной очереди столбцов
    order_new = [start]
    next_values = start

    for i in range(len(num)):
        if not res_[next_values]:
            break
        values_ord = res_[next_values][0]
        order_new.append(values_ord) 
        next_values = values_ord
        # i += 1
        
    print(f"order_new: {order_new}")
    # перемещение столбцов согласно очереди
    old_lett = lett_T
    new_lett = []
    for i in order_new:
        new_lett.append(old_lett[i])
    
    # print(new_lett)                
    lett = np.transpose(new_lett)
    # for i in lett:
    #     print(i)
    return lett
                

def read_file(filename):
    letters = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line_ = line.strip()
            if  line_:   
                letters.append(list(line_.lower()))
    lett_T = np.transpose(letters)
    for i in letters:
        print(i)
    print(lett_T)
    
    
    return lett_T 

def write_file(filename, text):
    k = 0
    with open(filename, 'w', encoding='utf-8') as file:
        for i in text:
            for j in i:
                file.write(j)
            file.write("\n")
            

def main():
    list = {'аь', 'еь', 'ёь', 'иь', 'оь', 'уь', 'ыь', 'эь', 'юь', 'яь', ' ь', 'бй', 'вй', 'гй', 'дй', 'жй', 'зй', 'йй', 'кй', 'лй', 'мй', 'нй', 'пй', 'рй', 'сй', 'тй', 'фй', 'хй', 'цй', 'чй', 'шй', 'щй', ' й'}
    lett_T = read_file("3_laba.txt")
    res = zapretgram(lett_T, list)
    print(f"res: {res}")
    res_ = truegram(res, lett_T)
    
    write_file("3_laba_dec.txt", res_)
    
    
if __name__ == "__main__":
    main()