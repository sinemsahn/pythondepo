import socket 

target_host="127.0.0.1"
target_port=80

#soket objeni oluştur
client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#biraz veri yolla
client.sendto("AAABBBCCC",(target_host,target_port))

#veriiyi al
data,addr=client.recvfrom(4096)

print data
