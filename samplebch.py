import bchlib
import hashlib
import os
import random
import decodefunctions


# create a bch object
def is_prime(n):
   if n <= 1:
      return False
   else:
      for i in range(2, n):
         # checking for factor
         if n % i == 0:
            # return False
            return False
      # returning True
   return True

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

def pdf1_to_bch(pdf1,bch1):
    #valid pdf1
    binary_data_pdf1 = pdf1

    bch1=bch1
    bch1=bch1+'000'
    #print('valid pdf1',len(binary_data_pdf1),binary_data_pdf1)


    BCH_POLYNOMIAL = 137   #137
    BCH_BITS = 3

    bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
    data = bytearray(bitstring_to_bytes(binary_data_pdf1))
    print('m:',bch.m)
    rebuildpdf=''
    for e in range(len(data)):
        segment=decodefunctions.dec2bin(data[e]).zfill(8)
        rebuildpdf=rebuildpdf+segment
        #print(e, data[e],segment)

    #print(binary_data_pdf1)
    #print(rebuildpdf,len(rebuildpdf),binary_data_pdf1==rebuildpdf)
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
    #data, ecc_provided = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

    #bitflips = bch.decode_inplace(data, ecc_provided)
    #print('bitflips: %d' % (bitflips))
    if ecc!=ecc_provided:
        #packet = data + ecc
        data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
        #correct
        bitflips = bch.decode_inplace(data,ecc)
        print('bitflips: %d' % (bitflips))
        newdata=''
        for e in data:
            binchar = decodefunctions.dec2bin(e).zfill(8)
            print(e, binchar)
            newdata = newdata + binchar
        print('corrected',newdata)
    return (bch,packet,data,ecc_provided, bchstring,bchstring==bch1)

pdf1= input("pdf1: ")
bch1= input("bch1: ")
if not pdf1:
    pdf1='1001001111001001110000000000000000000000001001011100000101111'
    bch1='110001100011101100000'

bch, packet, retdata_array ,ecc_provided2,bchsrting, valid = pdf1_to_bch(pdf1,bch1)


bchstring = ''

# if not valid:
#     #errors detected so correct in place
#     print(bch1)
#     ecc_provided_t = bytearray(bitstring_to_bytes(bch1))
#     bchstr=''
#     for e in ecc_provided_t:
#         binchar = decodefunctions.dec2bin(e).zfill(8)
#         bchstr=bchstr+binchar
#         print(binchar)
#     print(bchstr,len(bchstr),decodefunctions.dec2bin(decodefunctions.bin2dec(bchstr)))
#     bch1_recalc=decodefunctions.dec2bin(decodefunctions.bin2dec(bchstr))
#     print(bch1)
#     print(bch1_recalc)
#     ecc_provided =  bytearray(bitstring_to_bytes(bch1_recalc))
#
#
#     packet = retdata_array + ecc_provided
#     #depacketize
#     retdata_array,ecc_provided = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
#
#     #correct
#     bitflips = bch.decode_inplace(retdata_array,ecc_provided)
#     print('bitflips: %d' % (bitflips))
#     packet = retdata_array + ecc_provided
#     #depacketize
#     retdata_array,ecc_provided = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
#
#     rebuildpdf = ''
#     for e in range(len(retdata_array)):
#         segment = decodefunctions.dec2bin(retdata_array[e]).zfill(8)
#         rebuildpdf = rebuildpdf + segment
#     print(rebuildpdf)
#
#
# packet=data+ecc
# #print(len(packet))
# print(len(bchstring),bchstring)
# print('before change',packet[7])
# # encode and make a "packet"
#
# # # print hash of packet
# sha1_initial = hashlib.sha1(packet)
# # # de-packetize
# data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
# #
# print('sha1 initial: %s' % (sha1_initial.hexdigest(),))
# #
# #
# #
# #
# #
# #
# # def bitflip(packet):
# #     byte_num = random.randint(0, len(packet) - 1)
# #     bit_num = random.randint(0, 7)
# #     packet[byte_num] ^= (1 << bit_num)
# #
# # # make BCH_BITS errors
# # #for _ in range(BCH_BITS):
# # #    bitflip(packet)
# # print(byte_to_binary(data))
# packet[7] ^= (1 << 0)
# packet[7] ^= (1 << 1)
# packet[7] ^= (1 << 2)
#
# print('after change',packet[7])
# # # print hash of packet
# sha1_corrupt = hashlib.sha1(packet)
# #
# #
# # # de-packetize
# data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]
# #
# # print(byte_to_binary(data))
# print('sha1 corrupted : %s' % (sha1_corrupt.hexdigest(),))
# #
# # # correct
# bitflips = bch.decode_inplace(data, ecc)
# print('bitflips: %d' % (bitflips))
# #
# # # packetize
# packet = data + ecc
# # print(byte_to_binary(data))
# #
# # # print hash of packet
# sha1_corrected = hashlib.sha1(packet)
# print('sha1: %s' % (sha1_corrected.hexdigest(),))
# #
# if sha1_initial.digest() == sha1_corrected.digest():
#      print('Corrected!')
# else:
#      print('Failed')
#
#
# newbin=''
# for e in range(len(data)):
#     print(e,data[e])
#     x=decodefunctions.dec2bin(data[e]).zfill(8)
#     newbin=newbin+x
#
# print(newbin.lstrip('0'))
# print(binary_data_pdf1)
# # h='D3CE0000000003DDB678C140140C59'
# #
# # print(decodefunctions.hextobin(h))


# for x in range(1,10000):
#     if is_prime(x):
#         primes.append(x)
# #print(primes)
# for p in primes:
#      try:
#         bch = bchlib.BCH(p, BCH_BITS)
#         data = bytearray(bitstring_to_bytes2(binary_data_pdf1))
#
#
#         #for e in range(len(data)):
#         #    print(e, data[e])
#
#         ecc = bch.encode(data)
#         # print(type(ecc))
#         # print(ecc,len(ecc))
#         bchstring = ''
#         for e in ecc:
#             binchar = str(decodefunctions.dec2bin(e))
#             #print(e, binchar)
#             bchstring = bchstring + binchar
#         print(p,bchstring)
#         if bchstring == bch1:
#             print(p,bchstring)
#             break
#      except RuntimeError:
#         pass
#
