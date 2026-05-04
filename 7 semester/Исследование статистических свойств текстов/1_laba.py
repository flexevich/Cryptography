from scipy.stats import chi2
def read_file(filename, let):
    letters = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            for char in line:
                if "Ё" in char:
                    char = "Е"
                if char.upper() in  let:
                    letters.append(char.upper())
    # print(letters)
    return letters

def get_value(item):
    return item[1]

def ngram(letters, n):

    let_count = {}
    for i in range(len(letters) - n + 1):
        ngram_ = ''.join(letters[i:i+n])
        if ngram_ in let_count:
            let_count[ngram_] += 1
        else:
            let_count[ngram_] = 1
        
    return let_count


def print_ngram(ngram, filename):
    let_sorted = sorted(ngram.items(), key = get_value, reverse=True)
    with open(filename, 'w', encoding='utf-8') as file:
        for lett, count in let_sorted:
            file.write(f"{lett}: {count}\n")


def ngram_ver(ngram):
    all_ngram = 0
    for i in ngram.values():
        all_ngram +=i 
    print(all_ngram)  
    res = {}
    for i, j in ngram.items():
        res[i] = j / all_ngram
    # print(res)
    return res



def chi_2(ngram, ngram_ver_):
    all_ngram = 0
    for i in ngram.values():
        all_ngram +=i
    print(all_ngram)
    
    sum = 0

    for key, p_i in ngram_ver_.items():
        
        v_i = ngram.get(key, 0) 
        np = all_ngram * p_i 
        if np > 0:
            sum += pow((v_i - np), 2) / np
            sum1 = pow((v_i - np), 2) / np
            print(f"let = {key},v_ = {v_i}, p_ = {p_i}, sum1 = {sum1}, sum = {sum}")
    
    return sum

def main():
    let_ = {'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'}
    
    # let_3 = read_file('text.txt', let_)
    # # print(let_3)
    # let_3_count = ngram(let_3, 1)
    
    # print_ngram(let_3_count, "text____.txt")
    
    ######################################
    
    let_1 = read_file('Text_1.txt', let_)
    let_2 = read_file('Text_2.txt', let_)

    let_count_1 = ngram(let_1, 3)
    print_ngram(let_count_1, "ngram_Text_1.txt")
    ngram_ver_1 = ngram_ver(let_count_1)
    print_ngram(ngram_ver_1, "ngram_ver_Text_1.txt")
    let_count_2 = ngram(let_2, 3)
    print_ngram(let_count_2, "ngram_Text_2.txt")
    ngram_ver_2 = ngram_ver(let_count_2)
    print_ngram(ngram_ver_2, "ngram_ver_Text_2.txt")


    chi_2_ = chi_2(let_count_2, ngram_ver_1)

    all_ngram = 0
    for i in let_count_2.values():
        all_ngram +=i
    crit_chi_2 = chi2.ppf(0.95, 32**3)
    print(crit_chi_2)
    # print(pow((16984 - 967219 * 0.01405122776223784), 2) / (967219 * 0.01405122776223784))

    if chi_2_ < crit_chi_2:
        print("Верно")
    else:
        print("Не верно")  
    ######################################


if __name__ == "__main__":
    main()
        