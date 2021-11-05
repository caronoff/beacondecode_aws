import decodefunctions as Fcn
import Gen2functions as sgb
import random

import bchlib
import bch1correct

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
        for ipos in random.sample(range(0, 82), pdf1err):
            scramble[ipos] = str(int(not int(scramble[ipos])))
        for j in random.sample(range(82, 120), pdf2err):
            scramble[j] = str(int(not int(scramble[j])))

    elif sgberr:
        for i in range(int(sgberr)):
            epos = random.randint(0, 251)
            scramble[epos] = str(int(not int(scramble[epos])))


    return  Fcn.bin2hex(''.join(scramble))

preamble='000000000000000000101111'
short_long='1'
user_location='0'
countrycode='0100111100'  #316 - Canada

def fgbcompute(f,r):
    for n in range(r):
        ident=randombinary(49)
        while ident[:2]=='101' :

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

        hexvalid=Fcn.bin2hex(finalbin[24:])
        r1=3 # str(random.randint(0,4))
        r2= 3 # str(random.randint(0,3))
        hexbad=random_error(hexvalid,r1,r2,0)
        f.writelines(['{},{},{},{}'.format(hexvalid,r1,r2,hexbad),'\n'])



def sgbcompute(f,r):
    for n in range(r):
        pdf = randombinary(202).zfill(202)

        bchcalc= sgb.calcBCH( pdf + '0'*48, 0, 202, 250)

        finalbin = (pdf+bchcalc).zfill(252)

        hexvalid = Fcn.bin2hex(finalbin)

        r1 = random.randint(0, 8)

        hexbad = random_error(hexvalid, 0, 0, r1)

        f.writelines(['{},{},{}'.format(hexvalid, str(r1), hexbad), '\n'])


def samplepdf2(f,r):
    for n in range(r):
        pdf2 = randombinary(26).zfill(26)
        bch2 =  Fcn.calcbch('0'*107+pdf2, '1010100111001', 107, 133, 145) +'0000'
        bch = bchlib.BCH(67, 2)
        data = bytearray(bch1correct.bitstring_to_bytes(pdf2))
        ecc = bch.encode(data)
        bchstring=(Fcn.dec2bin(ecc[0]).zfill(8)+Fcn.dec2bin(ecc[1]).zfill(8))[:12] +'0000'
        e=random.sample(range(0,38),2)


        scramble = list(pdf2+bch2)
        for i in e:
            scramble[i] = str(int(not int(scramble[i])))
        corrupt = ''.join(scramble)


        ecc_provided=bytearray(bch1correct.bitstring_to_bytes(corrupt[26:]))
        data_provided = bytearray(bch1correct.bitstring_to_bytes(corrupt[:26]))
        ecc_c=bch.encode(data_provided)
        print(ecc_c==ecc_provided,ecc,ecc_provided)


        packet = bytearray(bch1correct.bitstring_to_bytes(corrupt[:26])) + bytearray(bch1correct.bitstring_to_bytes(corrupt[26:]))
        data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
        bitflips = bch.decode_inplace(data, ecc)
        newdata = Fcn.dec2bin(data[0]).zfill(2)
        for e in data[1:]:
            binchar = Fcn.dec2bin(e).zfill(8)
            newdata = newdata + binchar

        correctedbch2 = ''  # decodefunctions.dec2bin(ecc[0])
        for e in ecc:
            binchar = Fcn.dec2bin(e).zfill(8)
            correctedbch2 = correctedbch2 + binchar
        correctedbch2 = correctedbch2[:-4]
        bch2=bch2[:-4]
        bchstring=bchstring[:-4]

        f.writelines(['{},{},{},{},{},{},{},{}'.format(pdf2+bch2, bch2==bchstring,corrupt,len(pdf2+bch2),corrupt==pdf2+bch2,newdata+correctedbch2,newdata+correctedbch2==pdf2+bch2,bitflips), '\n'])






if __name__ == "__main__":
    f = open('samplebin2.csv', 'a')
    fgbcompute(f,250)
    #samplepdf2(f,5000)
    f.close()
