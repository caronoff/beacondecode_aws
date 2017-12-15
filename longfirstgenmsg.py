#generate random latitude and logitude coordinates
from __future__ import division
import decodehex2
import definitions
import time
from random import randint



def decode(hex_code):


    c = decodehex2.BeaconHex()
    try:
        c.processHex(str(hex_code.strip()))
        latitude = randint(0, 89999)
        longitude = randint(0, 179999)
        southnorth = randint(0, 1)
        eastwest = randint(0, 1)
        tsouthnorth = ('North', 'South')[southnorth]
        teastwest = ('East', 'West')[eastwest]

        if c.protocolflag() == 'User':
            bch = decodehex2.calcbch(c.bin[:25] + '1' + c.bin[26:86], "1001101101100111100011", 25, 86, 107)

            binstr = c.bin[0:25] + '1' + c.bin[26:86] + bch + '1' + \
                     coord2bin(latitude, longitude, 4, southnorth, eastwest)['course']

            bch2 = decodehex2.calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2






        elif c.protocolflag() == 'Location' and c.loctype() == 'Standard Location':

            co = coord2bin(latitude, longitude, 15, southnorth, eastwest)

            bch = decodehex2.calcbch(c.bin[:25] + '1' + c.bin[26:65] + co['course'], "1001101101100111100011",
                                     25, 86, 107)
            binstr = c.bin[0:25] + '1' + c.bin[26:65] + co['course'] + bch + '110111' + co['fine']
            bch2 = decodehex2.calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2






        elif c.protocolflag() == 'Location' and c.loctype() != 'Standard Location':

            co = coord2bin(latitude, longitude, 2, southnorth, eastwest)
            binstr = c.bin[0:25] + '1' + c.bin[26:59] + co['course']
            res = co['fine']
            bch = decodehex2.calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch + '110111' + res + '000000'
            bch2 = decodehex2.calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2


        nh = decodehex2.bin2hex(binstr[1:])
        c.processHex(nh)
        newline = '\n{l} {beacon}\n{sn} {deglat}-{ew} {deglong}. \nHex: {longh} {m}.\n15 Hex:{h15}:{test}\n'.format(
            m=c.type, l=c.loctype(), sn=tsouthnorth, ew=teastwest, deglat=latitude / 1000,
            deglong=longitude / 1000, longh=nh, h15=c.hex15, oldh=line, test=c.hex15 == line.upper(),
            beacon=c.btype())



        f1.write(newline)
        f1.write(c.protocoldata() + '\n')
        f1.write(c.countrydetail.countrydata() + '\n')
        f1.write(c.identdata() + '\n')

        f1.write(c.locationdata() + '\n')
        f1.write('{bch1}\n{bch2}\n'.format(mtype=c.type, bch1=c.bch.writebch1(), bch2=c.bch.writebch2()))




    except decodehex2.HexError as e:
        print(e.value, e.message)
