#import bchlib
import hashlib
import os
import random



def hextobin(hexval):
    '''
    Takes a string representation of hex data with
    arbitrary length and converts to string representation
    of binary.  Includes padding 0s
    '''
    thelen = len(hexval)*4
    hexval=str(hexval)

    try:
        binval = bin(int(hexval, 16))[2:]
    except ValueError:
        return False
    while ((len(binval)) < thelen):
        binval = '0' + binval
    return binval


def calcBCH(binary, b1start, b1end, b2end):
    """ Calculates the expected BCH error-correcting code for a given binary string.
    See C/S T.018 for details.

    Args:
        binary (str): binary string
        b1start (int): bit at which to start calculating
        b1end (int): bit at which to end calculating
        b2end (int): total length of bit string
    Returns:
        bchlist: calculated BCH code
    """
    gx = '1110001111110101110000101110111110011110010010111'
    bchlist = list(binary[b1start:b1end] + '0'*(b2end-b1end))
    for i in range(b1end-b1start):
        if bchlist[i] == '1':
            for k in range(len(gx)):
                if bchlist[i+k] == gx[k]:
                    bchlist[i+k] = '0'
                else:
                    bchlist[i+k] = '1'
    return ''.join(bchlist)[b1end-b2end:]

def bin2hex(binval):
    """Convert binary to hexadecimal

    Args:
        binval (str): binary data in string format
    Returns:
        hex_str (str): hexadecimal string    """

    hex_str = '{:0{}X}'.format(int(binval, 2), len(binval) // 4)

    return hex_str

def dec2bin(n, ln=None):
    '''convert denary integer n to binary string bStr'''
    n = int(n)
    bStr = ''

    if n < 0:
        raise ValueError("must be a positive integer.")
    # if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    if not ln:
        l = len(bStr)
    else:
        l = ln
    b = '0' * (l - len(bStr)) + bStr
    return b

def byte_to_binary(binarray):
    s=''
    for b in binarray:
        s=s+dec2bin(b)
    return s

def  bin2dec(s):
    try:
        a=int(s,2)
    except ValueError:
        a=0
    return a

def bitstring_to_bytes2(s):
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def bitstring_to_bytes3(bits):
    s=bits.zfill(202)

    b = bytearray()
    for i in range(0,202,8):
        b.append(int(s[i:i+8],2) & 0xff)


    return bytes(b[::-1])

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) +7) // 8, byteorder='big')


def is_prime(num):
    if num > 1:
        # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                #print(num, "is not a prime number")
                #print(i, "times", num // i, "is", num)
                return False
                break
        else:
            return True

    # if input number is less than
    # or equal to 1, it is not prime
    else:
        return False

def bitflip(packet,byte_num):
    #byte_num = random.randint(0, len(packet) - 1)
    bit_num = random.randint(0, 7)
    bit_num = 0
    packet[byte_num] ^= (1 << bit_num)


def scramble_msg(main_msg,p=487):
    success=False
    BCH_POLYNOMIAL = 487
    BCH_BITS = 6
    bch = bchlib.BCH(p, 6 , False)
    b= main_msg
    print(len(b),b,'msg input')
    data_only = bytearray(bitstring_to_bytes2(b))   #2
    ecc = bch.encode(data_only)
    recompose=''
    #print(ecc)
    bin_check=''
    for bc in data_only:
        c = dec2bin(bc).zfill(8)
        bin_check = bin_check + c
    print(len(bin_check),len(main_msg) , bin_check.zfill(202)==main_msg)
    print(bin_check)
    print(main_msg)
    recalcbch = calcBCH(bin_check.zfill(202),0,202,250)


    for e in ecc:
        c = dec2bin(e).zfill(8)
        #print(repr(e),e)
        #d=format(ord(e), '08b')
        recompose = recompose +  c

    packet = data_only + ecc
    # print hash of packet
    sha1_initial = hashlib.sha1(packet)
    #print('sha1: %s' % (sha1_initial.hexdigest(),))
    # make BCH_BITS errors
    for i in range(BCH_BITS ):
        bitflip(packet, i + 3 )

    sha1_corrupt = hashlib.sha1(packet)

    #print('sha1: %s' % (sha1_corrupt.hexdigest(),))
    corrupted=''
    for e in packet:
        c = dec2bin(e).zfill(8)
        corrupted = corrupted +  c
    data_only, ecc = packet[:-bch.ecc_bytes], packet[
                                              -bch.ecc_bytes:]  # data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

    # correct
    bitflips =0
    sha1_corrected = 0
    try:
        bitflips = bch.decode_inplace(data_only, ecc)
        #print('\nbitflips: %d' % (bitflips))

        # packetize
        packet = data_only + ecc
        correct_final=''
        for e in packet:
            c = dec2bin(e).zfill(8)
            correct_final = correct_final + c

        # print hash of packet
        sha1_corrected = hashlib.sha1(packet)
        #print('sha1: %s' % (sha1_corrected.hexdigest(),))

        if sha1_initial.digest() == sha1_corrected.digest():

            success=True
        else:
            success=False
    except:
        success = False
        return(success,'Done')
    hashes = (sha1_corrected.hexdigest(), sha1_corrupt.hexdigest(),sha1_initial.hexdigest())
    return {'original' : ('00'+ b+recompose, len('00'+ b), len(recompose),len('00'+ b+recompose)),
            'msg_input' : main_msg,
            'corrupted': (corrupted.zfill(252),len(corrupted.zfill(252))),
            'success': success,
            'hashes' : hashes,
            'flips' : bitflips,
            'ECC':{'New method' : recompose,'T.018 method' : calcBCH(b,0,202,250), 'recompECC' : recalcbch},
            'Len': len(recompose),
            'Done' : 'Done',
            'correct_final': correct_final.zfill(252),
            'hex': bin2hex(correct_final.zfill(252))}

def hex_bch(hex):
    b = hextobin(hex).zfill(255)
    packet = bytearray(bitstring_to_bytes2(b))
    bch = bchlib.BCH(487, 6 , False)
    data_only, ecc = packet[:-6], packet[-6:]  # data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

    # correct
    corrected_hex =''
    bitflips = 0

    try:
        bitflips = bch.decode_inplace(data_only, ecc)
        print('\nbitflips: %d' % (bitflips))
        # packetize
        packet = data_only + ecc
        correct_final=''
        for e in packet:
            c = dec2bin(e).zfill(8)
            correct_final = correct_final + c
        corrected_hex = bin2hex(correct_final)
        if bitflips:
            success = True
        else:
            success = False
    except:
        success = False
    return (hex,corrected_hex)



def create_test():
    #if __name__ == "__main__":
    # create a bch object
    BCH_POLYNOMIAL = 8219
    BCH_BITS = 6

    primes=[]
    for i in range(8500):
        if is_prime(i):
            primes.append(i)


    primes=[487]
    f=open('bchtext2.txt','w')
    for p in primes:
        try:
            bch = bchlib.BCH(p, BCH_BITS, True)
            f.write('\n===='+str(p)+'====='+str(bch.n)+'====='+str(bch.m))

            recompose=''
            # sample hex 00E608F4C986196188A047C000000000000FFFC0100C1A00960
            #print(p,bch.m,bch.n)

            b='0000000011100110000010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000000011111111111111000000000100000000110000011010000000001001011000'
            print(len(b),bin2hex(b))
            print( bin2hex(b))
            print( bin2dec(b[:16]))
            calcbch = calcBCH(b, 0, 202, 250)
            comp_b= b+calcbch


            print(len(comp_b))



            f.write('\nBCH provided calcbch {} '.format(str(calcbch)))

            #packet = newdata
            data_only = bytearray(bitstring_to_bytes2(b))
            ecc = bch.encode(data_only)
            f.write('\nECC computed{} '.format(str(byte_to_binary(ecc))))
            f.write('\nECC bits count: {}\n'.format(bch.ecc_bits))
            recompose = ''
            for e in ecc:
                c = dec2bin(e).zfill(8)

                f.write(str(e)+' ')
                recompose = recompose + ' ' +c

            f.write('\nECC bits   : {}'.format(recompose))

            print('ecc calc',len(ecc))
            packet = data_only + ecc
            # print hash of packet
            sha1_initial = hashlib.sha1(packet)
            print('sha1: %s' % (sha1_initial.hexdigest(),))
            f.write('\nsha1: %s' % (sha1_initial.hexdigest(),))

            # make BCH_BITS errors
            for i in range(BCH_BITS-1):
                bitflip(packet,i+2)

            bitflip(packet,25)
            # print hash of packet
            sha1_corrupt = hashlib.sha1(packet)

            print('sha1: %s' % (sha1_corrupt.hexdigest(),))
            f.write('\nsha1 corrupt: %s' % (sha1_corrupt.hexdigest(),))
            # de-packetize
            f.write('\nECC bits: {}'.format(bch.ecc_bits))

            data_only, ecc =  packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]#data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

            # correct
            try:
                bitflips = bch.decode_inplace(data_only, ecc)
                print('\nbitflips: %d' % (bitflips))
                f.write('\nbitflips: %d' % (bitflips))
                # packetize
                packet = data_only + ecc

                # print hash of packet
                sha1_corrected = hashlib.sha1(packet)
                print('sha1: %s' % (sha1_corrected.hexdigest(),))
                f.write('\nsha1: %s' % (sha1_corrected.hexdigest(),))
                if sha1_initial.digest() == sha1_corrected.digest():
                    print('Corrected!')
                    f.write('\nCorrected!')
                else:
                    print('Failed')
                    f.write('\nFailed')
            except:
                pass
        except RuntimeError or ValueError:
            f.write('Parameter Failed')

    f.close()

def create_test2():
    #if __name__ == "__main__":
    # create a bch object

    BCH_BITS = 48

    primes=[]
    for i in range(18500):
        if is_prime(i):
            primes.append(i)



    f=open('bchtext2.txt','w')
    for p in primes:
        try:
            bch = bchlib.BCH(p, BCH_BITS)
            f.write('\n===='+str(p)+'====='+str(bch.n)+'====='+str(bch.m))

            randombin = '000000'+ ''.join(map(lambda x: str(random.randint(0, 1)), [i for i in range(202)]))

            data = bytearray(map(lambda x: int(x), randombin))

            f.write('\nData provided  {} '.format(str(data)))
            # encode and make a "packet"
            ecc = bch.encode(data)
            renew = '-'.join(map(lambda x: str(int(x)), [e for e in ecc]))
            f.write('\necc int {} '.format(str(renew)))
            print(ecc, len(ecc))
            f.write('\npacket data before corrupt: %s' % (data))



            calcbch = calcBCH(randombin, 0, 202, 250)



            f.write('\nBCH provided calcbch {} '.format(str(calcbch)))
            f.write('\nECC computed{} '.format(str(byte_to_binary(ecc))))
                #packet = newdata

            f.write('\nECC computed{} '.format(ecc))


            f.write('\nECC bits count: {}\n'.format(bch.ecc_bits))


            packet = data + ecc
            # print hash of packet
            sha1_initial = hashlib.sha1(packet)
            print('sha1: %s' % (sha1_initial.hexdigest(),))
            f.write('\nsha1: %s' % (sha1_initial.hexdigest(),))

            # make BCH_BITS errors
            for i in range(6):
                r=random.randint(1,202)
                flip = packet[r]
                n = not flip
                f.write('\n==============position flipped ==={} == {}  === {}  '.format (r,flip,n))
                packet[r] = n



            # print hash of packet
            sha1_corrupt = hashlib.sha1(packet)
            f.write('\npacket corrupt: %s' % (packet))
            print('sha1: %s' % (sha1_corrupt.hexdigest(),))
            f.write('\nsha1 corrupt: %s' % (sha1_corrupt.hexdigest(),))
            # de-packetize
            f.write('\nECC bits: {}'.format(bch.ecc_bits))

            data, ecc =  packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]#data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

            # correct
            try:
                bitflips = bch.decode_inplace(data, ecc)
                print('\nbitflips: %d' % (bitflips))
                f.write('\nbitflips: %d' % (bitflips))
                # packetize
                packet = data + ecc

                # print hash of packet
                sha1_corrected = hashlib.sha1(packet)
                print('sha1: %s' % (sha1_corrected.hexdigest(),))
                f.write('\nsha1: %s' % (sha1_corrected.hexdigest(),))
                if sha1_initial.digest() == sha1_corrected.digest():
                    print('Corrected!')
                    f.write('\nCorrected!')
                else:
                    print('Failed')
                    f.write('\nFailed')
            except:
                pass
        except RuntimeError : #or ValueError:
            f.write('Parameter Failed')

    f.close()


if __name__ == "__main__":
    b='0011000001110011000001010111101001100100110011100101100101110001100010001010000001000111110000000000000000000000000000000000000000000000000011111111111111000000000100000000110000011010000000001001011000'
    #create_test2()
    a=scramble_msg('000000'+''.join(map(lambda x: str(random.randint(0, 1)), [i for i in range(202)])))
    print(a)
    print(a['ECC'])

    # print(len(b))
    # print(bitstring_to_bytes3(b),len(bitstring_to_bytes3(b)),type(bitstring_to_bytes3(b)))
    # print(bitstring_to_bytes2(b), len(bitstring_to_bytes2(b)), type(bitstring_to_bytes2(b)))
    # print(bitstring_to_bytes(b), len(bitstring_to_bytes(b)), type(bitstring_to_bytes(b)))
    # print('----')
    # a = scramble_msg(b)
    # print(a['hashes'])
    # print(a['ECC']['New method'])
    # print(a['ECC']['T.018 method'])
    # print(a['ECC']['recompECC'])
    # print(a['hex'])
    # print(a['flips'])
    # #print(a)
    # #print('\nHex Check:')
    # h = hex_bch(a['hex'])
    # #print(h)
    #
    # hexcheck='19CC15E9933965C622811F0000000200003FFF004030680258E0C546519300'
    # h = hex_bch(hexcheck)
    # #print(h)
    #
    # hexcheck ='001CC15E9933965C622811F0000000000003FFF0040306802585FC13960FA99'
    # h = hex_bch(hexcheck)
    # #print(h)
    #
    # print(bitstring_to_bytes3('000011'))
    # print(bitstring_to_bytes3('011'))
