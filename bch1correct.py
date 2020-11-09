import bchlib
import decodefunctions




def byte_to_binary(binarray):
    s=''
    for b in binarray:
        s=s+decodefunctions.dec2bin(b)
    return s


def bitstring_to_bytes2(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) +7) // 8, byteorder='big')

def pdf1_to_bch1(pdf1,bch1):
    #valid pdf1
    binary_data_pdf1 = newdata= pdf1

    correctedbch1=bch1
    bch1=bch1+'000'
    #print('valid pdf1',len(binary_data_pdf1),binary_data_pdf1)


    BCH_POLYNOMIAL = 137   #137
    BCH_BITS = 3
    bitflips=0
    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
    data = bytearray(bitstring_to_bytes(binary_data_pdf1))
    print('m:',bch.m)
    rebuildpdf=''
    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf=rebuildpdf+segment
        print(e, data[e],segment)

    #print(binary_data_pdf1)
    print(rebuildpdf,len(rebuildpdf),binary_data_pdf1==rebuildpdf)
    ecc = bch.encode(data)
    print(len(ecc))
    bchstring = ''
    for e in ecc:
        binchar = decodefunctions.dec2bin(e)
        print(e, binchar)
        bchstring = bchstring + binchar


    # create array of ecc provide by bch
    ecc_provided = bytearray(bitstring_to_bytes(bch1))
    packet=data + ecc_provided
    bchstr2=''
    print(len(data),len(ecc),len(packet))
    print('ecc included:',ecc_provided,len(ecc_provided),type(ecc_provided))
    print('ecc calc:', ecc,len(ecc),type(ecc))
    print('match',ecc==ecc_provided)



    if ecc!=ecc_provided:
        #packet = data + ecc
        data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
        #correct
        bitflips = bch.decode_inplace(data,ecc)
        print('bitflips: %d' % (bitflips))
        newdata=decodefunctions.dec2bin(data[0])
        for e in data[1:]:
            binchar = decodefunctions.dec2bin(e).zfill(8)
            #print(e, binchar)
            newdata = newdata + binchar

        correctedbch1 = ''
        for e in ecc:
            binchar = decodefunctions.dec2bin(e).zfill(8)
            #print(e, binchar)
            correctedbch1 = correctedbch1 + binchar
        if (len(correctedbch1)) > 21:
            correctedbch1 = correctedbch1[:21]


    return (bitflips,newdata,correctedbch1)

if __name__ == "__main__":
    pdf1= input("pdf1: ")
    bch1= input("bch1: ")
    if not pdf1:
        pdf1='1001001111001011000000100100001001010000100011110011101111001'
        bch1='001001010001011110010'

    bitflips,newpdf,newbch = pdf1_to_bch1(pdf1,bch1)
    print(pdf1)
    print(newpdf,len(newpdf))
    print
    print(bch1)
    print(newbch,len(newbch))
    print(bitflips)
    if bitflips==-1:
        print('fail')

    pdf1=(decodefunctions.hextobin('93CB0242508F3BC928BCB407180EC6'))[:61]
    bch1=(decodefunctions.hextobin('93CB0242508F3BC928BCB407180EC6'))[61:82]
    #print('93CB0242508F3BC928BCB407180EC6',pdf1,len(pdf1))
    #print('bch1',bch1,len(bch1))










