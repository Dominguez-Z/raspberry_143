import chardet

y = '\xe4\xb8\x89\xe4\xb8\x83\xe4\xbc\xa4\xe8\x8d\xaf\xe7\x89\x87'
yy = y.encode("latin-1")
yyy = yy.decode("utf8")
print(yy)
print(yyy)
