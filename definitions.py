#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
####################################
# Shared Gen 1 & Gen 2 definitions #
####################################
# Includes 1st and 2nd Gen 

import re

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def bin2hex(binval):
    return str(hex(int(binval, 2)))[2:].upper().strip('L')

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


countrydic = {}
country = open('countries.csv')

for line in country.readlines():
    mid = int(line.split(',')[0].rstrip())
    cname = line.split(',')[1].rstrip()
    countrydic[mid] = cname

baudot = {'111000':'A', '110011':'B', '101110':'C', '110010':'D',
          '110000':'E', '110110':'F', '101011':'G', '100101':'H',
          '101100':'I', '111010':'J', '111110':'K', '101001':'L',
          '100111':'M', '100110':'N', '100011':'O', '101101':'P',
          '111101':'Q', '101010':'R', '110100':'S', '100001':'T',
          '111100':'U', '101111':'V', '111001':'W', '110111':'X',
          '110101':'Y', '110001':'Z', '100100':' ', '011000':'-',
          '010111':'/', '001101':'0', '011101':'1', '011001':'2',
          '010000':'3', '001010':'4', '000001':'5', '010101':'6',
          '011100':'7', '001100':'8', '000011':'9', '010110':'?',
          '000000':'='}



####################
# Gen 1 definiions #
####################


# Beacon Hex Decoding Definitions
protocols = ['Location Protocol', 'User Protocol']


messagetype = {'0':'Short Message', '1':'Long Message'} #bit 25
protocol = {'0':'Location Protocol', '1':'User Protocol'} #bit 26

emergencycode = {'0001':'Fire/explosion',
                 '0010':'Flooding',
                 '0011':'Collision',
                 '0100':'Grounding',
                 '0101':'Listing, in danger of capsizing',
                 '0110':'Sinking',
                 '0111':'Disabled and adrift',
                 '0000':'Unspecified distress',
                 '1000':'Abandoning ship'}

#Bits 84 to 85
auxlocdevice = {'00':'No Auxiliary Radio-locating Device',
                '':'No Auxiliary Radio-locating Device',
                '01':'121.5 MHz Auxiliary Radio-locating Device',
                '10':'9 GHz SART Locating Device',
                '11':'Other Auxiliary Radio-locating Device(s)'
               }

#Bits 37 to 40
locprottype = {'0000':'Unknown location type',
               '0001':'Unknown location type',
               '0010':'Standard Location Protocol EPIRB-MMSI',
               '0110':'Standard Location Protocol - EPIRB (Serial)',
               '1010':'National location protocol - EPIRB',
               '1100':'Std. Location ship security protocol (SSAS)',
               '0011':'Std Loc. ELT 24-bit Address Protocol',
               '0100':'Standard Location Protocol - ELT (Serial)',
               '0101':'Std Loc. Serial ELT - Aircraft Operator Designator Protocol',
               '1000':'National location protocol - ELT',
               '1001':'ELT - DT Location Protocol - ELT',
               '0111':'Standard Location Protocol - PLB (Serial)',
               '1011':'National location protocol - PLB',
               '1101':'RLS Location Protocol',
               '1110':'Standard Location Protocol - Test',
               '1111':'National location protocol - Test'
              }


#Bits 41 to 42 for ELT-DT
eltdt = {'00':'Aircraft 24 bit address',
         '01': 'Aircraft operators designator and serial number',
         '10': 'TAC with serial number',
         '11': 'Location Test Protocol'
        }

stdloctypes = ['0010', '0011', '0100', '0101', '0110', '0111', '1110', '0000', '1100', '0001']
natloctypes = ['1000', '1010', '1011', '1111']

#Bits 37 to 39
userprottype = {'011':'Serial User Protocol (see bits 40 to 42)',
                '001':'ELT Aviation User Protocol',
                '111':'Test User Protocol',
                '110':'Radio Call Sign - EPIRB',
                '000':'Orbitography Protocol',
                '100':'National User Protocol ELT/EPIRB/PLB/TEST',
                '010':'Maritime User Protocol MMSI - EPIRB',
                '101':'Spare - undefined'
               }

#Bits 40 to 42
serialusertype = {'000':'ELT with Serial Identification',
                  '011':'ELT with Aircraft 24-bit Address',
                  '110':'PLB with Serial Identification Number',
                  '010':'Float Free EPIRB with Serial Identification Number',
                  '100':'Non Float Free EPIRB with Serial Identification',
                  '001':'ELT with Aircraft Operator Designator & Serial Number',
                  '111':'Spare',
                  '101':'Spare'
                 }

pselect = {'1':{'ELT':[(userprottype['001'],'1-1-001'),(userprottype['100'],'1-1-100'),
                       ('Serial User '+ serialusertype['000'],'1-1-011-000'),
                       ('Serial User ' +serialusertype['011'],'1-1-011-011'),
                       ('Serial User '+ serialusertype['001'],'1-1-011-001'),
                       (locprottype['0011'],'1-0-0011'),
                       (locprottype['0100'],'1-0-0100'),
                       (locprottype['0101'],'1-0-0101'),
                       (locprottype['1000'],'1-0-1000'),
                       (locprottype['1001'] + ' '+eltdt['00'] ,'1-0-1001-00'),
                       (locprottype['1001'] + ' '+eltdt['01'],'1-0-1001-01'),
                       (locprottype['1001'] + ' '+eltdt['10'],'1-0-1001-10'),
                       (locprottype['1001'] + ' '+eltdt['11'],'1-0-1001-11'),
                       ('ELT RLS location','1-0-1101')],
                'EPIRB':[(userprottype['110'],'1-1-110'),
                         (userprottype['100'],'1-1-100'),
                        ('Serial User '+ serialusertype['100'],'1-1-011-100'),
                        ('Serial User '+ serialusertype['010'],'1-1-011-010'),
                         (userprottype['010'],'1-1-010'),
                         (locprottype['1010'],'1-0-1010'),
                         (locprottype['1100'],'1-0-1100'),
                         (locprottype['0110'],'1-0-0110'),
                         (locprottype['0010'] ,'1-0-0010'),
                         ('EPIRB RLS location' ,'1-0-1101')
                         ],
                'PLB':[(userprottype['100'],'1-1-100'),
                       ('Serial User Protocol '+ serialusertype['110'],'1-1-011-110'),
                        ('PLB '+ locprottype['0111'],'1-0-0111'),
                        (locprottype['1011'],'1-0-1011'),
                        ('PLB - RLS location' ,'1-0-1101')],
                'TEST':[(userprottype['111'],'1-1-111'),
                        (userprottype['000'],'1-1-000'),
                        (userprottype['100'],'1-1-100'),
                        (locprottype['1111'],'1-0-1111'),
                        ('TEST - RLS location' ,'1-0-1101'),
                        ('ELT DT - Test','1-0-1001-11')]},
           '2':{'EPIRB':[('EPIRB - Radio call sign','2-010'),
                         ('EPIRB - MMSI (6 digits)','2-001')
                         ],
                'ELT' : [('ELT - Aircraft marking - tail','2-011'),
                         ('ELT - Aircraft 24 bit address','2-100'),
                         ('ELT - Aircraft operator and Serial Number','2-101')],
                'PLB':  [('PLB -  No aircraft or maritime identity','2-000')]
                }}


class Country:
    def __init__(self,ctrytext,results):
        self.midpat = re.compile(r'(\d{3})')
        self.ctxt=ctrytext
        self.results=results
    def getmid(self):
        try:
            ccode = int(self.midpat.search(self.ctxt).groups()[0])
            return dec2bin(ccode, 10)
        except AttributeError:
            self.results['status'] = 'invalid'
            self.results['message'].append('Country code is required')
            return '0000000000'




class Hexgen:
    def __init__(self,formfields,protocol):
        self.results = {'status': 'valid', 'binary': '', 'hexcode': '', 'message': [],'flderrors' :{}}
        self.formfields=formfields
        self.protocol=protocol
        self.mid=self.getmid()
        self.beacontype = formfields.get('beacontype')
        self.auxdeviceinput = str(formfields.get('auxdeviceinput'))
        self.tano = str(formfields.get('tano_input'))
        self.beacon_gen = 'first'

    def getgen(self):
        return self.beacon_gen

    def beaconbaudot(self):
        beaconno_input = str(self.formfields.get('beaconno_input'))

        if is_number(beaconno_input):
            sno = self.getbaudot(beaconno_input, 1, 1, 'Beacon number must be in range 0-9', 'id_beaconnoerror')
        else:
            self.seterror('Beacon number must be numeric (range 0-9)', 'id_beaconnoerror')
            sno = '001101'
        return sno

    def binhex(self,b,l=0):
        h=""
        if len(b)%4 >0 or (l>0 and len(b)!=l):
            self.seterror('binary length {} not valid.'.format(str(len(b))))
        else:
            h=bin2hex(b)
        return h

    def getmid(self):
        ctry= str(self.formfields.get('country'))
        midpat = re.compile(r'(\d{3})')

        try:
            ccode = int(midpat.search(ctry).groups()[0])
            return dec2bin(ccode, 10)
        except AttributeError:

            self.seterror('Country code is required',"id_miderror")
            return '0000000000'

    def seterror(self,errormsg,fld=""):
        self.results['status'] = 'invalid'
        self.results['message'].append(errormsg)
        if fld:
            self.results['flderrors'][fld] = errormsg

    def getbaudot(self,strval,min, max,errormsg,flderror,short=False):
        bin=''
        if short and not strval.isalpha():
            self.seterror('Only alphabetic characters A-Z', flderror)

        if len(strval)>max or len(strval)<min:
            self.seterror(errormsg,flderror)
        for letter in strval:
            try:
                key = next(key for key, value in baudot.items() if value == letter.upper())
                if short:
                    key=key[1:]
                bin = bin + key
            except StopIteration:
                self.seterror('Input must be alphanumeric',flderror)
        return bin

    def getserial(self,ser,min,max,errormsg,n,flderror):
        bin=''

        if not is_number(ser) or int(ser)<min or int(ser)>max:
            self.seterror(errormsg,flderror)
        else:
            bin=dec2bin(ser,n)
        print(ser,n,bin)
        return bin

    def sethexcode(self, *args):
        binstr=''
        d='-'
        for a in args:
            binstr+=str(a)+d
        binstr=binstr[:-1] #remove last -
        self.results['binary']=binstr
        self.results['hexcode']=self.binhex(''.join(binstr.split(d)))




class Mmsi_location_protocol(Hexgen):
    # EPIRB - MMSI/Location Protocol 1-0-0010 or SAAS 1-0-11000
    def __init__(self,formfields,protocol):
        Hexgen.__init__(self,formfields,protocol)

    def getresult(self):
        radio_or_mmsi_input = str(self.formfields.get('radio_or_mmsi_input'))
        beaconno_input = str(self.formfields.get('beaconno_input'))
        sno = self.getserial(beaconno_input, 0, 15, 'Beacon number must be numeric (range 0-15)', 4 , 'id_beaconnoerror')
        # this is a location protocol.  Can only be numeric.
        if not is_number(radio_or_mmsi_input) or len(radio_or_mmsi_input) > 6:
            # since all numeric, interpret as MMSI last 6 digits
            self.seterror('MMSI must be numeric and max 6 digits','id_radio_or_mmsierror')
        else:
            # must be a location protocol and use decimal conversion
            mmsi = dec2bin(int(radio_or_mmsi_input), 20)
            self.results['binary'] = self.mid + '+'+ dec2bin(int(radio_or_mmsi_input), 20)
            self.sethexcode('0', self.mid, self.protocol.split('-')[2], mmsi,sno,'0111111111','01111111111' )
        return self.results


class Radio_callsign(Hexgen):
    # Radio callsign '1-1-110'
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)
    def getresult(self):
        radio_input = str(self.formfields.get('radio_input'))
        # must have non-numeric therefore be radio call sign
        bin1 = bin2 = pad = ''
        if len(radio_input) > 7:
            self.seterror('Radio call sign must not exceed 7 characters','id_radioerror')
        elif len(radio_input) > 4 and not is_number(radio_input[4:]):
            self.seterror('Radio Callsign last digits need to be numeric','id_radioerror')
        else:
            bin1= self.getbaudot(radio_input[:4],1,4,"Radio Callsign error (at least 1 digit)",'id_radioerror')
            for number in radio_input[4:]:
                bin = dec2bin(number, 4)
                bin2 = bin2 + bin
            radio= bin1 + bin2 + (7 - len(radio_input)) * '1010'
            self.sethexcode('1', self.mid, '110', radio, self.beaconbaudot(), '00', self.auxdeviceinput)
        return self.results

class Aircraftmarking(Hexgen):
    # aviation user protocol '1-1-001'
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        aircraftmarking_input=str(self.formfields.get('aircraftmarking_input'))
        beaconno_input = str(self.formfields.get('beaconno_input'))
        sno = self.getserial(beaconno_input, 0, 3, 'Beacon number must be numeric (range 0-3)', 2, 'id_beaconnoerror')
        acrft=(7 - len(aircraftmarking_input)) * '100100'+self.getbaudot(aircraftmarking_input,1, 7,'First generation aircraft marking maximum 7 characters','id_aircraftmarkingerror')
        self.sethexcode('1',self.mid,'001',acrft,sno,self.auxdeviceinput)
        return self.results

class Maritime_mmsi(Hexgen):
    # Maritime MMSI can be trailing 6 digits or combination of radio callsign (1-1-010)
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        radio_or_mmsi_input = str(self.formfields.get('radio_or_mmsi_input'))
        if is_number(radio_or_mmsi_input):
            if len(radio_or_mmsi_input)>6:
                self.seterror('First generation maritime protocol maximum 6 characters','id_radio_or_mmsierror')
        radio= (6 - len(radio_or_mmsi_input)) * '100100'+ self.getbaudot(radio_or_mmsi_input, 1, 6, 'MMSI or radio marking maximum 6 characters', 'id_radio_or_mmsierror')
        self.sethexcode('1', self.mid, '010', radio, self.beaconbaudot(), '00', self.auxdeviceinput)
        return self.results

class Secondgen(Hexgen):
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        tano = str(formfields.get('tano_input'))
        self.testprotocol=str(formfields.get('testprotocol_input'))
        self.ptype = protocol.split('-')[1]
        self.sn= self.getserial(serialnumber_input, 0, 16383, 'Serial number range (0 - 16,383)', 14, 'id_serialnumbererror')
        self.ta= self.getserial(tano, 0, 65535, 'Type approval number range (0 - 65,535)', 16, 'id_tanoerror')
        self.beacon_gen='second'
    def getresult(self):
        self.sethexcode('1', self.mid, '101', self.ta, self.sn, self.testprotocol,self.ptype, '0'*44 )
        return self.results


class Mmsi_secgen(Secondgen):
    #MMSI 001
    def __init__(self, formfields, protocol):
        Secondgen.__init__(self, formfields,protocol)

    def getresult(self):
        mmsi_input = str(self.formfields.get('mmsi_input'))
        if len(mmsi_input) == 0:
            mmsi=dec2bin(111111,30)
        else:
            mmsi= self.getserial(mmsi_input, 0, 999999, 'Serial number 6 digit maximum range (0 - 999999)', 20, 'id_mmsierror')
            mmsi6digit= (6-len(mmsi_input))*'0' + mmsi_input
            mmsi=dec2bin(str(int(self.mid,2))+ str(mmsi6digit),30)

        epirbais_input = str(self.formfields.get('epirbais_input'))
        if len(epirbais_input) == 0:
            epirbais = dec2bin(10922,14)
        else:
            epirbais= self.getserial(epirbais_input, 0, 9999, 'EPIRB AIS range error (0 - 9999)', 14, 'id_epirbaiserror')

        self.sethexcode('1', self.mid, '101', self.ta, self.sn, self.testprotocol,self.ptype,mmsi, epirbais)
        return self.results


class Radio_secgen(Secondgen):
    #radio call sign 010
    def __init__(self, formfields, protocol):
        Secondgen.__init__(self, formfields,protocol)

    def getresult(self):
        radio_input = str(self.formfields.get('radio_input'))
        radio = self.getbaudot(radio_input, 1, 7, 'Radio callsign maximum 7 characters', 'id_radioerror') +  (7 - len(radio_input)) * '100100' + '00'
        self.sethexcode('1', self.mid, '101', self.ta, self.sn, self.testprotocol,self.ptype,radio)
        return self.results


class Aircraftmarking_secgen(Secondgen):
    #Aircraftmarking - Second Gen 2-011
    def __init__(self, formfields, protocol):
        Secondgen.__init__(self, formfields,protocol)

    def getresult(self):
        aircraftmarking_input = str(self.formfields.get('aircraftmarking_input'))
        aircraftmarking = (7 - len(aircraftmarking_input)) * '100100'+ self.getbaudot(aircraftmarking_input, 1, 7, 'Aircraft marking maximum 7 characters', 'id_aircraftmarkingerror') + '00'
        self.sethexcode('1', self.mid, '101', self.ta, self.sn, self.testprotocol,self.ptype,aircraftmarking)
        return self.results



class Air24bit_secgen(Secondgen):
    #Aircraft 24 bit location 2-100
    def __init__(self, formfields, protocol):
        Secondgen.__init__(self, formfields,protocol)

    def getresult(self):
        elt24bitaddress_serial = str(self.formfields.get('elt24bitaddress_serialuser'))
        sn = self.getserial(elt24bitaddress_serial, 0, 16777215, 'Serial number range (0 - 16,777,215)', 24,'id_elt24biterror')
        self.sethexcode('1', self.mid, '101', self.ta, self.sn, self.testprotocol,self.ptype, sn,'0'*20)
        return self.results




class Aircraftoperator_secgen(Secondgen):
    #Aircraft operator 2-101
    def __init__(self, formfields, protocol):
        Secondgen.__init__(self, formfields,protocol)

    def getresult(self):

        aircraftoperator_input = str(self.formfields.get('aircraftoperator_input'))
        acftop = self.getbaudot(aircraftoperator_input, 3, 3, 'Aircraft operator must be 3 digits','id_aircraftoperatorerror')
        sn_input= str(self.formfields.get('aircraftserial_input'))
        sn= self.getserial(sn_input, 0, 4095, 'Serial number range (0 - 4,095)', 12,'id_aircraftserialerror')
        self.sethexcode('1', self.mid, '101', self.ta, self.sn,self.testprotocol,self.ptype, acftop, sn  ,'1'*14)
        return self.results









class Aircraftoperator(Hexgen):
    # Aircraft operator 011-001 (user)
    # Aircraft operator 0101 (standard location)
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        if self.tano=='0':
            b43='0'
        else:
            b43 = '1'
        aircraftoperator_input = str(self.formfields.get('aircraftoperator_input'))
        acftop=self.getbaudot(aircraftoperator_input,3,3,'Aircraft operator must be 3 digits','id_aircraftoperatorerror')
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 4095, 'Serial number range (0 - 4,095)', 12,'id_serialnumbererror')
        ta = self.getserial(self.tano,0,1023,'Type approval number range (0 - 1,023)',10,'id_tanoerror')
        self.sethexcode('1', self.mid, '011', self.protocol.split('-')[3], b43,acftop, sn, ta,self.auxdeviceinput)
        return self.results


class Aircraftoperator_location(Hexgen):
    # Aircraft operator 0101 (standard location)
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        aircraftoperator_input = str(self.formfields.get('aircraftoperator_input'))
        acftop=self.getbaudot(aircraftoperator_input,3,3,'Aircraft operator must be 3 alphabetic digits','id_aircraftoperatorerror',True)
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 511, 'Serial number range (0 - 511)', 9,'id_serialnumbererror')
        self.sethexcode('0', self.mid, '0101', acftop, sn,'0111111111','01111111111')
        return self.results


class Serial(Hexgen):
    #Serial 011-000, 011-010, 011-100, 011-110
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        if self.tano=='0':
            b43='0'
        else:
            b43 = '1'
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 1048575, 'Serial number range (0 - 1,048,575)', 20,'id_serialnumbererror')
        ta = self.getserial(self.tano,0,1023,'Type approval number range (0 - 1,023)',10,'id_tanoerror')
        self.sethexcode('1', self.mid, '011', self.protocol.split('-')[3], b43, sn, 10*'0', ta,self.auxdeviceinput)
        return self.results

class Air24bit_location(Hexgen):
    #Aircreft 24 bit location 0011
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        elt24bitaddress_serial = str(self.formfields.get('elt24bitaddress_serialuser'))
        sn = self.getserial(elt24bitaddress_serial, 0, 16777215, 'Serial number range (0 - 16,777,215)', 24,'id_elt24biterror')
        self.sethexcode('0', self.mid, self.protocol.split('-')[2],  sn,'0111111111','01111111111' )
        return self.results


class Air24bit_locationdt(Hexgen):
    #Aircreft 24 bit location ELT-DT   1001-00
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        elt24bitaddress_serial = str(self.formfields.get('elt24bitaddress_serialuser'))
        sn = self.getserial(elt24bitaddress_serial, 0, 16777215, 'Serial number range (0 - 16,777,215)', 24,'id_elt24biterror')
        self.sethexcode('0', self.mid, '1001','00', sn,'011111111','0111111111' )
        return self.results


class Serial_location(Hexgen):
    #Serial location 0100, 0110, 0111
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 16383, 'Serial number range (0 - 16,383)', 14,'id_serialnumbererror')
        ta = self.getserial(self.tano,0,1023,'Type approval number range (0 - 1,023)',10,'id_tanoerror')
        self.sethexcode('0', self.mid, self.protocol.split('-')[2], ta , sn,'0111111111','01111111111' )
        return self.results

class Elt_dt_test(Hexgen):
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)
    def getresult(self):
        self.sethexcode('0', self.mid, '100111', '0'*24, '011111111', '0111111111')
        return self.results


class Elt_dt_tasn(Hexgen):

    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 16383, 'Serial number range (0 - 16,383)', 14,'id_serialnumbererror')
        ta = self.getserial(self.tano,0,1023,'Type approval number range (0 - 1,023)',10,'id_tanoerror')
        self.sethexcode('0', self.mid, '100110', ta , sn,'011111111','0111111111' )
        return self.results

class Elt_dt_24bit(Hexgen):
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        elt24bit = str(self.formfields.get('elt24bitaddress_serialuser'))
        sn = self.getserial(elt24bit, 0, 16777215, 'Serial number range (0 - 16,777,215)', 24,'id_elt24biterror')
        self.sethexcode('0', self.mid, '100100',  sn, '011111111','0111111111')
        return self.results


class Elt_dt_aircraft(Hexgen):
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        aircraftoperator_input = str(self.formfields.get('aircraftoperator_input'))
        acftop=self.getbaudot(aircraftoperator_input,3,3,'Aircraft operator must be 3 alphabetic digits','id_aircraftoperatorerror',True)
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 511, 'Serial number range (0 - 511)', 9,'id_serialnumbererror')
        self.sethexcode('0', self.mid, '100101', acftop, sn,'011111111','0111111111')
        return self.results





class Serial24(Hexgen):
    #Serial 1-1-011-011
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        elt24bitaddress_serialuser = str(self.formfields.get('elt24bitaddress_serialuser'))
        beaconno_input =  str(self.formfields.get('beaconno_input'))
        sn= self.getserial(elt24bitaddress_serialuser, 0,16777215,'Serial number range (0 - 16,777,215)',24,'id_elt24biterror')
        ta = self.getserial(self.tano,0,1023,'Type approval number range (0 - 1,023)',10,'id_tanoerror')
        eltno =self.getserial(beaconno_input ,0,63,'Beacon identification number range must be 0 - 63',6,'id_beaconnoerror')
        if self.tano=='0':
            b43='0'
        else:
            b43='1'
        self.sethexcode('1', self.mid, '011', self.protocol.split('-')[3], b43, sn,eltno, ta, self.auxdeviceinput)
        return self.results

class National(Hexgen):
    # National location 1-1-111, 1-1-100, 1-1-111, 1-1-000
    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        nationaluser_input= str(self.formfields.get('nationaluser_input'))
        if nationaluser_input:
            nationaluser = self.getserial(nationaluser_input, 0, 70368744177663, 'Maximum value exceeded', 46,'id_nationalerror')
        else:
            nationaluser=46*'0'
        self.sethexcode('1', self.mid, self.protocol.split('-')[2],nationaluser)
        return self.results

class National_location(Hexgen):
    # National 1-0-1000, 1-0-1010, 1-0-1011, 1-0-1111

    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        nationallocation_input= str(self.formfields.get('nationallocation_input'))
        nationallocation = self.getserial(nationallocation_input, 0, 262143, 'Maximum value (262,143) exceeded', 18,'id_nationallocationerror')
        self.sethexcode('0', self.mid, self.protocol.split('-')[2],nationallocation,'0111111100000','01111111100000')
        return self.results

class Rls_location(Hexgen):
    # RLS Location 1-0-1101

    def __init__(self, formfields, protocol):
        Hexgen.__init__(self, formfields,protocol)

    def getresult(self):
        serialnumber_input = str(self.formfields.get('serialnumber_input'))
        sn = self.getserial(serialnumber_input, 0, 16383, 'Serial number range (0 - 16,383)', 14, 'id_serialnumbererror')
        ta = self.getserial(self.tano, 0, 1023, 'Type approval number range (0 - 1,023)', 10, 'id_tanoerror')
        b=self.beacontype
        beacondic={'ELT':'00','EPIRB':'01','PLB':'10','TEST':'11'}
        self.sethexcode('0', self.mid, self.protocol.split('-')[2],beacondic[b], ta, sn, '011111111', '0111111111')
        return self.results


protocolspecific={
                  '1-1-110' :   Radio_callsign,
                  '1-0-0010':   Mmsi_location_protocol,
                  '1-0-1100':   Mmsi_location_protocol,
                  '1-1-010' :    Maritime_mmsi,
                  '2-000'   :   Secondgen,
                  '2-010'   :    Radio_secgen,
                  '2-001'   :   Mmsi_secgen,
                  '2-011'  :    Aircraftmarking_secgen,
                  '2-100' : Air24bit_secgen,
                  '2-101': Aircraftoperator_secgen,
                  '1-1-001' :     Aircraftmarking,
                  '1-1-011-000': Serial,
                  '1-1-011-010': Serial,
                  '1-1-011-100': Serial,
                  '1-1-011-110': Serial,
                  '1-0-0011' : Air24bit_location,
                  '1-0-1001-00' : Air24bit_locationdt,
                  '1-0-0100': Serial_location,
                  '1-0-0110': Serial_location,
                  '1-0-0111':  Serial_location,
                  '1-1-011-001': Aircraftoperator,
                  '1-0-0101': Aircraftoperator_location,
                  '1-1-011-011': Serial24,
                  '1-1-100': National,
                  '1-1-111': National,
                  '1-1-000': National,
                  '1-0-1000': National_location ,
                  '1-0-1010' : National_location,
                  '1-0-1011' : National_location,
                  '1-0-1111' : National_location,
                  '1-0-1101': Rls_location,
                  '1-0-1001-10' : Elt_dt_tasn,
                  '1-0-1001-11' : Elt_dt_test,
                  '1-0-1001-00' : Elt_dt_24bit,
                  '1-0-1001-01' : Elt_dt_aircraft,

                }




posneg = {'0':'-1', '1':'1'}
dataflag110 = {'0':'Result of bits 113 to 132 defined nationally',
               '1':'Delta position data defined in PDF-2'}

enc_delta_posflag = {'0':'Encoded position data is provided by an external navigation device',
                     '1':'Encoded position data is provided by an internal navigation device'}


enc_alt = {'0000':['0', '400 m (1312 ft)'],
           '0001':['400 m (1312 ft)', '800 m (2625 ft)'],
           '0010':['800 m (2625 ft)', '1200 m (3937 ft)'],
           '0011':['1200 m (3937 ft)', '1600 m (5249 ft)'],
           '0100':['1600 m (5249 ft)', '2200 m (7218 ft)'],
           '0101':['2200 m (7218 ft)', '2800 m (9186 ft)'],
           '0110':['2800 m (9186 ft)', '3400 m (11155 ft)'],
           '0111':['3400 m (11155 ft)', '4000 m (13123 ft)'],
           '1000':['4000 m (13123 ft)', '4800 m (15748 ft)'],
           '1001':['4800 m (15748 ft)', '5600 m (18373 ft)'],
           '1010':['5600 m (18373 ft)', '6600 m (21654 ft)'],
           '1011':['6600 m (21654 ft)', '7600 m (24934 ft)'],
           '1100':['7600 m (24934 ft)', '8800 m (28871 ft)'],
           '1101':['8800 m (28871 ft)', '10000 m (32808 ft)'],
           '1110':['10000 m (32808 ft)', 'greater'],
           '1111':['not available', 'not available']
          }


homer = {'0':'121.5 MHz Homing device not present', '1':'121.5 MHz Homing device present'}


####################
# Gen 2 definiions #
####################

dop = {'0000':'DOP <=1', '0001':'DOP >1 and <=2', '0010':'DOP >2 and <=3',
       '0011':'DOP >3 and <=4', '0100':'DOP >4 and <=5', '0101':'DOP >5 and <=6',
       '0110':'DOP >6 and <=7', '0111':'DOP >7 and <=8', '1000':'DOP >8 and <=10',
       '1001':'DOP >10 and <=12', '1010':'DOP >12 and <=15', '1011':'DOP >15 and <=20',
       '1100':'DOP >20 and <=30', '1101':'DOP >30 and <=50', '1110':'DOP >50',
       '1111':'not available'}

activation_note = {'00':'Manual activation by user',
                   '01':'Automatic activation by the beacon',
                   '10':'Automatic activation by external means',
                   '11':'Spare'}

battery = {'000':'<=5% remaining',
           '001':'>5% and <=10% remaining',
           '010':'>10% and <=25% remaining',
           '011':'>25% and <=50% remaining',
           '100':'>50% and <=75% remaining',
           '101':'>75% and <=100% remaining',
           '110':'reserved for future use',
           '111':'Not available'}

gnss_status = {'00':'No fix',
               '01':'2D location only',
               '10':'3D location',
               '11':'Reserved for future use'}

triggering_event = {'0001':'Manual activation by the crew',
                    '0100':'G-switch/deformation activation',
                    '1000':'Automatic activation from avionics or triggering system'}

inflight_battery = {'00':'<=9 hours autonomy remaining',
                    '01':'>9 and <=18 hours autonomy remaining',
                    '10':'>18 hours autonomy remaining',
                    '11':'Battery capacity not available'}

beacon_distress_type = {'00':'Distress',
               '01':'Distress',
               '10':'Distress',
               '11':'RLS Test Protocol'}


beacon_type = {'000':'ELT (excludes ELT(DT))',
               '001':'EPIRB',
               '010':'PLB',
               '011':'ELT(DT)',
               '100':'Spare',
               '101':'Spare',
               '110':'Spare',
               '111':'Spare'}

beacon_rls = {'00':'No automatic RLM Type-1 received - No manual RLM Type 2 received',
              '01':'No automatic RLM Type 1 received -  Manual RLM Type 2 received ',
              '10':'Automatic RLM Type-1 received - No manual RLM Type 2 received',
              '11':'Automatic RLM Type-1  received - Manual RLM Type 2 received'}

rls_provider = {'001':'GALILEO Return Link Service Provider',
                '010':'GLONASS Return Link Service Provider',
                '000':'spare',
                '011':'spare',
                '100':'spare',
                '101':'spare',
                '110':'spare',
                '111':'spare'}

deactivation = {'00':'Spare',
                '10':'Manual de-activation by user',
                '01':'Automatic de-activation by external means',
                '11':'Spare'}
vessel_id = {'000':'No aircraft or maritime identity (may be for national use; default bits 94-137 all 0)',
             '001':'Maritime MMSI',
             '010':'Radio call sign',
             '011':'Aircraft Registration Marking (Tail Number)',
             '100':'Aircraft aviation 24 Bit Address',
             '101':'Aircraft operator and serial number',
             '110':'Spare',
             '111':'Reserved for System Testing (may contain information; default  bits 94-137 - 0s).Invalid if T-Prot bit-43 - 0'}

baudot2 = {'': '100000', ' ': '100100', '-': '011000', '/': '010111', '1': '011101', '0': '001101',
           '3': '010000', '2': '011001', '5': '000001', '4': '001010', '7': '011100', '6': '010101',
           '9': '000011', '8': '001100', '?': '000000', 'A': '111000', 'C': '101110', 'B': '110011',
           'E': '110000', 'D': '110010', 'G': '101011', 'F': '110110', 'I': '101100', 'H': '100101',
           'K': '111110', 'J': '111010', 'M': '100111', 'L': '101001', 'O': '100011', 'N': '100110',
           'Q': '111101', 'P': '101101', 'S': '110100', 'R': '101010', 'U': '111100', 'T': '100001',
           'W': '111001', 'V': '101111', 'Y': '110101', 'X': '110111', 'Z': '110001'}


moreinfo= {'sgb_radio_callsign':('sgb_radio_callsign',' more instructions ')}

