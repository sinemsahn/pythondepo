def sum(number_one,number_two):
    number_one_int = convert_integer(number_one)
    number_two_int = convert_integer(number_two)
    result = number_one_int + number_two_int
    return result
def convert_integer(number_string):
    converted_integer = int(number_string)
    return converted_integer
answer = sum("1","2")
print(answer)
#f9 ile debug koyabiliyorsun
#f5 ile çalıştırabiliyorsun ve stack dataya bakalım
#stack data barı ile aşağıdan değişkenleri local ve global olarak görebilirsin

#bulamadım ama debug proble ile o andaki değerleri değiştirebiiyorsun

#wingide hem geliştirmek hemde debug işlemlerinde bize kolaylık sağlar