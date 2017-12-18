#generate random latitude and logitude coordinates
from __future__ import division
import decodehex2
import definitions
import time



from decodefunctions import calcbch, bin2hex,dec2bin
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


def stdloc(lat,long):
    latdegrees = round(float(lat / 1000) * 4, 0)
    binlat = dec2bin(latdegrees, 9)
    longdegrees = round(float(long / 1000) * 4, 0)
    binlong = dec2bin(longdegrees, 10)
    offsets = []
    for coord in [(lat, latdegrees), (long, longdegrees)]:
        dif = float(coord[0] / 1000) - float(coord[1] / 4)
        if (dif) > 0:
            s = '1'
        else:
            s = '0'
        dif = abs(dif)
        min = int(float(dif * 60))
        minbin = dec2bin(min, 5)
        sec = round((dif * 3600), 0) - min * 60
        secbin = dec2bin(round((float(sec / 4)), 0), 4)
        offsetbin = s + minbin + secbin
        offsets.append(offsetbin)
    return (binlat, binlong, offsets[0], offsets[1])

def natloc(l,lg):
    lat=float(l/1000)
    long=float(lg/1000)
    binlat = dec2bin(int(lat),7) + dec2bin( round(float((lat-int(lat))*30 ),0 ), 5)
    binlong = dec2bin(int(long), 8) + dec2bin(round(float((long - int(long)) * 30), 0), 5)
    offsets=[]
    for coord in [l,lg]:
        offsets.append(min_sec(coord,2,4))
    return (binlat,binlong,offsets[0],offsets[1])

def min_sec(degrees,bits_min, bits_sec):
    dif = float(degrees - round(degrees,0)) * float ( 30 / 1000 )
    if (dif) > 0:
        s = '1'
    else:
        s = '0'
    intdif= int(float( dif / 30))
    decdif = float( dif / 30) - intdif
    minutes =int(float(decdif*60))
    minbin = dec2bin(minutes, bits_min)
    seconds = round((float(decdif*3600)- float(minutes*60),0)/4)
    secbin = dec2bin(seconds, bits_sec)
    return s+minbin+secbin


def eltdt_rls(lat,long):
    latdegrees = round(float(lat / 1000) * 2, 0)
    binlat = dec2bin(latdegrees, 8)
    longdegrees = round(float(long / 1000) * 2, 0)
    binlong = dec2bin(longdegrees, 9)
    offsets=[]
    for coord in [(lat,latdegrees),(long,longdegrees)]:
        dif = float(coord[0] / 1000) - float(coord[1] / 2)
        if (dif) > 0:
            s = '1'
        else:
            s = '0'
        dif = abs(dif)
        min = int(float(dif * 60))
        minbin = dec2bin(min , 4)
        sec = round((dif * 3600),0) - min* 60
        secbin = dec2bin(round((float(sec / 4)),0), 4)
        offsetbin = s + minbin + secbin
        offsets.append(offsetbin)
    return (binlat,binlong,offsets[0],offsets[1])


def decode(hex_code,latitude,southnorth,longitude,eastwest):
    c = decodehex2.BeaconHex()
    try:
        c.processHex(str(hex_code.strip()))


        if c.protocolflag() == 'User':
            bch = calcbch(c.bin[:25] + '1' + c.bin[26:86], "1001101101100111100011", 25, 86, 107)

            binstr = c.bin[0:25] + '1' + c.bin[26:86] + bch + '1' + \
                     coord2bin(latitude, longitude, 4, southnorth, eastwest)['course']

            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2

        elif c.protocolflag() == 'Location' and c.loctype() == 'Standard Location':
            bincoord = stdloc(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:65] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + '110111' + bincoord[2] + bincoord[3]
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2



        elif c.protocolflag() == 'Location' and c.loctype() in ['ELT-DT Location','RLS Location']:
            bincoord= eltdt_rls(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:67] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + '11111111' + bincoord[2] + bincoord[3]
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2



        elif c.protocolflag() == 'Location' and c.loctype() in ['National Location']:

            bincoord= natloc(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:67] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + '11111111' + bincoord[2] + bincoord[3]
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2



            co = coord2bin(latitude, longitude, 2, southnorth, eastwest)
            binstr = c.bin[0:25] + '1' + c.bin[26:59] + co['course']
            res = co['fine']
            bch = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch + '110111' + res + '000000'
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2


        nh = bin2hex(binstr[1:])

        return nh

    except decodehex2.HexError as e:
        print(e.value, e.message)


if __name__ == "__main__":
    serialuser = 'A78DC882F0411ED'
    eltdt ='2792E26E3DBFDFF'
    std = '4CAB4C48F6FFBFF'
    rls='279A8180103FDFF'
    hex_code = rls
    latitude = randint(0, 89999)
    longitude = randint(0, 179999)
    southnorth = randint(0, 1)
    eastwest = randint(0, 1)
    tsouthnorth = ('North', 'South')[southnorth]
    teastwest = ('East', 'West')[eastwest]


    longhex=decode(hex_code,latitude,southnorth,longitude,eastwest)

    c = decodehex2.BeaconHex(longhex)

    newline = '\n{l} {beacon}\n{sn} {deglat}-{ew} {deglong}. \nHex: {longh} {m}.\n15 Hex:{h15}:{test}\n'.format(
        m=c.type, l=c.loctype(), sn=tsouthnorth, ew=teastwest, deglat=latitude / 1000,
        deglong=longitude / 1000, longh=longhex, h15=c.hex15, oldh=hex_code, test=c.hex15 == hex_code.upper(),
        beacon=c.btype())

    print(newline)
    print(c.protocoldata() + '\n')
    print(c.countrydetail.countrydata() + '\n')
    print('{bch1}\n{bch2}\n'.format(mtype=c.type, bch1=c.bch.writebch1(), bch2=c.bch.writebch2()))
