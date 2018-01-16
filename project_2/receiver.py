import socket  
import time
import numpy as np
import sys
BUFFER_SIZE = 32

buffer_read = ["" for i in range(BUFFER_SIZE)]

ip_a2r = sys.argv[1]
port_a2r = int(sys.argv[2])
port_r2a = int(sys.argv[3])
file_dir = sys.argv[4]

address = (ip_a2r, port_a2r)  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
s.bind(address)

address2 = (ip_a2r, port_r2a)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

buffer_count = 0
head = 1
next = 1
got = np.zeros((BUFFER_SIZE, 1))

file_out = 0

while True:
	data, haha = s.recvfrom(1024)
	# data = data.decode('utf-8')
	# print(data)
	if data[0:9] == b'FILE_TYPE':
		print("recv" + "	" + "type")
		data = data.decode('utf-8')
		name, file_type = data.split(",", 1)
		file_out = open(file_dir + "result."+file_type, "wb")
		message = "FILE_TYPE ACK"
		message = bytes(message, encoding = 'utf-8')
		s2.sendto(message, address2)
		print("send" + "	" + "typeack")
		# print("got_type")
		# print(data)
		continue

	if data == b'FINISH':
		print("recv" + "	" + "fin")
		message = "FINISHACK"
		message = bytes(message, encoding = 'utf-8')
		s2.sendto(message, address2)
		print("send" + "	" + "finack")
		for i in range(buffer_count):
			file_out.write(buffer_read[i])
		print("flush")
		break
		
	if data[0:6] == b'Packet':
		number, data = data.split(b',', 1)
		number = number.decode('utf-8')
		number = number[6:]
		if int(number) != next:
			if next == 1:
				continue
			print("drop" + "	" + "data" + "	" + "#" + number)
			message = "ACK" + str(next - 1)
			message = bytes(message, encoding = 'utf-8')
			s2.sendto(message, address2)
			print("send" + "	" + "ack" + "	" + "#" + str(next - 1))

		else:
			if buffer_count == 32:
				print("drop" + "	" + "data" + "	" + "#" + number)
				message = "ACK" + str(next - 1)
				message = bytes(message, encoding = 'utf-8')
				s2.sendto(message, address2)
				print("send" + "	" + "ack" + "	" + "#" + str(next - 1))
				for i in range(32):
					file_out.write(buffer_read[i])
				buffer_count = 0
				print("flush")
				continue

			print("recv" + "	" + "data" + "	" + "#" + number)
			buffer_read[buffer_count] = data
			buffer_count += 1
			message = "ACK" + str(next)
			message = bytes(message, encoding = 'utf-8')
			s2.sendto(message, address2)
			print("send" + "	" + "ack" + "	" + "#" + str(next))
			next += 1

s.close()