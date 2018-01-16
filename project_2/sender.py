import socket  
import time
import numpy as np
import sys

WINDOW_SIZE = 1
THRESHOLD = 16

ip_s2a = sys.argv[1]
port_s2a = int(sys.argv[2])
port_a2s = int(sys.argv[3])
file_name = sys.argv[4]

address = (ip_s2a, port_s2a)  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #sender to receiver

address2 = (ip_s2a, port_a2s)
s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	#receiver to sender
s2.bind(address2)
s2.setblocking(0)
# s2.settimeout(0.1)

done = 0
packet_num = 1
head = 1
time_out = 0
chunk_out = 0

read_data = []
read_data.append("********")
data_count = 0
with open(file_name, "rb") as file_read:
# with open("00.mp3", "rb") as file_read:
	while True:
		chunk = file_read.read(1000)
		if chunk:
			message = "Packet" + str(data_count + 1) + ","
			# message = message.zfill(1024)
			message = bytes(message, encoding = 'utf-8')
			message = message + chunk
			read_data.append(message)
			data_count = data_count + 1
		else:
			break

type_flag = 0
while type_flag == 0:
	send_list = np.zeros((data_count + 1, 1))
	filetype = file_name.split(".")[-1]
	message = "FILE_TYPE" + "," + filetype
	message = bytes(message, encoding = 'utf-8')
	s.sendto(message, address)
	print("send" + "	type")
	time.sleep(0.2)
	try:
		data, haha = s2.recvfrom(1024)
		data = data.decode("utf-8")
		if data == "FILE_TYPE ACK":
			print("recv" + "	typeack")
			type_flag = 1
	except socket.error:
		continue
# print("sent FILE_TYPE")
receive = np.zeros((WINDOW_SIZE, 1))
while done == 0:
	time_out = 0
	if head > data_count:
		done = 1
		break
	for i in range(WINDOW_SIZE):
		if (head + i) == (data_count):
			s.sendto(read_data[head + i], address)
			if send_list[head + i] == 0:
				print("send"+"	"+"data"+"	"+"#"+str(head+i)+",	"+"winSize = "+str(WINDOW_SIZE))
			else:
				print("resnd"+"	"+"data"+"	"+"#"+str(head+i)+",	"+"winSize = "+str(WINDOW_SIZE))
			send_list[head + i] += 1
			chunk_out = i
			done = 1
			break
		else:
			s.sendto(read_data[head + i], address)
			if send_list[head + i] == 0:
				print("send"+"	"+"data"+"	"+"#"+str(head+i)+",	"+"winSize = "+str(WINDOW_SIZE))
			else:
				print("resnd"+"	"+"data"+"	"+"#"+str(head+i)+",	"+"winSize = "+str(WINDOW_SIZE))
			send_list[head + i] += 1
	time.sleep(0.5)
	receive = np.zeros((WINDOW_SIZE, 1))
	if done == 1:
		for i in range(chunk_out + 1, WINDOW_SIZE):
			receive[i] = 1
	for i in range(WINDOW_SIZE):
		try:
			data, haha = s2.recvfrom(20)	
			if data:
				data = data.decode('utf-8')
				if(data[0:3] == "ACK"):
					print("recv"+"	ack"+"	#" + data[3:])
					if int(data[3:]) >= head:
						receive[int(data[3:]) - head] = 1
		except socket.error:
			continue

	for i in range(WINDOW_SIZE):
		if receive[i] == 0:
			# print("gg")
			THRESHOLD = max(WINDOW_SIZE/2, 1)
			THRESHOLD = int(THRESHOLD)
			print("time"+"	"+"out,	threshold = "+str(THRESHOLD))
			WINDOW_SIZE = 1
			head = head + i
			time_out = 1
			if done == 1:
				done = 0
			break
	if time_out == 1 or done == 1:
		continue
	else:
		head = head + WINDOW_SIZE
		if WINDOW_SIZE < THRESHOLD:
			WINDOW_SIZE = WINDOW_SIZE * 2
		else:
			WINDOW_SIZE = WINDOW_SIZE + 1

message = "FINISH"
message = bytes(message, encoding = 'utf-8')
s.sendto(message, address)
print("send" + "	fin")
time.sleep(0.2)
try:
	data, addr2 = s2.recvfrom(20)
	data = data.decode("utf-8")
	if data == "FINISHACK":
		print("recv" + "	finack")
except socket.error:
	pass
s.close()
s2.close()