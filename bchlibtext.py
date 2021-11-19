import bchlibcaronoff
import hashlib
import os
import random

#import decodefunctions


def test_bchlib():
    # create a bch object
    BCH_POLYNOMIAL = 285
    BCH_BITS = 6
    bch = bchlibcaronoff.BCH(BCH_POLYNOMIAL, BCH_BITS)

    # random data
    data = bytearray(b'\x01'+os.urandom(25))
    print(len(data))
    # encode and make a "packet"
    ecc = bch.encode(data)
    packet = data + ecc
    #l=''.join([decodefunctions.dec2bin(e).zfill(8)  for e in packet])[4:]
    #print(l,len(l))
    #print(decodefunctions.bin2hex(l))
    # print hash of packet
    sha1_initial = hashlib.sha1(packet)
    print('sha1: %s' % (sha1_initial.hexdigest(),))

    def bitflip(packet):
        byte_num = random.randint(0, len(packet) - 1)
        bit_num = random.randint(0, 7)
        packet[byte_num] ^= (1 << bit_num)

    # make BCH_BITS errors
    for _ in range(BCH_BITS):
        bitflip(packet)

    # print hash of packet
    sha1_corrupt = hashlib.sha1(packet)
    print('sha1: %s' % (sha1_corrupt.hexdigest(),))

    # de-packetize
    data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

    print(len(data))
    # correct
    bitflips = bch.decode_inplace(data, ecc)

    print('bitflips: %d' % (bitflips))

    # packetize
    packet = data + ecc

    # print hash of packet
    sha1_corrected = hashlib.sha1(packet)
    print('sha1: %s' % (sha1_corrected.hexdigest(),))

    if sha1_initial.digest() == sha1_corrected.digest():
        print('Corrected!')
    else:
        print('Failed')

if __name__ == "__main__":
    test_bchlib()

