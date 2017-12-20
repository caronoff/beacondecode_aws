#generate random latitude and logitude coordinates
from __future__ import division
import decodehex2
import definitions

from decodefunctions import calcbch, bin2hex,dec2bin
from random import randint


def stdloc(lat,long):
    latdegrees = round(float(lat / 1000) * 4, 0)
    binlat = dec2bin(latdegrees, 9)
    longdegrees = round(float(long / 1000) * 4, 0)
    binlong = dec2bin(longdegrees, 10)
    offsets = []
    for coord in [(lat, latdegrees), (long, longdegrees)]:
        dif = float(coord[0] / 1000) - float(coord[1] / 4)
        offsets.append(min_sec(dif, 5, 4))
    return (binlat, binlong, offsets[0], offsets[1])

def natloc(l,lg):
    lat=float(l/1000)
    long=float(lg/1000)
    binlat = dec2bin(int(lat),7) + dec2bin( round(float((lat-int(lat))*30 ),0 ), 5)
    binlong = dec2bin(int(long), 8) + dec2bin(round(float((long - int(long)) * 30), 0), 5)
    offsets=[]
    for coord in [l,lg]:
        print(int(coord/1000),float(coord/1000)-int(coord/1000), round(30*(float(coord/1000) - int(coord/1000)) ,0)/30 )
        rnd= float(coord/1000)-int(coord/1000) - round(30*(float(coord/1000) - int(coord/1000)) ,0)/30
        offsets.append(min_sec(rnd,2,4))
    return (binlat,binlong,offsets[0],offsets[1])

def min_sec(rnd,bits_min, bits_sec):
    if (rnd) > 0:
        s = '1'
    else:
        s = '0'
    dif=abs(rnd)
    minutes =int(float(dif*60))
    minbin = dec2bin(minutes, bits_min)
    seconds = float(dif*3600)  -   float(minutes*60)
    sec = round(float(seconds/4))
    secbin = dec2bin(sec, bits_sec)
    print(minutes,sec)
    return s+minbin+secbin


def eltdt_rls(lat,long):
    latdegrees = round(float(lat / 1000) * 2, 0)
    binlat = dec2bin(latdegrees, 8)
    longdegrees = round(float(long / 1000) * 2, 0)
    binlong = dec2bin(longdegrees, 9)
    offsets=[]
    for coord in [(lat,latdegrees),(long,longdegrees)]:
        dif = float(coord[0] / 1000) - float(coord[1] / 2)
        offsets.append(min_sec(dif, 4, 4))

    return (binlat,binlong,offsets[0],offsets[1])


def encodelongFGB(hex_code,latitude,southnorth,longitude,eastwest, suppdata):

    latitude=float(latitude) * 1000
    longitude = float(longitude) * 1000
    print(type(latitude))
    print(latitude)
    c = decodehex2.BeaconFGB()
    try:
        c.processHex(str(hex_code.strip()))


        if c.protocolflag() == 'User':
            binstr = c.bin[0:25] + '1' + c.bin[26:86]

            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr  + bch1 + suppdata

            binstr = binstr + str(southnorth) + dec2bin(int(float(latitude/1000)),7) + \
                     dec2bin( round(( float(latitude/1000) - int(float(latitude/1000))) * 15,0) ,4) + str(eastwest) + \
                     dec2bin(int(float(longitude / 1000)), 8) + \
                     dec2bin(round((float(longitude / 1000) - int(float(longitude / 1000))) * 15, 0), 4)
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2


        elif c.protocolflag() == 'Location' and c.loctype() == 'Standard Location':
            bincoord = stdloc(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:65] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + suppdata + bincoord[2] + bincoord[3]
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2



        elif c.protocolflag() == 'Location' and c.loctype() in ['ELT-DT Location','RLS Location']:
            bincoord= eltdt_rls(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:67] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + suppdata + bincoord[2] + bincoord[3]
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2



        elif c.protocolflag() == 'Location' and c.loctype() == 'National Location':
            bincoord= natloc(latitude, longitude)
            binstr = c.bin[0:25] + '1' + c.bin[26:59] + str(southnorth) + bincoord[0] + str(eastwest) + bincoord[1]
            bch1 = calcbch(binstr, "1001101101100111100011", 25, 86, 107)
            binstr = binstr + bch1 + suppdata + bincoord[2] + bincoord[3] + '000000'
            bch2 = calcbch(binstr, '1010100111001', 107, 133, 145)
            binstr = binstr + bch2

        return bin2hex(binstr[1:])

    except decodehex2.HexError as e:
        print(e.value, e.message)


if __name__ == "__main__":
    serialuser = 'A78DC882F0411ED'
    eltdt ='2792E26E3DBFDFF'
    std = '4CAB4C48F6FFBFF'
    rls='279A8180103FDFF'
    nat ='A79000000000000'
    nat_loc='27942D56BF81FE0'
    hex_code = std
    #suppdat='11111110'
    suppdat = '110111'
    latitude = randint(0, 89999)
    longitude = randint(0, 179999)
    southnorth = randint(0, 1)
    eastwest = randint(0, 1)
    tsouthnorth = ('North', 'South')[southnorth]
    teastwest = ('East', 'West')[eastwest]


    longhex=encodelongFGB(hex_code,latitude/1000,southnorth,longitude/1000,eastwest,suppdat)

    c = decodehex2.BeaconFGB(longhex)

    newline = '\n{l} {beacon}\n{sn} {deglat}-{ew} {deglong}. \nHex: {longh} {m}.\n15 Hex:{h15}:{test}\n'.format(
        m=c.type, l=c.loctype(), sn=tsouthnorth, ew=teastwest, deglat=latitude / 1000,
        deglong=longitude / 1000, longh=longhex, h15=c.hex15, oldh=hex_code, test=c.hex15 == hex_code.upper(),
        beacon=c.btype())

    print(newline)
    print(c.protocoldata() + '\n')
    print(c.countrydetail.countrydata() + '\n')
    print('{bch1}\n{bch2}\n'.format(mtype=c.type, bch1=c.bch.writebch1(), bch2=c.bch.writebch2()))
