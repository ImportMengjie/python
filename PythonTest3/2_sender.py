import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    data = input("请输入你想发送的话:")
    localtime = time.asctime(time.localtime(time.time()))
    info = data + '\n' + localtime
    print(info)
    s.sendto(info.encode(), ('127.0.0.1', 8888))
    if 'bye' == data.lower():
        break
s.close()
