from decodefunctions import getFiveCharChecksum
from random import randint
import definitions
country = open('countries.csv')

midlist=[]
for line in country.readlines():
    mid = int(line.split(',')[0].rstrip())
    midlist.append(mid)
baudotlist = []
for key in definitions.baudot:
    baudotlist.append(key)

hexchars='ABCDEF0123456789'

def realrandom23hex():
    mid = midlist[randint(0, len(midlist) - 1)]
    midbin = definitions.dec2bin(mid, 10)
    tac = definitions.dec2bin(randint(0, 65535), 16)
    sn = definitions.dec2bin(randint(0, 16383), 14)
    vesselID = ['000', '001', '010', '011', '100', '101'][randint(0, 5)]
    if vesselID == '000':
        # no vessel ID
        IdBits = vesselID + '0' * 44
    elif vesselID == '001':
        # Maritime MMSI
        mmsi = int(str(mid) + str(randint(0, 999999)))
        IdBits = vesselID + definitions.dec2bin(mmsi, 30) + definitions.dec2bin(randint(0, 9999), 14)
    elif vesselID == '010' or vesselID == '011':
        # radio callsign or Aircraft marking
        IdBits = vesselID
        for i in range(7):
            r = randint(0, len(baudotlist) - 1)
            IdBits = IdBits + baudotlist[r]
        IdBits = IdBits + '00'

    elif vesselID == '100':
        # aircraft 24 bit
        add24 = randint(0, 16777215)
        IdBits = vesselID + definitions.dec2bin(add24, 24) + 20 * '0'

    elif vesselID == '101':
        # aircraft operator and serial number
        IdBits = vesselID
        for i in range(3):
            r = randint(0, len(baudotlist) - 1)
            IdBits = IdBits + baudotlist[r]
        IdBits = IdBits + definitions.dec2bin(randint(0, 4095), 12) + 14 * '1'

    return definitions.bin2hex('1' + midbin + '101' + tac + sn + '0' + IdBits)


def collisions(limitrealhex,testperhex, randomchar,collisionfile,testedfile,infile=''):


if __name__ == "__main__":
    hexchars='ABCDEF0123456789'
    randhexdic={}
    checksumdic={}
    user_input3 = raw_input('Enter how many actual real hex to test :')
    limittest=int(user_input3)
    user_input1 = raw_input('Enter number of characters to randomize :')
    randchar=int(user_input1)
    user_input2 = raw_input('Enter tests per sample :')
    testpersample=int(user_input2)

    writefile= open('sgbhexcollision.txt',"w")
    infile=open('test23uin.csv',"r")
    realhexfile=open('test23uintested.csv',"w")

    j=0
    collisions=0
    while(1):

        if j == limittest:
            break
        #for lines in range(j): #infile(10000) buffersize specified:
        for lines in infile.readlines(10000):
            if j % 100 == 0:
                print('Tested {} unique ids out of {} total '.format(j, limittest))
            #realhex=realrandom23hex()
            realhex=infile.readline().strip()
            #print('\n'+realhex)
            realhexfile.write('\n'+realhex)
            if j<limittest:
                j+=1
                realchecksum = getFiveCharChecksum(realhex)
                randomhex = []
                collision = []
                i=0
                while i < testpersample:
                    randposlist=[]

                    while len(randposlist) < randchar :
                        randpos = randint(0, len(realhex)-1)
                        if randpos not in randposlist:
                            randposlist.append(randpos)
                    newhex=realhex
                    for randpos2 in randposlist:
                        hexchar = hexrandom = realhex[randpos2]
                        while hexchar==hexrandom:
                            hexrandom = hexchars[(randint(0,15))]
                        if randpos2 == 0:
                            newhex = hexrandom + newhex[1:]
                        elif randpos2 == len(realhex)-1:
                            newhex = newhex[:-1] + hexrandom
                        else:
                            newhex = newhex[0:randpos2] + hexrandom + newhex[randpos2+1:]

                    if realchecksum ==getFiveCharChecksum(newhex) and realhex!=newhex:
                        collision.append((newhex,realhex))
                        writefile.write(':'.join(( '\n\nActual    ',    realhex, realchecksum,   '\nCollision ', newhex , getFiveCharChecksum(newhex)        )))
                        collisions+=1
                        #print( newhex,getFiveCharChecksum(newhex),realhex,realchecksum)
                    i += 1

                # for posno,char in enumerate(realhex[:-1]):
                #     newhex = realhex[0:posno] + realhex[posno:posno+2][::-1] + realhex[posno+2:]
                #    if realchecksum == getFiveCharChecksum(newhex) and realhex!=newhex:
                #        collision.append((newhex,realhex))
                #       writefile.write(':'.join(( '\n\nActual    ',    realhex, realchecksum,   '\nCollision ', newhex , getFiveCharChecksum(newhex)        )))
                #       collisions+=1
                #       print( newhex,getFiveCharChecksum(newhex),realhex,realchecksum)
        #
        # user_input = raw_input('Tested {} unique ids. Type STOP to quit, otherwise press the Enter/Return key '.format(j) )
        # if user_input == 'STOP' or j==limittest:



    #print(i)
    #print(len(checksumdic),i,(i-len(checksumdic))/float(i))
    print(j)
    writefile.write('\n\nUnique SGB tested: '+str(j)+ '  Collisions: '+ str(collisions)+'    Randomize Char : '+str(randchar)+'     Test per sample: ' + str(testpersample))
    infile.close()
    writefile.close()
    realhexfile.close()
