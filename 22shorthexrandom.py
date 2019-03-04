import random
import definitions
from decodehex2 import Bch
country = open('countries.csv')
codes = open('test22short.csv', 'w')
midlist=[]
binary='01'
for line in country.readlines():
    mid = int(line.split(',')[0].rstrip())
    midlist.append(mid)


for h in range(100):
    binary='0'+'0'*24+'01'
    mid=midlist[random.randint(0,len(midlist)-1)]
    midbin=definitions.dec2bin(mid,10)
    binary=binary+midbin
    userprotbinary=definitions.dec2bin(str(random.randint(0,7)),3)
    userprotocoltext=definitions.userprottype[userprotbinary]
    userprotbinary = '001'
    if userprotbinary=='000':
        # Orbitography
        identification=''
        for i in range(46):
            identification=identification+str(random.randint(0, 1))



        bintemp=binary+'000'+identification+83*'0'



        bch=Bch(bintemp,'Short Msg')
        bch1=bch.bch[0]
        binary = binary + '000' + identification + bch1


    elif userprotbinary=='001':
        # 'ELT Aviation user'
        identification=''
        baudotlist = []
        IdBits = ''
        for key in definitions.baudot:
            baudotlist.append(key)
        for i in range(7):
            r = random.randint(0, len(baudotlist) - 1)
            IdBits = IdBits + baudotlist[r]
        binary=binary+'010'+IdBits+'0000'
        bintemp=binary+83*'0'
        bch = Bch(bintemp, 'Short Msg')
        bch1 = bch.bch[0]
        binary = binary +  bch1


    elif userprotbinary == '010':
        # Maritime user'
        identification = ''
        baudotlist = []
        IdBits = ''
        for key in definitions.baudot:
            baudotlist.append(key)
        for i in range(7):
            r = random.randint(0, len(baudotlist) - 1)
            IdBits = IdBits + baudotlist[r]
        binary = binary + '001' + IdBits + '0000'
        bintemp = binary + 83 * '0'
        bch = Bch(bintemp, 'Short Msg')
        bch1 = bch.bch[0]
        binary = binary + bch1

    binary=binary + str(random.randint(0, 1)) + str(random.randint(0, 1)) + str(random.randint(0, 1))+ str(random.randint(0, 1))+ str(random.randint(0, 1))+ str(random.randint(0, 1))


    hex22=definitions.bin2hex(binary)
    codes.write(hex22+'\n')
codes.close()

