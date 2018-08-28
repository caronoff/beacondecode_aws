import decodefunctions as Fcn
import random
import decodehex2
decoded=open('samplehex.csv','w')


def randombinary(l):
    binstr = ''
    for i in range(l):
        x = random.random()
        if x < .5:
            b = '0'
        else:
            b = '1'

        binstr = binstr + b
    return binstr


preamble='000000000000000000101111'

short_long='1'
user_location='1'
countrycode='0100111100'  #316 - Canada


for n in range(10000):

    ident=randombinary(49)
    pdf1=preamble+short_long+user_location+countrycode+ident
    bch1= Fcn.calcbch(('_'+pdf1+'0'*59), "1001101101100111100011", 25, 86, 107)
    newbin=pdf1+bch1
    supdata=randombinary(26)
    bch2 = Fcn.calcbch('_'+newbin+supdata+'0'*12, '1010100111001', 107, 133, 145)
    finalbin=newbin+supdata+bch2
    # print(Fcn.bin2hex(finalbin))
    hexcheck=Fcn.bin2hex(finalbin)
    if decodehex2.BeaconFGB(hexcheck).errors==[]:
        decoded.write(hexcheck+'\n')
decoded.close()
