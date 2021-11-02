import decodefunctions as Fcn
import Gen2functions as sgb
import random
import decodehex2



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

def random_error(hexvalid,pdf1err,pdf2err,sgberr):
    #pdf1/bc1 errors correctible 3
    #pdf2/bc2 errors correctible 2
    scramble=list( Fcn.hextobin(hexvalid))
    #print(scramble)
    b=Fcn.hextobin(hexvalid)
    if pdf1err or pdf2err:
        for i in range(pdf1err):
            epos=random.randint(0,81)

            scramble[epos] = str(int(not int(scramble[epos])))

        for j in range(pdf2err):
            epos = random.randint(82, 119)

            scramble[epos] = str(int(not scramble[epos]))
    elif sgberr:
        for i in range(sgberr):
            epos = random.randint(0, 251)
            scramble[epos] = str(int(not int(scramble[epos])))


    return  Fcn.bin2hex(''.join(scramble))

preamble='000000000000000000101111'
short_long='1'
user_location='1'
countrycode='0100111100'  #316 - Canada

def fgb(f,r):
    for n in range(r):
        ident=randombinary(49)
        while ident[:4]=='101' and user_location=='1':

            ident=randombinary(49)

        pdf1=preamble+short_long+user_location+countrycode+ident
        bch1= Fcn.calcbch(('_'+pdf1+'0'*59), "1001101101100111100011", 25, 86, 107)
        newbin=pdf1+bch1

        supdata=randombinary(26)

        bch2=''
        try:
            bch2 = Fcn.calcbch('_'+newbin+supdata+'0'*12, '1010100111001', 107, 133, 145)
        except IndexError:
            print('error')
            print(len('_'+newbin+supdata+'0'*12))
        finalbin=newbin+supdata+bch2

        hexcheck=Fcn.bin2hex(finalbin[24:])

        f.write(random_error(hexcheck,random.randint(0,4),random.randint(0,3),0)+'\n')



def sgbcompute(f,r):
    for n in range(r):
        pdf = randombinary(202).zfill(202)

        bchcalc= sgb.calcBCH( pdf + '0'*48, 0, 202, 250)

        finalbin = (pdf+bchcalc).zfill(252)

        hex = Fcn.bin2hex(finalbin)

        f.write(random_error(hex, 0,0, random.randint(0, 8)) + '\n')




if __name__ == "__main__":
    f = open('samplehex.csv', 'a')
    sgbcompute(f,500)
    f.close()
