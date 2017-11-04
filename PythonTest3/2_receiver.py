import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 8888))
while True:
    data, addr = s.recvfrom(1024)
    data = data.decode().split('\n')
    print('内容:', data[0], '时间:', data[1], "host:", addr[0], "port:", addr[1])
    if data[0].lower() == 'bye':
        break
s.close()
