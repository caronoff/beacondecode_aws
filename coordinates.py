#generate random latitude and logitude coordinates
from __future__ import division
from random import randint
def myround(x, base=5):
    return int(base * round(float(x)/base))

latitude=74666 #randint(0,89999)
longitude=51905 #randint(0,179999)
southnorth=randint(0,1)
eastwest=randint(0,1)

def coord2bin(latcoord,longcoord,resolution):
    blat=roundcoord(latcoord,resolution)
    blong=roundcoord(longcoord,resolution)

    lat_bin_deg = (7-len(blat[0][2:]))*'0'+blat[0][2:]
    long_bin_deg =(8-len(blong[0][2:]))*'0'+blong[0][2:]

    if resolution==4:
        pad_min_len = 4
        pad_min2_len = 3
    elif resolution == 15:
        pad_min_len = 2
        pad_min2_len = 5
    elif resoltion== 2:
        pad_min_len = 5
        pad_min2_len = 2

    lat_bin_min = (pad_min_len - len(blat[1][2:]))*'0'+ blat[1][2:]    
    long_bin_min = (pad_min_len - len(blong[1][2:]))*'0'+ blong[1][2:]

    lat_bin_min2 = (pad_min2_len - len(blat[3][2:]))*'0'+ blat[3][2:]    
    long_bin_min2 = (pad_min2_len - len(blong[3][2:]))*'0'+ blong[3][2:]

    lat_bin_sec=  (4 - len(blat[4][2:]))*'0'    +   blat[4][2:]
    long_bin_sec= (4 - len(blong[4][2:]))*'0'   +  blong[4][2:]
    
    return (lat_bin_deg,lat_bin_min,blat[2],lat_bin_min2,lat_bin_sec),(long_bin_deg,long_bin_min,blong[2],long_bin_min2,long_bin_sec)




def roundcoord(coord,minres):
    deccoord=coord/1000
    intcoord=int(deccoord)
    coordmin_frac=deccoord-intcoord
    coordmin=coordmin_frac*60
    coordsec=(coordmin-int(coordmin))*60
    
    roundcoordmin=myround(coordmin,minres)

##    print '%.4f\n\n %d degrees %d minutes %d seconds (%.2f %.2f)\n' %  (deccoord,intcoord,int(coordmin),int(coordsec),coordmin,coordsec)
##
##    
##    print'\n'
    intcoord=int(deccoord)
    if roundcoordmin==60:
        roundcoordmin=0
        intcoord=intcoord+1

##    #print intcoord,'deg',roundcoordmin,'minutes',intcoord+roundcoordmin/60
##    #print 'real value ',deccoord
##    print 'Degree to save in PDF-1: %i    Minutes to save in PDF-1: %i' % (int(intcoord+roundcoordmin/60),roundcoordmin)
##    #print 'decimal adjust',-1*(intcoord+roundcoordmin/60-deccoord)
##    print 'minute adjust',int(-1*(intcoord+roundcoordmin/60-deccoord)*60)
##    #print 'second adjust',((-1*(intcoord+roundcoordmin/60-deccoord)*60)-int((-1*(intcoord+roundcoordmin/60-deccoord)*60)))*60
##    print 'second rounded adjust',myround(((-1*(intcoord+roundcoordmin/60-deccoord)*60)-int((-1*(intcoord+roundcoordmin/60-deccoord)*60)))*60,4)
    binvalues=(bin(int(intcoord+roundcoordmin/60)),
               bin(int(roundcoordmin/minres)),
               cmp(-1*(intcoord+roundcoordmin/60-deccoord)*60,0),
               bin(int(abs(int(-1*(intcoord+roundcoordmin/60-deccoord)*60)))),
               bin(int(abs(myround(((-1*(intcoord+roundcoordmin/60-deccoord)*60)-int((-1*(intcoord+roundcoordmin/60-deccoord)*60)))*60,4))/4))
               )         
               
    return binvalues

for coord in [latitude,longitude]:
    #coord=latitude


    deccoord=coord/1000
    intcoord=int(deccoord)

    coordmin_frac=deccoord-intcoord
    coordmin=coordmin_frac*60
    coordsec=(coordmin-int(coordmin))*60


    print '%.4f\n %d degrees %d minutes %d seconds (%.2f %.2f)\n' %  (deccoord,intcoord,int(coordmin),int(coordsec),coordmin,coordsec)

    for roundcoordmin in [myround(coordmin,15)]: #[myround(coordmin,4),myround(coordmin,15),myround(coordmin,2)]:
        print'\n'
        intcoord=int(deccoord)
        if roundcoordmin==60:
            roundcoordmin=0
            intcoord=intcoord+1
        #print intcoord,'deg',roundcoordmin,'minutes',intcoord+roundcoordmin/60
        #print 'real value ',deccoord
        print 'Degree to save in PDF-1: %i    Minutes to save in PDF-1: %i' % (int(intcoord+roundcoordmin/60),roundcoordmin)
        #print 'decimal adjust',-1*(intcoord+roundcoordmin/60-deccoord)
        print 'minute adjust',int(-1*(intcoord+roundcoordmin/60-deccoord)*60)
        #print 'second adjust',((-1*(intcoord+roundcoordmin/60-deccoord)*60)-int((-1*(intcoord+roundcoordmin/60-deccoord)*60)))*60
        print 'second rounded adjust',myround(((-1*(intcoord+roundcoordmin/60-deccoord)*60)-int((-1*(intcoord+roundcoordmin/60-deccoord)*60)))*60,4)
            






