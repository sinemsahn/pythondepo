import socket

target_host="0.0.0.0"
target_port = 9999

#yeni socket objesi olusturulu
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#clienta baglanmak icin
client.connect((target_host,target_port))

#biraz veri data yolla
client.send("ABCDEF")
#client("GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

#donen veriyi al
response = client.recv(4096)

print response
