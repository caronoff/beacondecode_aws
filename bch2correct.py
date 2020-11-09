import bchlib
import decodefunctions
import bch1correct


def pdf2_to_bch2(pdf2,bch2):
    #valid pdf1
    binary_data_pdf2 = newdata = pdf2

    correctedbch2=bch2
    bch2=bch2+'0000'
    #print('valid pdf1',len(binary_data_pdf1),binary_data_pdf1)


    BCH_POLYNOMIAL = 67   #137
    BCH_BITS = 2
    bitflips=0
    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
    data = bytearray(bch1correct.bitstring_to_bytes(binary_data_pdf2))

    rebuildpdf2=''
    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf2=rebuildpdf2+segment
        print(e, data[e],segment)

    print(binary_data_pdf2)
    print(rebuildpdf2,len(rebuildpdf2),binary_data_pdf2==rebuildpdf2)

    ecc = bch.encode(data)
    print('computed ecc bytes:',len(ecc))
    bchstring = ''

    for e in ecc:
        binchar = decodefunctions.dec2bin(e).zfill(8)
        print(e, binchar)
        bchstring = bchstring + binchar
    print(bchstring)
    print(bch2)

    # create array of ecc provide by bch
    ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bch2))
    packet=data + ecc_provided
    bchstr2=''
    print(len(data),len(ecc),len(packet))
    print('ecc included:',ecc_provided,len(ecc_provided),type(ecc_provided))
    print('ecc calc:', ecc,len(ecc),type(ecc))

    #
    #
    #
    if ecc!=ecc_provided:

         data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
    #     #correct
         bitflips = bch.decode_inplace(data,ecc)
         print('bitflips: %d' % (bitflips))
         newdata=decodefunctions.dec2bin(data[0])
         for e in data[1:]:
             binchar = decodefunctions.dec2bin(e).zfill(8)
    #         #print(e, binchar)
             newdata = newdata + binchar
    #
         correctedbch2 = '' #decodefunctions.dec2bin(ecc[0])
         for e in ecc:
             binchar = decodefunctions.dec2bin(e).zfill(8)
    #         #print(e, binchar)
             correctedbch2 = correctedbch2 + binchar
         if (len(correctedbch2))>12:
             correctedbch2=correctedbch2[:12]
    return (bitflips,newdata,correctedbch2)

if __name__ == "__main__":
    pdf2= input("pdf2: ")
    bch2= input("bch2: ")
    if not pdf2:

        pdf2='11010000000111000110000000'
        bch2='111011000110'

    bitflips,newpdf,newbch = pdf2_to_bch2(pdf2,bch2)
    print(pdf2)
    print(newpdf)
    print(bch2)
    print(newbch)
    print(bitflips)
    if bitflips==-1:
        print('fail')

    pdf2=(decodefunctions.hextobin('93CB0242508F3BC928BCB407180EC6'))[82:108]
    bch2=(decodefunctions.hextobin('93CB0242508F3BC928BCB407180EC6'))[108:]
    #print('93CB0242508F3BC928BCB407180EC6',pdf2,len(pdf2))
    #print('bch2',bch2,len(bch2))







