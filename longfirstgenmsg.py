#generate random latitude and logitude coordinates
from __future__ import division
import decodehex2
import definitions
import time



from decodefunctions import calcbch
from random import randint

def myround(x, base=5):
    return int(base * round(float(x)/base))


def roundcoord(coord, minres):
    deccoord = coord / 1000
    intcoord = int(deccoord)
    coordmin_frac = deccoord - intcoord
    coordmin = coordmin_frac * 60
    coordsec = (coordmin - int(coordmin)) * 60

    roundcoordmin = myround(coordmin, minres)

    intcoord = int(deccoord)
    if roundcoordmin == 60:
        roundcoordmin = 0
        intcoord = intcoord + 1

    if (-1 * (intcoord + roundcoordmin / 60 - deccoord) * 60) < 0:
        sign = '0'
    else:
        sign = '1'

    binvalues = (bin(int(intcoord + roundcoordmin / 60)),
                 bin(int(roundcoordmin / minres)),
                 sign,
                 bin(int(abs(int(-1 * (intcoord + roundcoordmin / 60 - deccoord) * 60)))),
                 bin(int(abs(myround(((-1 * (intcoord + roundcoordmin / 60 - deccoord) * 60) - int(
                     (-1 * (intcoord + roundcoordmin / 60 - deccoord) * 60))) * 60, 4)) / 4))
                 )

    return binvalues

def coord2bin(latcoord, longcoord, resolution, ns=0, ew=0):
    blat = roundcoord(latcoord, resolution)
    blong = roundcoord(longcoord, resolution)

    lat_bin_deg = (7 - len(blat[0][2:])) * '0' + blat[0][2:]
    long_bin_deg = (8 - len(blong[0][2:])) * '0' + blong[0][2:]

    if resolution == 4:
        pad_min_len = 4
        pad_min2_len = 3
    elif resolution == 15:
        pad_min_len = 2
        pad_min2_len = 5
    elif resolution == 2:
        pad_min_len = 5
        pad_min2_len = 2

    lat_bin_min = (pad_min_len - len(blat[1][2:])) * '0' + blat[1][2:]
    long_bin_min = (pad_min_len - len(blong[1][2:])) * '0' + blong[1][2:]

    lat_bin_min2 = (pad_min2_len - len(blat[3][2:])) * '0' + blat[3][2:]
    long_bin_min2 = (pad_min2_len - len(blong[3][2:])) * '0' + blong[3][2:]

    lat_bin_sec = (4 - len(blat[4][2:])) * '0' + blat[4][2:]
    long_bin_sec = (4 - len(blong[4][2:])) * '0' + blong[4][2:]
    lat = (lat_bin_deg, lat_bin_min, blat[2], lat_bin_min2, lat_bin_sec)
    long = (long_bin_deg, long_bin_min, blong[2], long_bin_min2, long_bin_sec)

    return dict(course=str(ns) + lat[0] + lat[1] + str(ew) + long[0] + long[1],
                fine=lat[2] + lat[3] + lat[4] + long[2] + long[3] + long[4])


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
            bch = calcbch(c.bin[:25] + '1' + c.bin[26:86], "1001101101100111100011", 25, 86, 107)

            binstr = c.bin[0:25] + '1' + c.bin[26:86] + bch + '1' + \
                     coord2bin(latitude, longitude, 4, southnorth, eastwest)['course']

            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2

        elif c.protocolflag() == 'Location' and c.loctype() == 'Standard Location':

            co = coord2bin(latitude, longitude, 15, southnorth, eastwest)

            bch = calcbch(c.bin[:25] + '1' + c.bin[26:65] + co['course'], "1001101101100111100011",
                                     25, 86, 107)
            binstr = c.bin[0:25] + '1' + c.bin[26:65] + co['course'] + bch + '110111' + co['fine']
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2

        elif c.protocolflag() == 'Location' and c.loctype() != 'Standard Location':

            co = coord2bin(latitude, longitude, 2, southnorth, eastwest)
            binstr = c.bin[0:25] + '1' + c.bin[26:59] + co['course']
            res = co['fine']
            bch = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch + '110111' + res + '000000'
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
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

print(decode('A78DC882F0411ED'))