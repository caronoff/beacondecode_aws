import bchlib
import decodefunctions
import bch1correct
from Gen2functions import calcBCH


def pdf_to_bchsgb(pdf,bchsgb):

    binary_data_pdf = newdata =  pdf.zfill(204)
    print(len(binary_data_pdf))
    correctedbch=bchsgb
    bchsgb=bchsgb


    BCH_POLYNOMIAL = 285 #285
    BCH_BITS = 6
    bitflips=0
    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

    max_data_len = bch.n // 8 - (bch.ecc_bits + 7) // 8

    data = bytearray(bch1correct.bitstring_to_bytes(binary_data_pdf))
    print('len in bytes of data',len(data))
    print('m------------:', bch.m)


    print('ecc_bits: {}  ecc_bytes:  {} '.format(bch.ecc_bits,bch.ecc_bytes))
    print('m:', bch.m)
    print('n: {}  bytes: {}'.format(bch.n,bch.n // 8 ))
    print('max data length:', max_data_len)
    print('t: {}'.format(bch.t))
    print('length of data in bytes:', len(data))
    rebuildpdf=''
    print('---Per Byte'+'-' * 40)
    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf=rebuildpdf+segment
        print(e, data[e],segment)
    print('-'*50)
    print('pdf as input',len(pdf),pdf)
    print('bch as input', len(bchsgb),bchsgb)
    print('-' * 50)
    rebuildpdf=rebuildpdf.zfill(202)
    print(rebuildpdf,len(rebuildpdf))

    print(binary_data_pdf==rebuildpdf)
    print('inputed data len to encode bch: ',len(data))

    ecc = bch.encode(data)

    print('computed ecc bytes:',len(ecc))
    bchstring = ''

    for e in ecc:
        binchar = decodefunctions.dec2bin(e).zfill(8)
        print(e, binchar)
        bchstring = bchstring + binchar

    print(bchsgb)
    print(bchstring)
    print(bchsgb==bchstring)
    print(decodefunctions.bin2hex(rebuildpdf+bchstring))
    # create array of ecc provide by bch
    ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bchsgb))
    print(ecc)
    print('ecc included:',ecc_provided,len(ecc_provided),type(ecc_provided))
    print('ecc calc:', ecc,len(ecc),type(ecc))
    print('provided',bchsgb,len(bchsgb),decodefunctions.bin2hex(bchsgb))
    print('calculated',bchstring,len(bchstring),decodefunctions.bin2hex(bchstring))
    packet = data + ecc_provided
    print('ecc equiv',ecc==ecc_provided )

    if ecc!=ecc_provided:
         data, ecc = packet[1:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
         print('cropped len data',len(data))
         #data, ecc = packet[:-6], packet[-6:]
         print(data,ecc)
         bitflips =  bch.decode_inplace(data,ecc)
         print('bitflips: %d' % (bitflips))
         newdata=pdf[:4] #decodefunctions.dec2bin(byte_one)
         for e in data:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             newdata = newdata + binchar    #
         correctedbch = ''
         for e in ecc:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             correctedbch = correctedbch + binchar
    return (bitflips,newdata.zfill(204),correctedbch[:48])

def test_hex(testhex):

    pdf = decodefunctions.hextobin(testhex)[:204]
    print(pdf)
    print(len(pdf))
    bch = (decodefunctions.hextobin(testhex))[204:]

    print(bch, len(bch))

    bitflips, newpdf, newbch = pdf_to_bchsgb(pdf, bch)
    print('errors result: ', bitflips)
    if bitflips == -1:
        print('fail')
    elif bitflips == 0:
        print('match')
    elif bitflips > 0:
        print(20 * '-' + 'ORIGINAL MESSAGE' + 25 * '-')
        print(testhex)
        print(20 * '-' + 'CORRECTED MESSAGE' + 25 * '-')
        print(decodefunctions.bin2hex(newpdf + newbch))

        print(newpdf + newbch)

def make_full(hexinput):
    pdf1=decodefunctions.hextobin(hexinput)
    b= pdf1[:204]+ '0' *48
    print(b,len(b))
    ecc=calcBCH(b,0,202,250)
    newhex=decodefunctions.bin2hex(pdf1[:204]+ecc)
    print(newhex)
    print(ecc,decodefunctions.bin2hex(ecc))
    BCH_POLYNOMIAL = 285  # 285
    BCH_BITS = 6
    bitflips = 0
    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

    max_data_len = bch.n // 8 - (bch.ecc_bits + 7) // 8

    data = bytearray(bch1correct.bitstring_to_bytes(pdf1[:204]))
    necc = bch.encode(data)
    bchstring = ''

    for e in necc:
        binchar = decodefunctions.dec2bin(e).zfill(8)
        bchstring = bchstring + binchar
    print(bchstring,decodefunctions.bin2hex(bchstring))

    newhex =decodefunctions.bin2hex(pdf1[:204]+bchstring)

    return newhex


if __name__ == "__main__":
    # testhex='0039823D32618658622811F0000000000003FFF004030680258492A4FC57A49'
    testhex = '80001D63A50FF83E0FFFC1FE06FB6000002FFFF1FFFFFFF060075A5E14ADEC3'
    # '0039823D32618658622811F0000000000003FFF004030680258F7158700E5F1'
    ######## 0039823D32618658622811f0000000000003FFF004030680258F7158700E5F1
    # 039823D32618658622811F0000000000003FFF004030680258F7158700E5F1
    # testhex='0039823D32618658622811F0000000000003FFF004030680258'
    # per T018 '0039823D32618658622811F0000000000003FFF004030680258492A4FC57A49'
    testhex='3fFF2D63A50FF43E0FFFC1FE06FB6000002FFFF1FFFFFFF0600CC54D4E99993'
    testhex = '0139823D32618658622811F0000000000003FFF004030680258492A4FC57A49'
    testhex='2139823D32618658622811F0000000000003FFF004030680258307EB09F236e'
    t='1139823D32618658622811F0000000000003FFF004030680258194DF35C70A8'


    testhex = '3fFF2D63A50FF43E0FFFC1FE06FB6000002FFFF1FFFFFFF0600CC54D4E99993'
    test_hex(t)


    a='3fff2D63A50FF43E0FFFC1FE06FB6000002FFFF1FFFFFFF060075A5E14ADEC3'
    a='1139823D32618658622811F0000000000003FFF004030680258492A4FC57A49'
    #print(len(a))
    h=make_full(a)
    #print(h)





