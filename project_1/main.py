import socket

iplist = []
def searchip(ipnumber, loc, nodenum = 0):
	if nodenum == 3:
		ippart = ipnumber.split(".")
		for part in ippart:
			if len(part) > 1 and part[0] == "0":
				return
			if int(part) <= 255 and int(part) >= 0:
				pass
			else:
				return
		tempip = str(int(ippart[0])) + "." + str(int(ippart[1])) + "." + str(int(ippart[2])) + "." + str(int(ippart[3]))
		if tempip in iplist:
			return
		iplist.append(tempip)
		return
	if loc >= len(ipnumber):
		return
	searchip(ipnumber[:loc] + '.' + ipnumber[loc:], loc + 2, nodenum + 1)
	searchip(ipnumber, loc + 1, nodenum)


file1 = open("config", "r")
filestring = file1.readline()
CHAN = filestring.split("'")[1]
#CHAN='#CN_Demo'
HOST = "irc.freenode.net"
PORT = "6667"
NICK = "iceBot00"
IDENT = "icewolf"
REALNAME = "b04902099_bot"
anslist = ["@repeat <Message>", "@convert <Number>", "@ip <String>"]


IRCSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IRCSocket.connect(("irc.freenode.net", 6667))
IRCSocket.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
IRCSocket.send(bytes("USER %s %s haha :%s\r\n" % (IDENT, HOST, REALNAME), "UTF-8"))
IRCSocket.send(bytes("JOIN %s \r\n" % CHAN, "UTF-8"))	
Msg = "Hello! I am robot."
IRCSocket.send(bytes("PRIVMSG %s :%s\r\n" % (CHAN, Msg), "UTF-8"))

while True:
	IRCMsg = IRCSocket.recv(4094).decode()
	if not IRCMsg:
		continue
	newMsg1 = IRCMsg.split()
	newMsg = newMsg1[-2:]
	newMsg[0] = newMsg[0][1:]
	print(IRCMsg)
	outMsg = []
	if "PING" in str(IRCMsg):
		IRCSocket.send(bytes("PONG :pingis\n", "UTF-8"))
	if "@repeat" in str(IRCMsg):
		pos1 = IRCMsg.index("@repeat")
		torepeat = IRCMsg[pos1 + 8:]
		if torepeat == "":
			continue
		IRCSocket.send(bytes("PRIVMSG %s :%s" % (CHAN, torepeat), "UTF-8"))
	elif "@convert" in str(IRCMsg):
		outnumber = []
		pos2 = IRCMsg.index("@convert")
		innumber = IRCMsg[pos2 + 9:]
		innumber = innumber[:-2]
		if innumber == "":
			continue
		if innumber[:2] == "0x":
			flag = 0
			for digit in innumber[2:]:
				if digit.isdigit() != True and digit not in ["a", "b", "c", "d", "e", "f"]:
					flag = 1
					break
			if flag == 1:
				continue
			outnumber = str(int(innumber, 16))
		elif innumber.isdigit():
			outnumber = str(hex(int(innumber)))
		else:
			continue
		IRCSocket.send(bytes("PRIVMSG %s :%s\r\n" % (CHAN, outnumber), "UTF-8"))
	elif "@ip" in str(IRCMsg):
		pos3 = IRCMsg.index("@ip")
		ipnumber = IRCMsg[pos3 + 4:]
		ipnumber = ipnumber[:-2]
		if len(ipnumber) > 20:
			continue
		if len(ipnumber) > 12 or len(ipnumber) < 4 or ipnumber.isdigit() != True:
			continue
		if ipnumber == "":
			continue
		iplist = []
		searchip(ipnumber, 1, 0)		
		#iplist = list(set(iplist))
		IRCSocket.send(bytes("PRIVMSG %s :%d\r\n" % (CHAN, len(iplist)), "UTF-8"))
		for ip in iplist:
			IRCSocket.send(bytes("PRIVMSG %s :%s\r\n" % (CHAN, ip) , "UTF-8"))
	elif "@help" in str(IRCMsg):
		IRCSocket.send(bytes("PRIVMSG %s :@repeat <Message>\r\n" % CHAN, "UTF-8"))
		IRCSocket.send(bytes("PRIVMSG %s :@convert <Number>\r\n" % CHAN, "UTF-8"))
		IRCSocket.send(bytes("PRIVMSG %s :@ip <String>\r\n" % CHAN, "UTF-8"))