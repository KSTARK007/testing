c = 0
fo = open("users.txt","r")
k = fo.readline()
while(k != ''):
	c = k.split(":")[0]
	k = fo.readline()
print(c)
fo.close()