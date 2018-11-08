import csv
import math
from random import randint
from decodefunctions import getFiveCharChecksum
import zlib

def calcBCH(binary, b1start, b1end, b2end):
    """ Calculates the expected BCH error-correcting code for a given binary string.
    See C/S T.018 for details.

    Args:
        binary (str): binary string
        b1start (int): bit at which to start calculating
        b1end (int): bit at which to end calculating
        b2end (int): total length of bit string
    Returns:
        bchlist: calculated BCH code
    """
    f = open('bchfile2.txt', 'w')
    sout=""
    gx = '1110001111110101110000101110111110011110010010111'
    bchlist = list(binary[b1start:b1end] + '0' * (b2end - b1end))
    newrow = []
    c = 0
    first = ''.join(bchlist)
    #print(first)
    #print(len(first))
    oldgxspace = newgxspace = 0

    gxfirst = first.index('1') * ' ' + gx
    f.write("\r\nm(x):{}\r\ng(x):{}".format(first, gxfirst))
    sout="\r\nm(x):{}\r\ng(x):{}".format(first, gxfirst)
    firstone = first.index('1')
    for i in range(b1end - b1start):
        c = c + 1
        if bchlist[i] == '1':
            if c > 0:

                mx = ''.join(newrow)
                if len(mx) > 0:
                    newgxspace =  mx.index('1')
                    #mx = mx + newgxspace * '0'
                    bchnew = "\r\nm(x):{}{}\r\ng(x):{}{}".format((oldgxspace + firstone) * ' ', mx + mx.index('1')*'0',
                                                         (firstone + mx.index('1') + oldgxspace) * ' ', gx)
                    newgx = (newgxspace + oldgxspace) * ' ' + gx
                    oldgxspace = newgx.index('1')
                    f.write("\r\n{} {} {}".format(str(i), str(mx.index('1')),(b2end-2) * '-'))
                    sout=sout+"\r\n{} {} {}".format(str(i), str(mx.index('1')),(b2end-2) * '-')
                    f.write(bchnew)
                    sout=sout+bchnew
            newrow = []
            for k in range(len(gx)):
                if bchlist[i + k] == gx[k]:
                    bchlist[i + k] = '0'
                    newrow.append('0')
                else:
                    bchlist[i + k] = '1'
                    newrow.append('1')


    bchfinal = ''.join(bchlist)[b1end - b2end:]
    bchfinalw = "\r\nm(x):{}{}\r\n".format('', ''.join(bchlist))
    f.write(bchfinalw)
    sout=sout+bchfinalw
    f.write("\r\nBCH code (last 48 bits.)\r\n{}\r\n{}\r\n{}".format(48*'-',bchfinal,48*'-'))
    sout=sout+'\r\nBCH code (last 48 bits.)\r\n{}\r\n{}\r\n{}'.format(48*'-',"'"+bchfinal,48*'-')
    f.close()

    return (bchfinal,sout)


def calc_checksum_two(a):
    return hex(((sum(int(a[i:i+2],16) for i in range(0, len(a), 2))%0x100)^0xFF)+1)[2:]





def getFiveCharChecksum2(bcnId15):
    returnLimit = 1048576  # used to limit the return value to a 20 bit result
    runningSumLimit = 538471  # large prime which will not cause an overflow
    constPrimVal = 3911  # small prime value that stays constant throughout
    modifierLimit = 3847  # small prime which will not cause an overflow
    modifier = 3803  # modifier, simply initialized to a prime value
    runningSum = 0  # variable to hold the running value of the checksum
    tmpLongValue = 0
    tmpLongValue2 = 0

    ## Note: int data type is 4 bytes, largest positive value is 2,147,483,647 and
    ##  all computations are designed to remain within this value (no overflows)

    for char in bcnId15[0:-1]:
        decimalValue = int(ord(char))
        tmpLongValue = int(runningSum * modifier) + (decimalValue)
        print(tmpLongValue,tmpLongValue / runningSumLimit)
        tmpLongValue2 = int((tmpLongValue / float(runningSumLimit)))        #print(tmpLongValue>2147483647,tmpLongValue2>2147483647)
        runningSum = tmpLongValue - (tmpLongValue2 * runningSumLimit)
        tmpLongValue = constPrimVal * modifier
        tmpLongValue2 = int(tmpLongValue / modifierLimit)
        modifier = tmpLongValue - (tmpLongValue2 * modifierLimit)
        #print(tmpLongValue > 2147483647, tmpLongValue2 > 2147483647)
        print(char, decimalValue, tmpLongValue2, tmpLongValue, modifier, runningSum)

    # on last character here use the higher resolution result as input to final truncation

    decimalValue = int(ord(bcnId15[-1]))
    tmpLongValue = int(runningSum * modifier) +(decimalValue)
    tmpLongValue2 = int(tmpLongValue / returnLimit)
    runningSum = tmpLongValue - (tmpLongValue2 * returnLimit)
    print(bcnId15[-1], decimalValue, tmpLongValue2, tmpLongValue, modifier, runningSum)

    return hex(runningSum)[2:].upper().zfill(5)


if __name__ == "__main__":
    #b4 = '0000000000001110011010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000011111111111111111000000000100000000110000011010000000001001011000'
    #b2DecT018 = '000001001100100110100000000000011100110100011110111000000000000000000000000000000000000000000000111000110000011001110100011001000101000000010010010111111111111000000000100000000110000011001100000001001011011'
    #b3 = '000000000000000001110011010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000011111111111111111000000000100000000110000011010000000001001011000'
    #b5 = '000000000000000001111101000011011110101100100010001011010000000000000000001010000000000000000000010000100001111100111011010100111000000110111111111111111111111000000001000000011001000001101111111111000101100'
    #b6 = '0000000000001111101000011011110101100100010001011010000000000000000001010000000000000000000010000100001111100111011010100111000000110111111111111111111111000000001000000011001000001101111111111000101100'

    #print(calcBCH(b6, 0, 202, 250))
    #print(calc_checksum_two('00300005000'))
    #print(getFiveCharChecksum('ADCE02A8FC4106D'))
    hexchars='ABCDEF0123456789'
    #print(zlib.crc32('ADCE02A8FC4106D'))
    #print(hex(zlib.crc32('A7947889C7B80000E000001')))
    randhexdic={}
    checksumdic={}
    randchar=3
    testpersample=1000
    limittest=10000
    writefile= open('fgbhex.txt',"w")
    infile=open('fgbuser.txt',"r")


    c='ACCE09A52C41C0D'
    print(getFiveCharChecksum(c))
    j=0
    collisions=0
    for rh in infile:
        realhex=rh.strip()

        if len(realhex)==15 and j<limittest:
            j+=1

            if j%1000==0:
                print(j)
            realchecksum = getFiveCharChecksum(realhex)


            randomhex = []
            collision = []
            i=0
            while i < testpersample:

                randposlist=[]

                while len(randposlist) < randchar :
                    randpos = randint(0, 14)
                    if randpos not in randposlist:
                        randposlist.append(randpos)

                newhex=realhex
                for randpos2 in randposlist:
                    hexchar = hexrandom = realhex[randpos2]

                    while hexchar==hexrandom:
                        hexrandom = hexchars[(randint(0,15))]


                    if randpos2 == 0:
                        newhex = hexrandom + newhex[1:]
                    elif randpos2 == 14:
                        newhex = newhex[:-1] + hexrandom
                    else:
                        newhex = newhex[0:randpos2] + hexrandom + newhex[randpos2+1:]
                    #print(randpos)

                randomhex.append(newhex)

                if realchecksum ==getFiveCharChecksum(newhex):
                    collision.append((newhex,realhex))
                    writefile.write(':'.join(( '\n\nActual    ',    realhex, realchecksum,   '\nCollision ', newhex , getFiveCharChecksum(newhex)        )))
                    collisions+=1
                    print( newhex,getFiveCharChecksum(newhex),realhex,realchecksum)
                i += 1
                #print(getFiveCharChecksum(newhex))

                #print(realhex,len(realhex))
                #checksumdic[checksum] = hex




    #print(i)
    #print(len(checksumdic),i,(i-len(checksumdic))/float(i))
    print(j)
    writefile.write('\n\nUnique FGB tested: '+str(j)+ '  Collisions: '+ str(collisions)+'    Randomize Char : '+str(randchar)+'     Test per sample: ' + str(testpersample))
    infile.close()
    writefile.close()
    '''
    for i in range(10):
        randomhex = ''
        for d in range(15):
            randomhex=randomhex+hexchars[(randint(0,16))]
        #checksumdic[str(zlib.crc32(randomhex))]=randomhex
        checksumdic[str(getFiveCharChecksum(randomhex))] = randomhex
    print(len(checksumdic))
    '''


