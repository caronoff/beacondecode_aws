import csv


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
    f = open('bchfile2.txt', 'w')
    sout=""
    gx = '1110001111110101110000101110111110011110010010111'
    bchlist = list(binary[b1start:b1end] + '0' * (b2end - b1end))
    newrow = []
    c = 0
    first = ''.join(bchlist)
    #print(first)
    #print(len(first))
    oldgxspace = newgxspace = 0

    gxfirst = first.index('1') * ' ' + gx
    f.write("\r\nm(x):{}\r\ng(x):{}".format(first, gxfirst))
    sout="\r\nm(x):{}\r\ng(x):{}".format(first, gxfirst)
    firstone = first.index('1')
    for i in range(b1end - b1start):
        c = c + 1
        if bchlist[i] == '1':
            if c > 0:

                mx = ''.join(newrow)
                if len(mx) > 0:
                    newgxspace =  mx.index('1')
                    #mx = mx + newgxspace * '0'
                    bchnew = "\r\nm(x):{}{}\r\ng(x):{}{}".format((oldgxspace + firstone) * ' ', mx + mx.index('1')*'0',
                                                         (firstone + mx.index('1') + oldgxspace) * ' ', gx)
                    newgx = (newgxspace + oldgxspace) * ' ' + gx
                    oldgxspace = newgx.index('1')
                    f.write("\r\n{} {} {}".format(str(i), str(mx.index('1')),(b2end-2) * '-'))
                    sout=sout+"\r\n{} {} {}".format(str(i), str(mx.index('1')),(b2end-2) * '-')
                    f.write(bchnew)
                    sout=sout+bchnew
            newrow = []
            for k in range(len(gx)):
                if bchlist[i + k] == gx[k]:
                    bchlist[i + k] = '0'
                    newrow.append('0')
                else:
                    bchlist[i + k] = '1'
                    newrow.append('1')


    bchfinal = ''.join(bchlist)[b1end - b2end:]
    bchfinalw = "\r\nm(x):{}{}\r\n".format('', ''.join(bchlist))
    f.write(bchfinalw)
    sout=sout+bchfinalw
    f.write("\r\nBCH code (last 48 bits.)\r\n{}\r\n{}\r\n{}".format(48*'-',bchfinal,48*'-'))
    sout=sout+'\r\nBCH code (last 48 bits.)\r\n{}\r\n{}\r\n{}'.format(48*'-',"'"+bchfinal,48*'-')
    f.close()

    return (bchfinal,sout)


if __name__ == "__main__":
    b4 = '0000000000001110011010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000011111111111111111000000000100000000110000011010000000001001011000'
    b2DecT018 = '000001001100100110100000000000011100110100011110111000000000000000000000000000000000000000000000111000110000011001110100011001000101000000010010010111111111111000000000100000000110000011001100000001001011011'
    b3 = '000000000000000001110011010001111010011001001100001100001100101100001100010001010000001000111110000000000000000000000000000000000000000000000011111111111111111000000000100000000110000011010000000001001011000'
    b5 = '000000000000000001111101000011011110101100100010001011010000000000000000001010000000000000000000010000100001111100111011010100111000000110111111111111111111111000000001000000011001000001101111111111000101100'
    b6 = '0000000000001111101000011011110101100100010001011010000000000000000001010000000000000000000010000100001111100111011010100111000000110111111111111111111111000000001000000011001000001101111111111000101100'

    print(calcBCH(b6, 0, 202, 250))

