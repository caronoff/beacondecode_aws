import bchlib
import Gen2functions as Sgb
import decodefunctions as Fcn
import bch1correct
import os
import random
from bitarray import bitarray

def msgbits_to_bch(msgbits,bchsgb):
    print(len(msgbits))
    binary_data_msgbits = newdata =  msgbits.zfill(207)    #.zfill(204) #Msg size is 202
    correctedbch=bchsgb



    BCH_POLYNOMIAL = 463
    BCH_BITS = 6
    bitflips=0
#109,113,127,131,137,139,149,151,157,163,167,173,179,   181,    191,    193,    197,    199,    211,    223,    227,    229
    #233,    239 ,   241,    251,    257,    263,    269,    271,    277,    281
    for p in [229,233,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389, 397,401, 409, 419, 421, 431,433,439,443,449,457, 461,463, 467,    479,    487,    491,    499,    503,    509,    521,    523, 541,547,557,563,569,571,577,587,594,599,601,607]:
            #   233,    239 ,   241,    251,    257,    263,    269,    271,    277,    281,
            #   283,    293,    307,    311,    313,    317,    331,    337,    347,    349,
            #   353,    359,    367,    373 ,   379,    383 ,   389,    397 ,   401,    409,
            #   419,    421,    431,    433,    439,    443,    449,    457,    461,    463,
            # 467,    479,    487,    491,    499,    503,    509,    521,    523,    541,
            # 547,    557,    563,    569,    571,    577,    587,    593,    599,    601,
            # 607,    613,    617,    619,    631,    641,    643,    647,    653,    659,
            # 661,    673,    677,    683,    691,    701,    709,    719,    727,    733,
            # 739,    743,    751,    757,    761,    769,    773,    787,    797,    809]:
        try:
            bch = bchlib.BCH(p, BCH_BITS)
            data = bytearray(bch1correct.bitstring_to_bytes(binary_data_msgbits))
            #data = data[1:]
            rebuildmsg=''
            for e in range(len(data)):
                segment=Fcn.dec2bin(data[e]).zfill(8)
                rebuildmsg=rebuildmsg+segment
                #print(e, data[e],segment)

            #print(binary_data_msgbits,len(binary_data_msgbits))
            #print(rebuildmsg,len(rebuildmsg),binary_data_msgbits==rebuildmsg)


            ecc = bch.encode(data)
            print('computed ecc bytes:',len(ecc))
            ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bchsgb))
            bchstring = ecc_provided[0]
            print(ecc)
            print(ecc_provided)
            for e in ecc_provided:
                binchar = Fcn.dec2bin(e).zfill(8)
                print(e, int(e), binchar)
                #bchstring = bchstring + binchar
            for e in ecc:
                #binchar = Fcn.dec2bin(e).zfill(8)
                print(e, int(e) , binchar)
                #bchstring = bchstring + binchar
            #print(bchstring)
            #print(bchsgb)
            print(p)
        except RuntimeError:
            pass
    # create array of ecc provide by bch
    ecc_provided = bytearray(bch1correct.bitstring_to_bytes(bchsgb))
    packet=data + ecc_provided

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
         newdata=Fcn.dec2bin(data[0])
         for e in data[1:]:
             binchar = Fcn.dec2bin(e).zfill(8)
    #         #print(e, binchar)
             newdata = newdata + binchar
    #
         correctedbch = '' #decodefunctions.dec2bin(ecc[0])
         for e in ecc:
             binchar = Fcn.dec2bin(e).zfill(8)
    #         #print(e, binchar)
             correctedbch = correctedbch + binchar

    return (bitflips,newdata,correctedbch)

if __name__ == "__main__":
    mainmsg= input("Main msg: ")
    bchsgb= input("BCH SGB: ")
    if not mainmsg:

        mainmsg='0000000000001110011010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000011111111111111111000000000100000000110000011010000000001001011000'
        bchsgb='101010110000011010101010101010010101111010111001'
        calculatedBCH = Sgb.calcBCH(mainmsg, 0, 202, 250)
        #print(bchsgb)
        #print(bchsgb==calculatedBCH)

        #testhex='00E608F4C986196188A047C000000000000FFFC0100C1A00960'
        #m = (Fcn.hextobin(testhex))
        #print(len(m),m)
        #calculatedBCH = Sgb.calcBCH(m, 0, 202, 250)
        #print(calculatedBCH,len(calculatedBCH))
        #print(len(mainmsg),len(bchsgb))
        #print(calculatedBCH=='010010010010101001001111110001010111101001001001')
        #data=bytearray(os.urandom(26))
        #rebuildmsg=''
        #for e in range(len(data)):
        #    segment = Fcn.dec2bin(data[e]).zfill(8)
        #    rebuildmsg = rebuildmsg + segment
        #print(rebuildmsg,len(rebuildmsg))
        mainmsg='0001110000111101111010001001111111000011111111100111100011111001110010001111101111000100010010000011101101111001001011110000101110110010001000100011001001110110100101000001010001110100010001011110110110'
        bchsgb='011001011000001000000101110011100111001101100010'
        print(mainmsg,bchsgb)
        calculatedBCH = Sgb.calcBCH(mainmsg, 0, 202, 250)
        print(calculatedBCH, len(calculatedBCH),bchsgb==calculatedBCH)
        print(Fcn.bin2hex('00'+mainmsg+calculatedBCH))
        print(len(mainmsg))
        h='070F7A27F0FF9E3E723EF1120EDE4BC2EC888C9DA5051D117B6658205CE7362'
    bitflips,newmsg,newbch = msgbits_to_bch(mainmsg,bchsgb)
    #print(mainmsg)
    #print(newmsg,len(newmsg))
    #print(bchsgb)
    #print(newbch,len(newbch))
    #print(bitflips)
    #if bitflips==-1:
    #    print('fail')

    testhex='00039A3D32618658622811F000000000001FFFF004030680258AB06AAA95EB9'
    m=(Fcn.hextobin(testhex))[2:204]
    b=(Fcn.hextobin(testhex))[204:]
    #print(testhex)
    #print(m,len(m))
    #print('bch',b,len(b))







