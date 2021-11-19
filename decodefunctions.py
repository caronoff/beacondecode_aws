#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
#decode functions

# -*- coding: utf-8 -*-
import definitions
import time


# updated July 12, 2017


BAUDOT={
            '111000':'A','110011':'B','101110':'C','110010':'D','110000':'E'
            ,'110110':'F','101011':'G','100101':'H','101100':'I','111010':'J'
            ,'111110':'K','101001':'L','100111':'M','100110':'N','100011':'O'
            ,'101101':'P','111101':'Q','101010':'R','110100':'S','100001':'T'
            ,'111100':'U','101111':'V','111001':'W','110111':'X','110101':'Y'
            ,'110001':'Z','100100':' ','011000':'-','010111':'/','001101':'0'
            ,'011101':'1','011001':'2','010000':'3','001010':'4','000001':'5'
            ,'010101':'6','011100':'7','001100':'8','000011':'9','010110':'?'
            }



def calcbch(binary,gx,b1start,b1end,b2end):        
    bchlist=list(binary[b1start:b1end] +'0'*(b2end-b1end))    
    for i in range(b1end-b1start):    
        if bchlist[i]=='1':           
            for k in range(len(gx)):
                if bchlist[i+k]==gx[k] :                    
                    bchlist[i+k]='0'
                else:                    
                    bchlist[i+k]='1'           
    return ''.join(bchlist)[b1end-b2end:]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getFiveCharChecksum(bcnId):
    returnLimit=1048576 #used to limit the return value to a 20 bit result
    runningSumLimit = 538471 # large prime which will not cause an overflow
    constPrimVal = 3911 #small prime value that stays constant throughout
    modifierLimit = 3847 #small prime which will not cause an overflow
    modifier = 3803 #modifier, simply initialized to a prime value
    runningSum = 0 #variable to hold the running value of the checksum
    tmpLongValue =0 #holds temporary data
    decimalValue =0 #holds decimal value for character
    ## Note: int data type is 4 bytes, largest positive value is 2,147,483,647 and
	##	 all computations are designed to remain within this value (no overflows)
    i=0
    for char in bcnId:
        decimalValue=int(ord(char))
        tmpLongValue =  (runningSum * modifier) + decimalValue
        # on last character here use the higher resolution result as input to final truncation
        if i==len(bcnId)-1:
            runningSum = tmpLongValue % returnLimit
            #print(runningSum)
        else:
            runningSum = tmpLongValue % runningSumLimit
            #print(tmpLongValue,runningSumLimit,runningSum)
            modifier = (constPrimVal * modifier) % modifierLimit
        i += 1
    return str(hex(runningSum)[2:].upper().zfill(5)) #'Checksum: {} ({})'.format(hex(runningSum)[2:].upper().zfill(5),runningSum)


def dec2bin(n,ln=None):
    '''convert denary integer n to binary string bStr'''
    n=int(n)
    bStr = ''
    
    if n < 0:
        raise ValueError("must be a positive integer.")
    #if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    if not ln:
        l=len(bStr)
    else:
        l=ln
    b='0'*(l-len(bStr))+bStr
    return b


def is_neg(s):
    if s<0:
        return -1
    else:
        return 1

def  bin2dec(s):
    try:
        a=int(s,2)
    except ValueError:
        a=0
    return a

def bin2hex2(binval,lpad=0):
    hexstr=str(hex(int(binval, 2)))[2:].upper().strip('L')
    ln=len(hexstr)
    if lpad==0:
        z = ln
    else:
        z = int(lpad)
    return hexstr.zfill(z)

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



def baudot(binstr,startpos,endpos,short=False):
    if short:
        jump=5
        one='1'
    else:
        jump=6
        one=''
    #baudot string values are 6 bit length binary with following code reference
    baudot= BAUDOT
    baudstr=b=''
      
    while startpos < endpos:
        
        try:
            b=baudot[one+binstr[startpos:startpos+jump]]
            
        except KeyError:
            b='?' #__['+ binstr[startpos:startpos+jump] +']__'
        
        startpos+=jump
        baudstr=baudstr+b

    return baudstr
        


def latlongresolution(binary,startpos,endpos):
    #   PDF-2 from 20 or 14 bits starting from bit 113
    #   Standard Location Protocols are 20 bit length ( bits 113 to 132) with from 0-30 minutes resolution adjustment
    #   and 0 to 60 seconds resolution in 4 second increments.
    #   National Location Protocol are 14 bit length - Bits 113 to 126 express 0-3 minute resultions and 0-60 second,(4 sec) increments resolution.
    #   RLS or ELT-DT Location Protocol is 18 bits of data for location offset

    l=endpos-startpos
    DEFAULT = 'Default value'
    if binary[startpos]=='0':                                           #   1 bit (113)
        signlat=-1
        latdir='negative'
    else:
        signlat=1
        latdir='positive'
    


    if l==20:
        # Standard Location Protocol location offset provides 20 data bits from 113 - 132.
        # Five bits resolution for minutes of max 30 minute adjustment
        # 4 bits for seconds resolution from 0 to 60 seconds resolution in 4 second increments
        # See page A-27 of T001

       
        latminutes  =   float(bin2dec(binary[startpos+1:startpos+6]))         #   5 bits 
        latseconds  =   float(bin2dec(binary[startpos+6:startpos+10])* 4 )    #   4 bits
        longminutes =   float(bin2dec(binary[startpos+11:startpos+16]))       #   5 bits
        longseconds =   float(bin2dec(binary[startpos+16:startpos+20])* 4 )   #   4 bits       

        if binary[startpos+10]=='0':                                        #   1 bit
            signlong=-1
            lndir='negative'
        else:
            signlong=1
            lndir='positive'

        if binary[startpos : startpos + 10] == '1000001111':
            latoffset = DEFAULT
        else:
            latoffset = '{} minutes {} seconds ({})'.format(latminutes, latseconds, latdir)

        if binary[startpos + 10 : startpos + 20] == '1000001111':
            longoffset = DEFAULT
        else:
            longoffset = '{} minutes {} seconds ({})'.format(longminutes, longseconds, lndir)



    elif l == 18:

        # RLS or ELT-DT Location Protocol is 18 bits of data from 115 - 132.
        # 4 bits for minutes of max 15 minute adjustment
        # 4 bits for seconds resolution from 0 to 60 seconds resolution in 4 second increments
        # See page A-40 of T.001
        latminutes = float(bin2dec(binary[startpos + 1:startpos + 5]))  # 4 bits
        latseconds = float(bin2dec(binary[startpos + 5:startpos + 9]) * 4)  # 4 bits
        longminutes = float(bin2dec(binary[startpos + 10:startpos + 14]))  # 4 bits
        longseconds = float(bin2dec(binary[startpos + 14:startpos + 18]) * 4)  # 4 bits
        if binary[startpos + 9] == '0':  # 1 bit
            signlong = -1
            lndir = 'negative'
        else:
            signlong = 1
            lndir = 'positive'

        if binary[startpos:startpos + 9] == '100001111':
            latoffset = DEFAULT
        else:
            latoffset = '{} minutes {} seconds ({})'.format(latminutes, latseconds, latdir)

        if binary[startpos + 9:startpos + 18] == '100001111':
            longoffset = DEFAULT
        else:
            longoffset = '{} minutes {} seconds ({})'.format(longminutes, longseconds, lndir)


    elif l==14:
        # National Location Protocol is 14 bits of data from bits 113 - 126.
        # bits 127 - 132 are reserved for national use
        # 2 bits for minutes of max 3 minute adjustment
        # 4 bits for seconds resolution from 0 to 60 seconds resolution in 4 second increments
        # see page A-30 of T.001
        latminutes  =   float(bin2dec(binary[startpos+1:startpos+3]))         #   2 bits   
        latseconds  =   float(bin2dec(binary[startpos+3:startpos+7])*4)       #   4 bits
        longminutes =   float(bin2dec(binary[startpos+8:startpos+10]))       #   2 bits
        longseconds =   float(bin2dec(binary[startpos+10:startpos+14])*4)     #   4 bits
        if binary[startpos+7]=='0':                                         #   1 bit
            signlong=-1
            lndir='negative'
        else:
            signlong=1
            lndir='positive'

        if binary[startpos : startpos + 7] == '1001111':
            latoffset = DEFAULT
        else:
            latoffset = '{} minutes {} seconds ({})'.format(latminutes, latseconds, latdir)

        if binary[startpos + 7 : startpos + 14] == '1001111':
            longoffset = DEFAULT
        else:
            longoffset = '{} minutes {} seconds ({})'.format(longminutes, longseconds, lndir)
        



    else:
        # Bad length.  Length must be 14,18 or 20.
        return False





    return  (signlat*(float(latminutes/60)+float(latseconds/3600)),
             signlong*(float(longminutes/60)+float(longseconds/3600)),             
             latoffset,
             longoffset,signlat,signlong)


def latitudeRLS(latsono,latdeg):    
    if latsono=='1':
        latdir='South'
        sg=-1
    else:
        latdir='North'
        sg=1    
    deg=float(bin2dec(latdeg))/float(2)
    decimal=sg*deg
    if deg>90:
        if '0' not in latdeg:
            lat = decimal = 'Default - no location'
        else:
             lat = decimal = 'Error >90 (Deg:{})'.format(decimal)        
    else:
        lat = str(deg)+' Degrees '+latdir    
    return (lat,decimal,latdir)

def longitudeRLS(longEW,longdeg):    
    if longEW=='0':
        longdir='East'
        sg=1
    else:
        longdir='West'
        sg=-1    
    deg=float(bin2dec(longdeg))/float(2)
    #print longdeg,bin2dec(longdeg)
    decimal=sg*deg
    if deg>180:
        if '0' not in longdeg:
            longe = decimal = 'Default - no location'
        else:
             longe = decimal = 'Error >180 (Deg:{})'.format(decimal)        
    else:
        longe = str(deg)+' Degrees '+longdir    
    return (longe,decimal,longdir)

    
def latitude(latsono,latdeg,latmin):    
    n=1
    if latsono=='1':
        latdir='South'
        sg=-1
    else:
        latdir='North'
        sg=1
        
    if len(latmin)==5:
        n=2
    elif len(latmin)==4:
        n=4
    elif len(latmin)==2:
        n=15       
    
    minutes=float(bin2dec(latmin)*n)
    deg=float(bin2dec(latdeg))
    decimal=sg*(float(deg)+float(minutes/60))
    if deg>90:
        if '0' not in latdeg:
            lat = decimal = 'Default - no location'
        else:
             lat = decimal = 'Error >90 (Deg:{})'.format(decimal)     
        
    else:
        

        lat = str(int(deg))+' Degrees '+str(int(minutes))+' Minutes '+latdir 
    
    
    return (lat,decimal,latdir,minutes)


def bin2hex(binval):
    """Convert binary to hexadecimal

    Args:
        binval (str): binary data in string format
    Returns:
        hex_str (str): hexadecimal string    """

    hex_str = '{:0{}X}'.format(int(binval, 2), len(binval) // 4)

    return hex_str

def longitude(longeswe,longdeg,longmin):
    n=1
    if longeswe=='0':
        lngdir='East'
        sg=1
    else:
        lngdir='West'
        sg=-1
    
    if len(longmin)==5:
        n=2
    elif len(longmin)==4:
        n=4
    elif len(longmin)==2:
        n=15
    minutes=float(bin2dec(longmin)*n)
    deg=float(bin2dec(longdeg))
    decimal=sg*(float(deg)+float(minutes/60))
    if deg>180:
        if '0' not in longdeg:
            
            lng = decimal = 'Default - no location'
            
        else:
            lng = decimal = 'Error! > 180 (Deg:{})'.format(decimal)
            
        
        
    else:
        
        lng =str(int(deg))+' Degrees '+str(int(minutes))+' Minutes '+ lngdir
    
    
    #decimal=deg + float( minutes / 60 )
    
    return (lng,decimal,lngdir,minutes)


def latlongdir(direction):
    if direction in ['South','West']:
        return -1
    else:
        return 1

def samplehex():
    b='10001100110110010'
    
    c='0000000110000010110000001000001111001011010011010000011011011110011011100011100000001111000101110110011'
    c='111111111111111000101111100100111100100100000000000101101011000000000101110101010101001010011010010011001000000000000110001001100100011001001000'
    c='000000000000000000000000100100111100100100000000000101101011000000000101110101010101001010011010010011001000000000000110001001111111011001001000'
    return bin2hex(c),len(c),c

#print(hextobin('3DA6D7095BCAB000AB000ABE000000000004'))
#print(bin2hex('111111111111111000101111100100111100100100000000000101101011000000000101110101010101001010011010010011001000000000000110001001100100011001001000'))
