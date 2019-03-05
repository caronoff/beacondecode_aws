import random
import definitions
country = open('countries.csv')
codes = open('test23uin.csv', 'w')
midlist=[]
for line in country.readlines():
    mid = int(line.split(',')[0].rstrip())
    midlist.append(mid)


for h in range(10000):

    mid=midlist[random.randint(0,len(midlist)-1)]
    midbin=definitions.dec2bin(mid,10)
    tac=definitions.dec2bin(random.randint(0,65535),16)
    sn=definitions.dec2bin(random.randint(0,16383),14)
    vesselID=['000','001','010','011','100','101'][random.randint(0,5)]
    if vesselID=='000':
        #no vessel ID
        IdBits=vesselID+'0'*44
    elif vesselID=='001':
        #Maritime MMSI
        mmsi=int(str(mid)+str(random.randint(0,999999)))
        IdBits=vesselID+definitions.dec2bin(mmsi,30)+definitions.dec2bin(random.randint(0,9999),14)
    elif vesselID=='010' or vesselID=='011':
        # radio callsign or Aircraft marking
        baudotlist=[]
        IdBits=vesselID
        for key in definitions.baudot:
            baudotlist.append(key)
        for i in range(7):
            r=random.randint(0,len(baudotlist)-1)

            IdBits=IdBits+baudotlist[r]
        IdBits=IdBits+'00'

    elif vesselID=='100':
        # aircraft 24 bit
        add24=random.randint(0,16777215)
        IdBits=vesselID+definitions.dec2bin(add24,24)+20*'0'


    elif vesselID=='101':
        # aircraft operator and serial number
        baudotlist = []
        IdBits = vesselID
        for key in definitions.baudot:
            baudotlist.append(key)
        for i in range(3):
            r = random.randint(0, len(baudotlist)-1)
            IdBits = IdBits + baudotlist[r]
        IdBits=IdBits + definitions.dec2bin(random.randint(0,4095),12) + 14* '1'



    uin='1'+midbin+'101'+tac+sn+'0'+IdBits
    hex23=definitions.bin2hex(uin)
    codes.write(hex23+'\n')
codes.close()

