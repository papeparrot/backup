input = 20

# 소수는 자기 자신과 1외에는 아무것도 나눌 수 없다. 
def find_prime_list_under_number(number):
    prime_list = []
    for n in range(2, number + 1):
        for i in range(2, n):
            if n % i == 0:
                break
        else:
            prime_list.append(n)
    return prime_list


result = find_prime_list_under_number(input)
print(result)