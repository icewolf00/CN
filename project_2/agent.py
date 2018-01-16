import socket  
import time
import numpy as np
import sys
import random

ip_s2a = sys.argv[1]
ip_a2r = sys.argv[2]
port_s2a = int(sys.argv[3])
port_a2s = int(sys.argv[4])
port_a2r = int(sys.argv[5])
port_r2a = int(sys.argv[6])
THRESHOLD = float(sys.argv[7])

# ip_s2a = '127.0.0.1'
# ip_a2r = '127.0.0.1'
# port_s2a = 31500
# port_a2s = 31501
# port_r2a = 31503
# port_a2r = 31502
# THRESHOLD = float(sys.argv[1])

address_s2a = (ip_s2a, port_s2a)
address_a2s = (ip_s2a, port_a2s)
address_r2a = (ip_a2r, port_r2a)
address_a2r = (ip_a2r, port_a2r)

s_s2a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_a2s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_r2a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_a2r =	socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_s2a.bind(address_s2a)
s_s2a.setblocking(0)
s_r2a.bind(address_r2a)
s_r2a.setblocking(0)
packet_num = 0
drop_num = 0
come_in = 0
come_ack = 0
loss_rate = 0.0000
got_type = 0

while True:
	if got_type == 0:
		try:
			data, haha = s_s2a.recvfrom(1024)
			if data[0:9] == b'FILE_TYPE':
				print("get	type")
				s_a2r.sendto(data, address_a2r)
				print("fwd	type")
				try:
					data, haha = s_r2a.recvfrom(20)
					if data == b'FILE_TYPE ACK':
						print("get	typeack")
						s_a2s.sendto(data, address_a2s)
						print("fwd	typeack")
						got_type += 1
				except socket.error:
					continue
				# print("send_type")
		except socket.error:
			continue
	try:
		data, haha = s_s2a.recvfrom(1024)
		# data = data.decode('utf-8')
		if data == b'FINISH':
			print("get	fin")
			s_a2r.sendto(data, address_a2r)
			print("fwd	fin")
			time.sleep(0.1)
			data, haha = s_r2a.recvfrom(20)
			if data == b'FINISHACK':
				print("get	finack")
				s_a2s.sendto(data, address_a2s)
				print("fwd	finack")
			break
		if data[0:6] == b'Packet':
			number, haha = data.split(b',', 1)
			number = number.decode('utf-8')
			number = number[6:]
			print("get	data	#" + str(number))
			packet_num += 1
			random_num = random.random()
			if random_num < THRESHOLD:
				drop_num += 1
				loss_rate = drop_num / packet_num
				print("drop"+ "	data	#"+str(number)+",	loss rate = ", str(loss_rate))
			else:
				come_in += 1
				s_a2r.sendto(data, address_a2r)
				print("fwd	data	#" + str(number))
	except socket.error:
		while come_ack < come_in:
			try:
				data, haha = s_r2a.recvfrom(20)
				data = data.decode('utf-8')
				if data[0:3] == "ACK":
					print("get"+"	ack"+"	#" + data[3:])
					message = bytes(data, encoding = 'utf-8')
					s_a2s.sendto(message, address_a2s)
					print("fwd"+"	ack"+"	#" + data[3:])
					come_ack += 1
			except socket.error:
				pass
		come_in = 0
		come_ack = 0
		# for i in range(come_in):
		# 	data, haha = s_r2a.recvfrom(20)
		# 	data = data.decode('utf-8')
		# 	if data[0:3] == "ACK":
		# 		print("get"+"	ack"+"	#" + data[3:])
		# 		message = bytes(data, encoding = 'utf-8')
		# 		s_a2s.sendto(message, address_a2s)
		# 		print("fwd"+"	ack"+"	#" + data[3:])
		# come_in = 0

