input = [3, 5, 6, 1, 2, 4]


def is_number_exist(number, array):
    for element in array:
        if number == element:
            return True
    return False
    # 이 부분을 채워보세요!
    return True


result = is_number_exist(3, input)
print(result)