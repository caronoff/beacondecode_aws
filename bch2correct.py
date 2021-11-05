import bchlibcaronoff as bchlib
import decodefunctions
import bch1correct


def pdf2_to_bch2(pdf2,bch2):

    binary_data_pdf2 = newdata = pdf2.zfill(26)

    correctedbch2=bch2
    bch2=bch2+'0000'



    BCH_POLYNOMIAL = 67
    BCH_BITS = 2
    bitflips=0
    #bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
    bch=bchlib.BCH(2,prim_poly=67)
    max_data_len = bcn.n // 8 - (bch.ecc_bits + 7) // 8
    data = bytearray(bch1correct.bitstring_to_bytes(binary_data_pdf2))

    rebuildpdf2=''
    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf2=rebuildpdf2+segment


    ecc = bch.encode(data)




    # create array of ecc provide by bch
    ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bch2))
    packet=data + ecc_provided
    #
    #
    if ecc!=ecc_provided:

         data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
    #     #correct
         nerr=bch.decode(data,ecc)
         bitflips = nerr
         #bitflips = bch.decode_inplace(data,ecc)
         bch.correct(data,ecc)
         newdata=decodefunctions.dec2bin(data[0]) #.zfill(2)
         for e in data[1:]:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             newdata = newdata + binchar
    #
         correctedbch2 = '' #decodefunctions.dec2bin(ecc[0])
         for e in ecc:
             binchar = decodefunctions.dec2bin(e).zfill(8)
             correctedbch2 = correctedbch2 + binchar

    return (bitflips,newdata.zfill(26),correctedbch2[:-4])

if __name__ == "__main__":
    pdf2= input("pdf2: ")
    bch2= input("bch2: ")
    if not pdf2:

        pdf2='00010001000001010101001100'
        bch2='001000100100'

    bitflips,newpdf,newbch = pdf2_to_bch2(pdf2,bch2)
    print(pdf2)
    print(newpdf,len(newpdf))
    print(bch2)
    print(newbch)
    print(bitflips)
    if bitflips==-1:
        print('fail')

    pdf2=(decodefunctions.hextobin('D3C4EB28140AA681100A444154C224'))[82:108]
    bch2=(decodefunctions.hextobin('D3C4EB28140AA681100A444154C224'))[108:]
    print('D3C4EB28140AA681100A444154C224',pdf2,len(pdf2))
    print('bch2',bch2,len(bch2))







