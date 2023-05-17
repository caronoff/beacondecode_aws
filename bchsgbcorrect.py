#import bchlibcaronoff
#import bchlib
import decodefunctions
import bch1correct

import os


def test63hex():
    data = bytearray(b'\x03' + os.urandom(25))
    bch = bchlibcaronoff.BCH(6, m=8, prim_poly=285)
    ecc = bch.encode(data)
    rebuildpdf=''

    for e in data:
        segment=decodefunctions.dec2bin(e).zfill(8)
        rebuildpdf=rebuildpdf+segment

    rebuildbch=''
    for e in ecc:
        segment = decodefunctions.dec2bin(e).zfill(8)
        rebuildbch = rebuildbch + segment

    b=rebuildpdf+rebuildbch
    #print(decodefunctions.bin2hex(b))
    return decodefunctions.bin2hex(b)




def correct_bchsgb(testhex):

    pdf=decodefunctions.hextobin(testhex)[:204]
    bchsgb=(decodefunctions.hextobin(testhex))[204:]
    binary_data_pdf = newdata = pdf.zfill(204)
    correctedbch=bchsgb

    BCH_POLYNOMIAL = 285
    BCH_BITS = 6
    bitflips=0

    bch = bchlibcaronoff.BCH(BCH_BITS,m=8, prim_poly=BCH_POLYNOMIAL)
    max_data_len = bch.n // 8 - (bch.ecc_bits + 7) // 8 + 1
    data = bytearray(bch1correct.bitstring_to_bytes(binary_data_pdf))
    rebuildpdf=''

    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf=rebuildpdf+segment

    rebuildpdf=rebuildpdf.zfill(204)
    ecc = bch.encode(data)
    bchstring = ''

    for e in ecc:
        binchar = decodefunctions.dec2bin(e).zfill(8)
        bchstring = bchstring + binchar


    ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bchsgb))



    packet=data + ecc_provided



    if ecc!=ecc_provided:

         data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
         bch.data_len = max_data_len
         nerr = bch.decode(data, ecc)


         bitflips = nerr
         bch.correct(data, ecc)


         newdata=decodefunctions.dec2bin(data[0])
         for e in data[1:]:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             newdata = newdata + binchar

         newdata=newdata.zfill(204)
         correctedbch = ''
         for e in ecc:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             correctedbch = correctedbch + binchar
         newhex=decodefunctions.bin2hex(newdata + correctedbch)
    else:
        bitflips=0
        newdata=pdf
        correctedbch=bchsgb
        newhex=decodefunctions.bin2hex(pdf+bchsgb)


    return (bitflips,newdata,correctedbch,newhex)

if __name__ == "__main__":
    testhex='070F7A27F0FF9E3E723EF1120EDE4BC2EC888C9DA5051D117B6658205CE7363'
    #'0039823D32618658622811F0000000000003FFF004030680258F7158700E5F1'
    ######## 0039823D32618658622811f0000000000003FFF004030680258F7158700E5F1
    #039823D32618658622811F0000000000003FFF004030680258F7158700E5F1
    #testhex='0039823D32618658622811F0000000000003FFF004030680258'
    # per T018 '0039823D32618658622811F0000000000003FFF004030680258492A4FC57A49'
    testhex='3601a10E612E756CB5721DDAC483D85879A00DC1E1EDA6FB8BC382811E9CA72'



    bitflips,newpdf,newbch,newhex = correct_bchsgb(testhex)
    print('errors result: ',bitflips)
    if bitflips == -1:
        print('fail')
    elif bitflips == 0:
        print('match')
        print(newhex)
        print(testhex)
    else:
        print('corrected errors')
        print(newhex)
        print(testhex)

    #print(test63hex())
