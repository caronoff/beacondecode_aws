#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
import decodefunctions as Fcn
### -*- coding: utf-8 -*-
import Gen2secondgen as Gen2
import definitions
import time


UIN = 'unique hexadecimal ID'
BCH1='BCH-1 error correcting code'
BCH2='BCH-2 error correcting code'


class Bch:
    def __init__(self, testbin, mtype):
        bch1 = bch2 = bch1error = bch2error = 'na'
        self.complete = '0'
        if mtype in ['Short Msg', 'Long Msg','Short Msg/Long Msg']:
            bch1 = Fcn.calcbch(testbin, "1001101101100111100011", 25, 86, 107)
            bch1error = self.errors(testbin[86:107], bch1)

        if mtype in ['Long Msg','Short Msg/Long Msg']:
            bch2 = Fcn.calcbch(testbin, '1010100111001', 107, 133, 145)
            bch2error = self.errors(testbin[133:145], bch2)
            if bch2error == 'BCH matches encoded BCH':
                self.complete = '1'

        self.bch = (bch1, bch2, testbin[86:107], testbin[133:145], bch1error, bch2error)

    def errors(self, b1, b2):
        e = 0
        for n, bit in enumerate(b1):
            e = e + abs(int(bit) - int(b2[n]))
        if e>0:
            match='NO MATCH WITH ENCODED BCH!!'
        else:
            match='BCH matches encoded BCH'
        return match

    def bcherror(self, n):
        return 'BCH-{} errors: {}'.format(str(n), self.bch[3+int(n)])

    def bch1calc(self):
        return 'Calculated :  {bchcalc}   {e}'.format(bchcalc=self.bch[0], e=self.bch[4])

    def bch2calc(self):
        return 'BCH-2 Calculated (133-144):  {bchcalc}  {e}'.format(bchcalc=self.bch[1], e=self.bch[5])

    def writebch1(self):
        return 'BCH-1 Encoded: {bch1enc}   BCH-1 Calculated:  {bchcalc}  {e}'.format(bch1enc=self.bch[2], bchcalc=self.bch[0], e=self.bch[4])
    def writebch2(self):
        return 'BCH-2 Encoded: {bch2enc}   BCH-2 Calculated:  {bchcalc}   {e}'.format(bch2enc=self.bch[3], bchcalc=self.bch[1], e=self.bch[5])





class HexError(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message

    def __str__(self):
        return repr(self.value, self.message)

class Country:
    def __init__(self, midbin):
        mid = Fcn.bin2dec(midbin)
        try:
            cname = definitions.countrydic[mid]
        except KeyError:
            cname = 'Unknown MID'

        #self.result = 'Country Code (bits 27-36) :({b})  Decimal: {d}   Name: {n}.'.format(b=midbin,d=mid,n=cname)
        self._result = (('Country Code:', mid), ('Country Name:', cname))
        self.cname = "{} - {}".format(cname, mid)
        self.mid = mid
    def countrydata(self):
        s = ''
        for t in self._result:
            for c in t:
                s = s + (str(c)) + '  '
            s = s + '     '
        return s




class BeaconFGB(HexError):
    "decode beacon message hex"
    def __init__(self, strhex=None):

        if strhex:
            self.processHex(str(strhex))

    def processHex(self, strhex):
        self.bchstring = ''
        self.hex15 =''
        self.bch1 = self.bch2 = self.tac = 'na'
        self.courseloc = ('na', 'na')
        self.location = ('na', 'na')
        self.latitude='na'
        self.errors=[]
        self.typeapproval=('','','na')
        self.longitude='na'
        self.fixedbits = ''
        self.hex = str(strhex)
        self.count = 1
        self._loc = False
        self.tablebin = []
        self.type=''
        self.tac=''
        self._loctype=''
        bitsynch=''
        framesynch=''
        if Fcn.hextobin(strhex):
            if len(strhex) == 15:
                #   15 Hex does not use bit 25 - framesynch 24 bits 0 prefix plus bit 25 0 needs to be padded for bit range to match T.001
                self.type = 'uin'
                pad = '0'* 25
            elif len(strhex) == 22:
                # if user does not enter framesynch 6 hex prefix, then need to prefix 24 bits 0
                self.type = 'Short Msg'
                pad = '0' * 24
            elif len(strhex) == 28:
                # if user enters 28 hex including the 6 hex framesynch then likely a short message
                self.type = 'Short Msg'
                pad = ''

            elif len(strhex) == 30:
                self.type = 'Long Msg'
                pad = '0' * 24
            elif len(strhex) == 36:
                pad = ''
                self.type = 'Long Msg'

            else:
                self.type = 'Hex length of ' + str(len(strhex)) + '.' + '\nLength of First Generation Beacon Hex Code must be 15, 22,28, 30 or 36'
                raise HexError('LengthError', self.type)
            self.hexcode=str(strhex)            
            
            
            
        else:
            self.type = 'Not a valid Hex ID'
            raise HexError('FormatError',self.type)         
     
        # make a standard 144 bit (36 Hex) binary string.  '_' in front is to make string operations march the numbering and not start at position 0
        self.bin = '_' + pad + Fcn.hextobin(strhex) + (144 - len(pad + Fcn.hextobin(strhex)))*'0'
        if pad=='':
            bitsynch = self.bin[1:16]
            framesynch = self.bin[16:25]
            self.tablebin.append(['1-15', bitsynch, 'Bit-synchronization pattern consisting of "1"s shall occupy the first 15-bit positions', str(bitsynch=='111111111111111')])
            if self.bin[16:25]== '011010000':
                self.testm='1'
                self.tablebin.append(['16-24', framesynch,'Frame Synchronization Pattern','Correct. Self-Test Message'])
            elif self.bin[16:25]== '000101111':
                self.testm='0'
                self.tablebin.append(['16-24', framesynch, 'Frame Synchronization Pattern', 'Correct. Operational Message'])
            else:
                self.testm=''
                self.tablebin.append(['16-24', framesynch, 'Frame Synchronization Pattern', 'Error. Normal Mode: 000101111'])
                self.tablebin.append(['', '', '', 'Self-Test: 011010000'])

                

        
        self.id=()


        
        if self.type !='uin':
            formatflag=(self.bin[25],definitions.messagetype[self.bin[25]])
            self.tablebin.append(['25', self.bin[25], 'Format Flag', formatflag[1]])
        else:
            formatflag=('n/a','bit 25 not relevant in 15 Hex')
        #if self.type!='uin' and self.bin[25]=='0':
        #    self.type = 'Short Msg'

        protocolflag=self.bin[26]

        self.formatflag=formatflag    
        self.countrydetail=Country(self.bin[27:37])   #self.country()

        #   protocol == '0' :Standard Location Protocol.
        #   type of location protocol is found at bits 37-40
        self._pflag=['Location','User'][int(protocolflag)]


        if self._pflag=='Location':
            pflag='Standard location, National Location, RLS Location or ELT-DT Location protocol '
        else:
            pflag='User protocol'

        self.tablebin.append(['26',self.bin[26],'Protocol Flag',pflag])
        self.tablebin.append(['27-36',self.bin[27:37],'Country code:',self.countrydetail.cname,definitions.moreinfo['country_code']])

        if self.type == 'Short Msg' and self.bin[25] == '1':
            #Long message format should be 30 Hex or 36 Hex but the format flag is long.  Therefore, set type to Long Msg
            self.type = 'Long Msg'
        elif self.type == 'Long Msg' and self.bin[25]=='0':
            # Long message format should be 30 Hex or 36 Hex but the format flag is short.  Therefore, Short Msg
            self.type = 'Short Msg'



        if protocolflag == '0' and self.type != 'Short Msg':
            self.bch = Bch(self.bin, self.type)
            self.locationProtocol()
        #   protocol == '1' 'User Protocol'
        #   type of user protocol located at bits 37-39    
        elif protocolflag == '1' and self.type != 'Short Msg'  :
            self.bch = Bch(self.bin, self.type)
            self.userProtocol()

        if protocolflag == '0' and self.type == 'Short Msg':
            self.tablebin.append(['Inconsistent', 'Error', 'Incomplete', 'Location protocol bit pattern with short message not allowed'])
            self.type='Short Msg/Long Msg'
            self.bch = Bch(self.bin, self.type)
            self.locationProtocol()

        elif protocolflag == '1' and self.type == 'Short Msg':
            self.tablebin.append(['Short Message type', '', '', ''])
            self.bch = Bch(self.bin, self.type)
            self.userProtocol()




    def hexuin(self):
        if self.type =='uin':
            return 'Message is a UIN'
        return self.hex15

    def getmtype(self):
        return self.type

    def testmsg(self):
        if self.bin[16:25] == '011010000':
            return 'Self-test b:16-24: 0 1101 0000'
        elif self.bin[16:25] == '000101111':
            return 'Normal b:16-24: 0 0010 1111'
        return self.bin[16:25]

        
    def get_country(self):
        return Country(self.bin[27:37]).cname

    def get_mid(self):
        return Country(self.bin[27:37]).mid


    def has_loc(self):

        if self.type in ['uin','Short Msg']:
            self._loc=False
        else:
            self._loc=True
        return self._loc
    
    def protocolflag(self):
        return self._pflag


    def country(self):
        return self.countrydetail._result

    def getencpos(self):
        return self.encpos
 
    def protocoldata(self):
        s=''
        for k in sorted(self._protocold):
            s=s+self._protocold[k]+'       '
            
        return s

    def btype(self):
        return self._btype
    
    def loctype(self):
        return self._loctype

    def bch2match(self):
        if self.type=='Long Msg' and self.bch.complete=='1':
            return 'FGB BCH2 calculated matches encoded message'
        elif self.type=='Short Msg':
            return 'BCH-2 na for Short Message Type'
        else:
            return 'Error in BCH2 (no match)'

    def fbits(self):
        return self.fixedbits

    def gettac(self):
        return self.tac

    def userProtocol(self):
        self.hex15=Fcn.bin2hex(self.bin[26:86])
        #self.tablebin.append(['26-85',self.bin[26:86],UIN,self.hex15])
        self._loctype="User"
        self.encpos='na'
        btype='Unknown Beacon'
        tano='na'

        #############################################################################                                                                            #
        #       Bit 37-39: 011: Serial User Protocol                                #
        #       011:    Serial User Protocol                                        #
        #############################################################################

        typeuserprotbin=self.bin[37:40]

        self._loctype=definitions.userprottype[typeuserprotbin]
        self._protocol=('Protocol Flag (Bit 26) :'+ self.bin[26],
                       definitions.protocol[self.bin[26]],
                       'User Protocol Type (bits 37-39) : '+typeuserprotbin,
                       definitions.userprottype[typeuserprotbin])
        self._protocold={'pflag':definitions.protocol[self.bin[26]],
                       'ptype' :definitions.userprottype[typeuserprotbin],'serial':''                     
                       }
                
        if typeuserprotbin=='011':
            #   Bit 37-39: 011: Serial User Protocol (see bits 40 to 42)
            susertype=self.bin[40:43]
            serialtype=definitions.serialusertype[susertype]
            self._protocold['serial']=serialtype
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type','Serial user'])
            self.tablebin.append(['40-42',str(self.bin[40:43]),'Serial type',serialtype])
            self._loctype = 'User: {}'.format(serialtype)
            #   Bit 43 value 1 - Yes for type approval certificate
            if self.bin[43]=='1':  
                tacert='Bit 43 assisgned. Type Approval at bits 74-84.'
                #   Bits 64-73 all 0 or national use
                #   Bits 74-83 is the Type Approval Certificate Number
                tano=str(Fcn.bin2dec((self.bin)[74:84]))
                
            else:
                #   Bits 64-83 is national use or as defined by other protocl
                tacert='Bit 43 not assisgned - no type approval number in Hex'
                tano='na'

            self.tablebin.append(['43',str(self.bin[43]),'TAC',tacert])


            #   Bits 40-42 : 000 : ELT with Serial Identification
            #   Bits 40-42 : 010 : Float free EPIRB with Serial Identification
            #   Bits 40-42 : 100 : Nonfloat free EPIRB with Serial Identification
            #   Bits 40-42 : 110 : PLB with Serial Identification                
            #   Serial ID is from bit 44-63
            
            if susertype in ['000','010','100','110']:
                s1,s2=('Bits 64-73 : '+(self.bin[64:74]),
                          'Serial ID Decimal Value: ' + str(Fcn.bin2dec(self.bin[44:64]))                          
                          )
                auxradiodevice='Aux Radio Device: '+self.bin[84:86]+' '+definitions.auxlocdevice[self.bin[84:86]]
                
                if susertype in ['010','100']:
                    btype='EPIRB'
                elif susertype=='000':
                    btype='ELT'
                elif susertype=='110':
                    btype='PLB'
                self.tablebin.append(['44-63',str(self.bin[44:64]),'Serial Number',str(Fcn.bin2dec(self.bin[44:64]))])
                self.tablebin.append(['64-73',str(self.bin[64:74]),'National use',str(Fcn.bin2dec(self.bin[64:74]))])
                
             
            #   For Serial User Protocol
            #   Bit 40-42 : 011:   ELT with Aircraft 24-bit Address     
            if susertype == '011' : 
                btype,s1,s2=('ELT','Aircraft 24 bit Address (bits 44-67) :Dec value: '+ str(Fcn.bin2dec(self.bin[44:68]))+ '  Hex Value  : '+ Fcn.bin2hex(self.bin[44:68]),
                            'Number of Additional ELTs (bits 68-73):'+str(Fcn.bin2dec(self.bin[68:74])))
                auxradiodevice='Aux Radio Device: '+self.bin[84:86]+' '+definitions.auxlocdevice[self.bin[84:86]]
                emergencycode='Emergency Code (109-112): '
                self.tablebin.append(['44-67',str(self.bin[44:68]),'AirCraft 24 bit identification',str(Fcn.bin2dec(self.bin[44:68]))])
                self.tablebin.append(['68-73', str(self.bin[68:74]), 'Specific beacon number',  str(Fcn.bin2dec(self.bin[68:74]))])

                #   Bit 40-42 : 001 : Aircraft operator designator and serial number
            #   Aircraft Operator is in bits 44-61
            #   Serial ID is from bit 62-73
            
            if susertype == '001' :
                btype,s1,s2=('ELT','AirCraft Operator Designator : '+ Fcn.baudot(self.bin,44,62),
                          'Serial # Assigned by Operator: ' + str(Fcn.bin2dec(self.bin[62:74])))
                auxradiodevice='Aux Radio Device: '+self.bin[84:86]+' '+definitions.auxlocdevice[self.bin[84:86]]
                self.tablebin.append(['44-61',str(self.bin[44:62]),'Aircraft Operator Designator',Fcn.baudot(self.bin,44,62)])
                self.tablebin.append(['62-73',str(self.bin[62:74]),'Serial No Assigned by Operator',str(Fcn.bin2dec(self.bin[62:74]))])
            if susertype in ['111','101']:
                self.tablebin.append(['44-73',str(self.bin[44:74]),'Unknown Serial type',''])
                
            
            self._protocol=('Protocol Flag (Bit 26) :'+ self.bin[26],
                           definitions.protocol[self.bin[26]],
                           typeuserprotbin,definitions.userprottype[typeuserprotbin],
                           susertype,serialtype)
                       

            self.typeapproval=(tacert,'Type Approval ',str(tano))
            self.tac=str(tano)
            
            self.tablebin.append(['74-83',str(self.bin[74:84]),'Type Approval Cert. No:',tano])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
                 
        #############################################################################
        #       Bit 37-39: 000 Orbitography User Protocol                           #
        #############################################################################
        elif typeuserprotbin=='000' :
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type',definitions.userprottype[typeuserprotbin]])
            btype='Orbitography'
            self.tablebin.append(['40-85',str(self.bin[40:86]),'Identification',str(Fcn.bin2hex(self.bin[40:88]))])
            self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
            if self.type not in ['uin','Short Msg']:
                self.tablebin.append(['107-132',str(self.bin[107:133]),'Reserved','Reserved for national use'])
                if int(self.bin[113:])!=0 :
                    self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2,str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])
        #############################################################################
        #       Bit 37-39: 001 ELT Aviation User Protocol                           #
        #############################################################################
        elif typeuserprotbin=='001' :
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type','ELT Aviation User'])
            aircraftid=Fcn.baudot(self.bin,40,82)
            self.tablebin.append(['40-81',str(self.bin[40:82]),'Aircraft ID',aircraftid])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'ELT No',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            btype='ELT'
            self._loctype = 'User: ELT Aviation User'
        #############################################################################
        #       Bit 37-39: 111 : Test User protocol                                 #
        #############################################################################
        elif typeuserprotbin=='111':
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type','Test user'])
            self.tablebin.append(['40-85',str(self.bin[40:86]),'Test Beacon Data',''])
            btype = 'Test'

            if self.type!='uin':
                self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                self.tablebin.append(['107-112', str(self.bin[107:113]), 'Reserved', 'Reserved for test use'])




            if self.type!='Short Msg' and int(self.bin[113:])!=0:
                self.tablebin.append(['113-132',str(self.bin[113:133]),'Test','Reserved for test use'])
                self.tablebin.append(['133-144',
                                      str(self.bin[133:145]),
                                          BCH2,
                                          str(self.bch.bch2calc()),definitions.moreinfo['bch2']])












            self._loctype = 'User: Test User'











        #############################################################################
        #   Bit 37-39: 110 : Radio Call Sign xxx                                    #
        #############################################################################       
        elif typeuserprotbin=='110':
            btype='EPIRB'
            mmsi=bcd=emergencycode=''            
            m=self.bin[40:76]
            pad=''
            a= Fcn.bin2dec(self.bin[64:68])
            b= Fcn.bin2dec(self.bin[68:72])
            c= Fcn.bin2dec(self.bin[72:76])
            if a<9 and b>9 and c>9:
                pad=str(a)
            elif a<9 and b<9 and c>9:
                pad = str(a) + str(b)
            elif a<9 and b<9 and c<9:
                pad = str(a) + str(b)+ str(c)
            else:
                pad=''
            radiocallsign=Fcn.baudot(self.bin,40,64)+pad
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type',definitions.userprottype[typeuserprotbin]])
            self.tablebin.append(['40-75',str(self.bin[40:76]),'Radio call sign',radiocallsign])
            self.tablebin.append(['76-81',str(self.bin[76:82]),'Beacon No',self.bin[76:82]+': ' + Fcn.baudot(self.bin,76,82)])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'Spare No',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])
        #############################################################################
        #   Bit 37-39: 010 Maritime User Protocol                                   #
        #############################################################################               
        elif typeuserprotbin=='010' :
            mmsi='MMSI: '+ Fcn.baudot(self.bin,40,76)
            btype='EPIRB'
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type',definitions.userprottype[typeuserprotbin]])
            self.tablebin.append(['40-75',str(self.bin[40:76]),'MMSI or radio call sign',Fcn.baudot(self.bin,40,76)])
            self.tablebin.append(['76-81',str(self.bin[76:82]),'Specific beacon', Fcn.baudot(self.bin,76,82)])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'Spare bits',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])

        ##############################################################################
        #   Bit 37-39: 100  National User Protocol                                   #
        ##############################################################################        
        elif typeuserprotbin=='100' :
            self._loctype = 'National User'
            self._protocol=(self.bin[26],definitions.protocol[self.bin[26]],typeuserprotbin,definitions.userprottype[typeuserprotbin])
            
            self.tablebin.append(['37-39',str(self.bin[37:40]),'User protocol type',definitions.userprottype[typeuserprotbin]])
            self.tablebin.append(['40-85',str(self.bin[40:86]),'Reserved','Reserved for national use'])
            if self.type!='uin':
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                self.tablebin.append(['107-112',str(self.bin[107:113]),'Reserved','Reserved for national use'])
            if self.type!='Short Msg' and int(self.bin[113:])!=0:
                self.tablebin.append(['113-132',str(self.bin[113:133]),'Reserved','Reserved for national use'])
                self.tablebin.append(['133-144',
                                      str(self.bin[133:145]),
                                          BCH2,
                                          str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])


        if typeuserprotbin not in ['100','000','111'] and self.has_loc(): # and self.bch.complete=='1':
            location_data = 'Check for location'

            self.encpos=str(self.bin[107])
            lat,declat, latdir,ltminutes=Fcn.latitude(self.bin[108],self.bin[109:116],self.bin[116:120])
            lg,declng, lngdir,lgminutes=Fcn.longitude(self.bin[120],self.bin[121:129],self.bin[129:133])

            if self.type!='uin':
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
            if self.type != 'Short Msg' and int(self.bin[113:])!=0 :

                self.tablebin.append(['107',str(self.bin[107]),'Encoded position data source',definitions.enc_delta_posflag[self.encpos]])
                if Fcn.is_number(declat) and Fcn.is_number(declng):
                    self._loc=True
                    a = self.update_locd(declat,latdir)
                    b = self.update_locd(declng,lngdir)
                else:
                    self._loc=False
                    a = declat
                    b = declng
                self.location=(a,b)
                self.latitude=a
                self.longitude=b
                self.tablebin.append(['108-119',str(self.bin[108:120]),'Latitude','{} (decimal: {})'.format(lat,a)])
                self.tablebin.append(['120-132',str(self.bin[120:133]),'Longitude','{} (decimal: {})'.format(lg,b)])
                self.tablebin.append(['','','Resolved location','{} {}'.format(a,b)])
                if 'Error' in lat or 'Error' in lg:
                    self.errors.append('Bad location information')

                self.tablebin.append(['133-144',
                                      str(self.bin[133:145]),
                                          BCH2,
                                          str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
        
        self._btype=btype
        self.tac=str(tano)

        if self.type == 'Short Msg':
            self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
            self.tablebin.append(['107-112', str(self.bin[107:113]), 'Emergency code string', 'See below'])
            emergencycodeflag=str(self.bin[107])
            if emergencycodeflag=='1' :
                if btype=='EPIRB':
                    self.tablebin.append(['107', str(self.bin[107]), 'Emergency code', 'Maritime emergency code flag set'])
                    self.tablebin.append(['108', str(self.bin[108]), 'Activation type',{'0': 'Manual activation only', '1': 'Automatic and manual activation'}[str(self.bin[108])]])
                    self.tablebin.append(['109-112', str(self.bin[109:113]), 'Nature of distress',definitions.naturedistressmaritime[str(self.bin[109:113])]])
                else:
                    self.tablebin.append(['107', str(self.bin[107]), 'Emergency code', 'Non Maritime emergency code flag set'])
                    self.tablebin.append(['108', str(self.bin[108]), 'Activation type',{'0': 'Manual activation only', '1': 'Automatic and manual activation'}[str(self.bin[108])]])
                    self.tablebin.append(['109', str(self.bin[109]), 'Fire', {'0': 'No fire', '1': 'Fire'}[str(self.bin[109])]])
                    self.tablebin.append(['110', str(self.bin[110]), 'Medical help',{'0': 'No medical help required', '1': 'Medical help required'}[str(self.bin[110])]])
                    self.tablebin.append(['111', str(self.bin[111]), 'Disabled',{'0': 'Not disabled', '1': 'Disabled'}[str(self.bin[111])]])
                    self.tablebin.append(['112', str(self.bin[112]), 'Spare', 'Spare'])
            else:
                self.tablebin.append(['107', str(self.bin[107]), 'Emergency code','National use/undefined: 109 to 112 not decoded'])
                self.tablebin.append(['108', str(self.bin[108]), 'Activation type',{'0': 'Manual activation only', '1': 'Automatic and manual activation'}[str(self.bin[108])]])
                self.tablebin.append(['109-112', str(self.bin[109:113]), 'National use','Normally should be 0000'])
        
    def update_locd(self,_dec,_dir):        
        return '{:.3f}'.format(Fcn.latlongdir(_dir)*float(abs(_dec)))

    def locationProtocol(self):      
        
        typelocprotbin=self.bin[37:41]        
        self._locd=dict(lat='not provided',long='not provided',comp='')                          
        tano='na'
        self.encpos='na'
        if typelocprotbin in ['0010','0110','1010','1100']:
            btype='EPIRB'
        elif typelocprotbin in ['0011','0101','0100','1000','1001']:
            btype='ELT'
        elif typelocprotbin in ['0111','1011']:
            btype='PLB'
        elif typelocprotbin=='1110':
            btype='Std Loc Test'
        elif typelocprotbin=='1111':
            btype='Nat Loc Test'
        elif typelocprotbin=='1101' :  #RLS beacon
            trunc='Unknown'
            if self.bin[43:47]!='1111':
                if self.bin[41:43] == '00' :
                    btype='ELT'
                    trunc='2'
                elif self.bin[41:43] == '01' :
                    btype='EPIRB'
                    trunc='1'
                elif self.bin[41:43] == '10' :
                    btype='PLB'
                    trunc='3'
                elif self.bin[41:43] == '11':
                    btype='RLS Loc Test'
                    trunc='?'  # beacon type unknown so therefor indeterminable leading digit
            else:
                if self.bin[41:43] == '00':
                    btype='First EPIRB'
                elif self.bin[41:43] == '01':
                    btype = 'Second EPIRB'
                elif self.bin[41:43] == '10' :
                    btype='PLB'
                elif self.bin[41:43]=='11':
                    btype = 'RLS Test Location'
                
        else:
            btype='Unknown'

        self._protocold={'pflag':definitions.protocol[self.bin[26]],
                       'ptype' :definitions.locprottype[typelocprotbin],'serial':''                     
                       }
       
        self._protocol=('Protocol Flag (Bit 26) :'+ self.bin[26],definitions.protocol[self.bin[26]],
                       'Location Protocol type (bits 37-40) : '+typelocprotbin,
                       definitions.locprottype[typelocprotbin],typelocprotbin)
   
                

        ident=('')
        
        #Standard Location protocols
        if typelocprotbin in definitions.stdloctypes : #['0010','0011','0100','0101','0110','0111','1100','1110']

            default='011111111101111111111'
            self._loctype=definitions.locprottype[typelocprotbin]
            self._loc = False
            
            self.hex15=Fcn.bin2hex(self.bin[26:65]+default)
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Protocol Code', definitions.locprottype[typelocprotbin]])
            #self.tablebin.append(['26-85',self.bin[26:65]+default,UIN,self.hex15])
            latdelta,longdelta,ltoffset,lgoffset = Fcn.latlongresolution(self.bin,113,133)
            lat,declat, latdir,ltminutes=Fcn.latitude(self.bin[65],self.bin[66:73],self.bin[73:75])
            lng,declng, lngdir,lgminutes=Fcn.longitude(self.bin[75],self.bin[76:84],self.bin[84:86])          
            self.courseloc=(declat,declng)

            
            #   EPIRB MMSI
            if typelocprotbin=='0010':                
                ident=('MMSI ID Number: ',str(Fcn.bin2dec(self.bin[41:61])),'Specific Beacon :',str(Fcn.bin2dec(self.bin[61:65])))
                self.tablebin.append(['41-60',str(self.bin[41:61]),'MMSI ID No',str(Fcn.bin2dec(self.bin[41:61]))])
                self.tablebin.append(['61-64',str(self.bin[61:65]),'Specific beacon No',str(Fcn.bin2dec(self.bin[61:65]))])
         

            #   ELT 24 bit address
            elif typelocprotbin=='0011':
                
                
                self.tablebin.append(['41-64',str(self.bin[41:65]),'Aircraft ID No','{} ({})'.format(str(Fcn.bin2dec(self.bin[41:65])),str(Fcn.bin2hex(self.bin[41:65])))])

            #   ELT - Aircraft Operator Designator Standard Location Protocol
            elif typelocprotbin=='0101':
                
                self.tablebin.append(['41-64',str(self.bin[41:65]),
                                      'ELT Operator ID',
                                      '{} ELT No:{}'.format(str(Fcn.baudot(self.bin,41,55,True)),str(Fcn.bin2dec(self.bin[56:65])))])
            
            #   PLB, ELT and EBIRB Serial
            elif typelocprotbin in ['0100','0110','0111']:
                tano = str(Fcn.bin2dec(self.bin[41:51]))
                self.tablebin.append(['37-40',str(self.bin[37:41]),'Beacon type','{}'.format(btype)])
                self.tablebin.append(['41-50',str(self.bin[41:51]),'Type Approval Cert. No:',tano])
                self.tablebin.append(['51-64',str(self.bin[51:65]),'Serial No',str(Fcn.bin2dec(self.bin[51:65]))])
                self.typeapproval=('','',tano)
                self.tac = str(tano)
            elif typelocprotbin == '1110':                
                self.tablebin.append(['41-65',str(self.bin[41:66]),'No decode identification',definitions.locprottype[typelocprotbin]])
                

            if self.type not in ['uin','Short Msg']:
                self.tablebin.append(['65-74',str(self.bin[65:75]),'Latitude','{} ({})'.format(lat,declat)])
                self.tablebin.append(['75-85',str(self.bin[75:86]),'Longitude','{} ({})'.format(lng,declng)])

                
                if self.bin[107:111]=='1101':
                    computed='107-110 should be 1101.  Passed.'
                else:
                    computed= '107-110 :'  + self.bin[107:111] + '. Not  1101. Failed'

                self.fixedbits=computed
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                self.tablebin.append(['107-110',str(self.bin[107:111]),'Validity',computed])
                self.tablebin.append(['111',
                                      str(self.bin[111]),
                                          'Encoded position',
                                          definitions.enc_delta_posflag[self.bin[111]]])

                self.tablebin.append(['112',
                                      str(self.bin[112]),
                                          '121.5 Mhz Homing Device',
                                          definitions.homer[self.bin[112]]])
                self.encpos=str(self.bin[111])
                if int(self.bin[113:]) != 0:
                    self.tablebin.append(['113-122',str(self.bin[113:123]),'Latitude offset', ltoffset])
                    self.tablebin.append(['123-132', str(self.bin[123:133]),'Longitude offset', lgoffset])
                    self.tablebin.append(['133-144', str(self.bin[133:145]),BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            
            elif self.type=='uin':
                if default==str(self.bin[65:86]):
                    valid='Valid'
                else:
                    valid='ERROR:  bits not default'
                self.tablebin.append(['65-85',default,'Default bits required','Defined by T.001 for Unique identifier'])
                self.tablebin.append(['65-85', str(self.bin[65:86]), 'Default bits in hex', valid])
                self._loc=False

        #   National Location protocols - PLB, ELT and EPIRB
        elif typelocprotbin in definitions.natloctypes: #['1000','1010','1011','1111']:            
            

            self._loctype='National Location'                         
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Location protocol','{} {}'.format(btype,self._loctype),definitions.moreinfo['natloc']])
            default='011111110000001111111100000'
            #59-85 default data 27 bit binary (to construct 15 Hex UIN when no location present)
            self.hex15=Fcn.bin2hex(self.bin[26:59]+default)
            #self.tablebin.append(['26-85',self.bin[26:59]+default,UIN,self.hex15])
            ident= ('Serial Number :',str(Fcn.bin2dec(self.bin[41:59])))            
            self.tablebin.append(['41-58',str(self.bin[41:59]),'Identification Data (decimal)','#{}'.format(str(Fcn.bin2dec(self.bin[41:59]))),definitions.moreinfo['natloc']])
            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset =(0, 0, 0, 0, 0, 0, 0, 0)
            lat,declat,latdir,ltminutes =  Fcn.latitude(self.bin[59],self.bin[60:67],self.bin[67:72])
            lng,declng,lngdir,lgminutes =  Fcn.longitude(self.bin[72],self.bin[73:81],self.bin[81:86])
            self.courseloc=(declat,declng)
            if self.type not in ['uin', 'Short Msg']:
                self.tablebin.append(['59-71',str(self.bin[59:72]),'Latitude','{} ({})'.format(lat,declat)])
                self.tablebin.append(['72-85',str(self.bin[72:86]),'Longitude','{} ({})'.format(lng,declng)])
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                if self.bin[107:110]=='110':
                    computed='107-109 should be 110.  Passed.'
                else:
                    computed= '107-109 :'  + self.bin[107:110] + '. Not  110. Failed'
                self.tablebin.append(['107-109',str(self.bin[107:110]),'Validity',computed])
                self.fixedbits=computed
                finallat=finallng='Not Used'            
                self._locd['encpos']=definitions.enc_delta_posflag[self.bin[111]]
            
                if self.bin[110]=='0':
                    self._locd['comp']='Value 0: bits 113-132 for national use'
                    latdelta=longdelta=0
                    self.tablebin.append(['110',str(self.bin[110]),
                                          'Location check',
                                          self._locd['comp']])
                    self.tablebin.append(['111',
                                          str(self.bin[111]),
                                          'Location source',
                                          self._locd['encpos']])
                    
                    self.tablebin.append(['112',
                                          str(self.bin[112]),
                                          'Aux device',
                                          definitions.homer[self.bin[112]]])
                    if int(self.bin[113:]) != 0:
                        self.tablebin.append(['113-132',str(self.bin[113:133]),'National use',''])


                    
                else :

                    latdelta,longdelta,ltoffset,lgoffset = Fcn.latlongresolution(self.bin,113,127)


                    self.tablebin.append(['110',str(self.bin[110]),
                                          'Location check',
                                          'bits 113-126 for location.\n 127-132 for national use'])
                    
                    self.tablebin.append(['111',
                                          str(self.bin[111]),
                                          'Location source',
                                          definitions.enc_delta_posflag[self.bin[111]]])
                    self.encpos=str(self.bin[111])
                    self.tablebin.append(['112',
                                          str(self.bin[112]),
                                          'Aux device',
                                          definitions.homer[self.bin[112]]])

                
                    if int(self.bin[113:]) != 0:
                        self.tablebin.append(['113-119',str(self.bin[113:120]),'Latitude offset',ltoffset])
                        self.tablebin.append(['120-126',str(self.bin[120:127]),'Longitude offset',lgoffset])
                        self.tablebin.append(['127-132',str(self.bin[127:133]), 'National use',''])

                if int(self.bin[113:]) != 0:
                    self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])

            elif self.type=='Short Msg':
                self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])

            elif self.type=='uin':
                if default==str(self.bin[59:86]):
                    valid='Valid'
                else:
                    valid='ERROR: bits not default'
                self.tablebin.append(['59-85',default,'Default bits required','Defined by T.001 for Unique identifier'])
                self.tablebin.append(['59-85', str(self.bin[59:86]), 'Default bits in hex', valid])
                self._loc=False
            
        # RLS Location Protocol 
        elif typelocprotbin =='1101':
            default='0111111110111111111' #67-85 default 19 bit binary (to construct 15 Hex)
            self.hex15=Fcn.bin2hex(self.bin[26:67]+default)
            #self.tablebin.append(['26-85',self.bin[26:67]+default,UIN,self.hex15])
            self._loctype=definitions.locprottype[typelocprotbin]
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Location protocol','{}'.format(self._loctype)])
            tano=str(Fcn.bin2dec(self.bin[43:53])).zfill(3)
            self.tablebin.append(['41-42',str(self.bin[41:43]),'Beacon type',btype])
            if self.bin[43:47]=='1111':
            # RLS for MMSI
                idtype='RLS protocol coded with MMSI last 6 digits'
                self.tablebin.append(['43-46', str(self.bin[43:47]), 'Identification type', idtype])
                self.tablebin.append(['47-66', str(self.bin[47:67]), 'Last 6 digits MMSI','{}'.format(str(Fcn.bin2dec(self.bin[47:67])).zfill(6))])
            else:
            # RLS for TAC number or National RLS with serial number
                idtype = 'RLS protocol coded with TAC or National RLS and Serial Number'
                self.tablebin.append(['43-46', str(self.bin[43:47]), 'Identification type', idtype])
                self.tablebin.append(['43-52',str(self.bin[43:53]),'RLS TAC# truncated or national assigned RLS','{}'.format(tano),definitions.moreinfo['rls_trunc']])
                self.tablebin.append(['', '', 'RLS TAC included missing leading digit prefix', '{}{}'.format(trunc,tano)])
                self.tablebin.append(['53-66',str(self.bin[53:67]),'Production or National assigned serial No','{}'.format(str(Fcn.bin2dec(self.bin[53:67])).zfill(5))])

            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset =(0,0,0,0,0,0,0,0)
            lat,declat,latdir =  Fcn.latitudeRLS(self.bin[67],self.bin[68:76])           
            lng,declng,lngdir =  Fcn.longitudeRLS(self.bin[76],self.bin[77:86])
            self.courseloc=(declat,declng)
            if self.type not in ['uin', 'Short Msg']:
                self.tablebin.append(['67-75',str(self.bin[67:76]),'Latitude','{} ({})'.format(lat,declat)])
                self.tablebin.append(['76-85',str(self.bin[76:86]),'Longitude','{} ({})'.format(lng,declng)])
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                #self.tablebin.append(['107-108',str(self.bin[107:109]),'supplementary','supplementary'])
                self._locd['encpos']=definitions.enc_delta_posflag[self.bin[107]]
                self.encpos=str(self.bin[107])
                self._locd['homer']=definitions.homer[self.bin[108]]
                self.tablebin.append(['107',str(self.bin[107]),'Encoded position source',self._locd['encpos']])
                self.tablebin.append(['108',str(self.bin[108]),'121.5 Mhz Homing Device',self._locd['homer']])
                #self.tablebin.append(['109-114',str(self.bin[109:115]),'RLS specific bits','See below'])
                self.tablebin.append(['109', str(self.bin[109]), 'Beacon capability to process and automatically generated RLM Type-1', ['Not capable to process an automatically generated RLM Type-1','Capable to process an automatically generated RLM Type-1'][int(self.bin[109])]])
                self.tablebin.append(['110', str(self.bin[110]), 'Beacon capability to process a manually generated RLM Type-1 RLM Type-2',['Not capable to process a manually generated RLM Type-2','Beacon able to process a manually generated RLM Type-2'][int(self.bin[110])]])
                self.tablebin.append(['111', str(self.bin[111]), 'Beacon Feedback on receipt of RLM Type-1',
                                      ['RLM Type-1 (automatic) not received by this beacon',
                                       'RLM Type-1 (automatic) received by this beacon'][int(self.bin[111])]])
                self.tablebin.append(['112', str(self.bin[112]), 'Beacon Feedback on receipt of RLM Type-2',
                                      ['RLM Type-2 (manual) not received by this beacon',
                                       'RLM Type-2 (manual) received by this beacon'][int(self.bin[112])]])
                finallat = finallng = 'Not Used'
                if int(self.bin[113:]) != 0:
                    self.tablebin.append(['113-114', str(self.bin[113:115]), 'RLS Provider Identification', {'00':'Spare','11':'Spare','01':'GALILEO Return Link Service Provider','10':'GLONASS Return Link Service Provider'}[str(self.bin[113:115])]])

                    latdelta,longdelta,ltoffset,lgoffset = Fcn.latlongresolution(self.bin,115,133)
                    self.tablebin.append(['115-123',str(self.bin[115:124]),'Latitude offset',ltoffset])
                    self.tablebin.append(['124-132',str(self.bin[124:133]),'Longitude offset',lgoffset])
                    self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            elif self.type=='uin':
                if default == str(self.bin[67:86]):
                    valid = 'Valid'
                else:
                    valid = 'ERROR: bits not default'
                self.tablebin.append(['67-85', default, 'Default bits required', 'Defined by T.001 for Unique identifier'])
                self.tablebin.append(['67-85', str(self.bin[67:86]), 'Default bits in hex', valid])


                self._loc = False

            elif self.type=='Short Msg':
                self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])

        # ELT-DT Location Protocol   
        elif typelocprotbin == '1001':
            default='0111111110111111111' #67-85 default 19 bit binary (to construct 15 Hex UIN)
            self.hex15=Fcn.bin2hex(self.bin[26:67]+default)
            #self.tablebin.append(['26-85',self.bin[26:67]+default,UIN,self.hex15])
            self._loctype='ELT-DT Location'
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Location protocol','{} {}'.format(btype,self._loctype)])            
            self.tablebin.append(['41-42',str(self.bin[41:43]),'ELT Type',definitions.eltdt[str(self.bin[41:43])]])
            if str(self.bin[41:43])=='10':
            # 10 bit TAC & Serial No
                tano=str(Fcn.bin2dec(self.bin[43:53]))
                self.tablebin.append(['43-52',str(self.bin[43:53]),'Tac No','#{}'.format(tano)])                      
                self.tablebin.append(['53-66',str(self.bin[53:67]),'Serial No','#{}'.format(str(Fcn.bin2dec(self.bin[53:67])))])
            elif str(self.bin[41:43])=='00':
            #24 bit aircraft address
                self.tablebin.append(['43-66',str(self.bin[43:67]),'Aircraft 24 bit address','#{}'.format(str(Fcn.bin2dec(self.bin[43:67])))])
            elif str(self.bin[41:43])=='01':
            # Aircraft operator designator
                self.tablebin.append(['43-57',str(self.bin[43:58]),'Aircraft Operator Designator (15 bit)',Fcn.baudot(self.bin,43,58,True),definitions.moreinfo['elt_dt_aircraftoperator']])
                self.tablebin.append(['58-66',str(self.bin[58:67]),'Serial No Assigned by Operator',str(Fcn.bin2dec(self.bin[58:67]))])
            elif str(self.bin[41:43])=='11':
            # ELT(DT) Location Test Protocol
                self.tablebin.append(['43-66',str(self.bin[43:67]),'ELT(DT) Location Test Protocol','reserved'])

            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset =(0,0,0,0,0,0,0,0)
            lat,declat,latdir =  Fcn.latitudeRLS(self.bin[67],self.bin[68:76])           
            lng,declng,lngdir =  Fcn.longitudeRLS(self.bin[76],self.bin[77:86])
            self.courseloc=(declat,declng)

            if self.type!='uin':
                if str(self.bin[67:86]) == '1111110101111111010': #type is ELT-DT cancellation message
                    pass
                    self.tablebin.append(['67-75', str(self.bin[67:76]), 'ELT-DT Cancellation message pattern: {}'.format('1 11111010'),'Cancellation message'])
                    self.tablebin.append(['76-85', str(self.bin[76:86]),  'ELT-DT Cancellation message pattern: {}'.format('1 111111010'),'Cancellation message'])
                    self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                    if str(self.bin[107:133]) == '00111100011110000011110000': #make sure pattern is correct
                        self.tablebin.append(['107-132', str(self.bin[107:133]), 'Bit pattern is valid for cancellation message', 'Calcellation message'])
                    else:
                        self.tablebin.append(['107-132', str(self.bin[107:133]), 'Bit pattern invalid','Calcellation message bit pattern wrong'])
                    if int(self.bin[113:])!=0:
                        self.tablebin.append(['133-144', str(self.bin[133:145]), BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])

                else: #proceed to decode location
                    self.tablebin.append(['67-75',str(self.bin[67:76]),'Latitude','{} ({})'.format(lat,declat)])
                    self.tablebin.append(['76-85',str(self.bin[76:86]),'Longitude','{} ({})'.format(lng,declng)])
                    self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                    means = {'01':'automatic activation by the beacon','11':'spare','00':'manual activation by user','10':'automatic activation by external means'}
                    meansbin = str(self.bin[107:109])
                    self.tablebin.append(['107-108',meansbin,'means of activation',means[meansbin]])
                    enc_altbin=str(self.bin[109:113])
                    enc_altstr='altitude is between {} and {}'.format(definitions.enc_alt[enc_altbin][0],definitions.enc_alt[enc_altbin][1])
                    self.tablebin.append(['109-112',enc_altbin,'encoded altitude',enc_altstr])
                    finallat=finallng='Not Used'
                    enc_loc_fresh = {'01':'message between 1 and 5 min old','11':'message current','00':'message >5 min old','10':'message >2 sec. and <60 sec. old'}
                    enc_freshbin=str(self.bin[113:115])
                    if int(self.bin[113:]) != 0:
                        self.tablebin.append(['113-114',enc_freshbin,'Encoded location freshness',enc_loc_fresh[enc_freshbin]])
                        latdelta,longdelta,ltoffset,lgoffset = Fcn.latlongresolution(self.bin,115,133)
                        self.tablebin.append(['115-123',str(self.bin[115:124]),'Latitude offset',ltoffset])
                        self.tablebin.append(['124-132',str(self.bin[124:133]),'Longitude offset',lgoffset])
                        self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2,str(self.bch.bch2calc()),definitions.moreinfo['bch2']])

            elif self.type=='uin':
                if default == str(self.bin[67:86]):
                    valid = 'Valid'
                else:
                    valid = 'ERROR:  bits not default'
                self.tablebin.append(['67-85', default, 'Default bits required', 'Defined by T.001 for Unique identifier'])
                self.tablebin.append(['67-85', str(self.bin[67:86]), 'Default bits in hex', valid])

                self._loc = False
        if Fcn.is_number(declat) and Fcn.is_number(latdelta) and Fcn.is_number(declng) and Fcn.is_number(longdelta):
            self._loc=True
            a=self.update_locd((abs(declat)+latdelta),latdir)         
            b=self.update_locd((abs(declng)+longdelta),lngdir)
        else:
            self._loc=False
            a=declat
            b=declng

            
        if self._loc:
            self.tablebin.append(['','','Composite location','{} {}'.format(a,b)])
            self.location=(a,b)
            self.latitude= a
            self.longitude = b
        else:
            self.location = (0, 0)
            self.latitude = 0
            self.longitude = 0


        self._btype=btype
        self.tac=str(tano)


        



class Beacon(HexError):
    def __init__(self,hexcode):
        genmsgdic={'63':'The code consists of 63 hexadecimal characters representing a 252 bit messgage format from a second generation beacon, including 48 bits of BCH error correcting bit as defined by T.018 Issue 1 - Rev.4.',
                   '15sgb':'The code consists of 15 hexadecimal characters representing a truncated 23 Hex ID for an SGB as defined by T.018 Issue 1 - Rev.4.',
                   '22':'The code consists of 22 hexadecimal characters representing a first gerneration beacon short message as defined by T.001 Issue 4 - Rev.6).',
                   '22long': 'The code consists of 22 hexadecimal characters representing a first generation beacon message with a Long format flag(30 hex trunctated to 22 excluding BCH-2).  Forrmat specifications are defined by T.001 Issue 4 - Rev.6).',
                   '30short': 'The code consists of 30 hexadecimal characters representing a first generation beacon message with format flag set to Short.   FGB short message format specifications 22 hex and truncate last 8 hex digits (as per T.001 Issue 4 - Rev.6).',
                   '15':'Hex data entered is a 15 Hex ID unique identifier based on FGB specifications (as per T.001 Issue 4 - Rev.5).',
                   '23': 'Hex data length of 23 consistent with Hex unique identifier based on SGB specifications (as per T.018 Issue 1 - Rev.4).',
                   '51': 'Hex data entered is a length of 51 characters representing a 204 bit (00 + 202 bit) consistent with SGB specifications, excluding BCH (as per T.018 Issue 1 - Rev.4).  The decoded message below computes the BCH portion of the message and associated hex characters for information purposes.',
                   '30':'Hex data length of 30 forms complete 30 hex message consistent with FGB long message format specifications (as per T.001 Issue 4 - Rev.6).',
                   '28': 'Hex data length of 28 character hexadecimal consistent with first generation beacon short message format specifications including 24 bit(6hex) framesynch prefix as defined by T.001 Issue 4 - Rev.6 Section 2.2.2.4.',
                   '28long': 'The code consists of 28 hexadecimal characters representing a first generation beacon message with the format flag set to Long including bit and frame synchronization pattern as defined by T.001 Issue 4 - Rev.6.',
                   '36short': 'The code consists of 36 hexadecimal characters representing a first generation beacon message with the format flag set to Short including bit and frame synchronization pattern prefix (24 bits) as defined by T.001 Issue 4 - Rev.6.',
                   '36': 'The code consists of 36 hexadecimal characters representing a first generation beacon message with the format flag set to Long including bit and frame synchronization pattern prefix (24 bits) as defined by T.001 Issue 4 - Rev.6.'}
        self.genmsg=''
        if not Fcn.hextobin(hexcode):
            raise HexError('Hex format Error', 'This is not a valid hexadecimal value!')

        if len(hexcode) == 63 or len(hexcode) == 51 :
            beacon = Gen2.SecondGen(hexcode)
            self.gentype ='second'
            if len(hexcode) == 63:
                self.genmsg = genmsgdic['63']
            elif len(hexcode) == 51:
                beacon = Gen2.SecondGen(hexcode)
                self.genmsg = genmsgdic['51']

        elif len(hexcode) == 23:
            beacon = Gen2.SecondGen(hexcode)
            self.gentype = 'second'
            self.genmsg = genmsgdic['23']

        elif len(hexcode) == 15:
            if Fcn.hextobin(hexcode)[0]=='1' and Fcn.hextobin(hexcode)[11:14]=='101':
                self.gentype = 'secondtruncated'
                beacon = Gen2.SecondGen(hexcode+8*'0')
                self.genmsg = genmsgdic['15sgb']
            else:
                self.gentype = 'first'
                beacon = BeaconFGB(hexcode)
                self.genmsg = genmsgdic['15']+' Computed Checksum : '+Fcn.getFiveCharChecksum(hexcode)

        elif len(hexcode) == 30 :

            beacon=BeaconFGB(hexcode)
            self.gentype='first'


            if beacon.type == 'Short Msg':
                self.genmsg = genmsgdic['30short']
            else:
                self.genmsg = genmsgdic['30']

        elif len(hexcode) == 22 :
            # check if this is a short message or a long message without the BCH2
            beacon=BeaconFGB(hexcode)
            self.gentype='first'

            if beacon.type == 'Long Msg':
                self.genmsg = genmsgdic['22long']
            else:
                self.genmsg = genmsgdic['22']

        elif len(hexcode) == 28:
            beacon = BeaconFGB(hexcode)
            self.gentype = 'first'
            if beacon.type == 'Long Msg':
                self.genmsg = genmsgdic['28long']
            else:
                self.genmsg = genmsgdic['28']

        elif len(hexcode) == 36:
            beacon=BeaconFGB(hexcode)
            self.gentype = 'first'
            if beacon.type in ['Short Msg','Short Msg/Long Msg']:
                self.genmsg = genmsgdic['36short']
            else:
                self.genmsg = genmsgdic['36']



        else:
            self.type = 'Hex length of ' + str(
                len(hexcode)) + '.' + '\nValid Lengths: FGB: 15,22,28 30 or 36.  SGB: 15, 23 or 63'
            raise HexError('Length Error', self.type)
            self.beacon=None



        self.beacon=beacon
        self.latitude=self.beacon.latitude
        self.longitude=self.beacon.longitude
        self.location=self.beacon.location
        self.courseloc=self.beacon.courseloc
        self.tablebin=self.beacon.tablebin
        self.bchstring=self.beacon.bchstring
        self.type = self.beacon.type
        self.errors = self.beacon.errors

    def has_loc(self):
        if self.beacon.type=='uin' or self.beacon.location==(0,0):
            return False
        elif self.beacon.latitude in ['No latitude data available','Invalid Latitude','na','Default - no location (Default - no location)'] or\
                        self.beacon.longitude in ['No longitude data available', 'Invalid Longitude','Default - no location (Default - no location)','na']:
            return False
        else:
            return True

    def btype(self):
        return self.beacon.btype()

    def hexuin(self):
        return self.beacon.hexuin()

    def bchmatch(self):
        return self.beacon.bchmatch()

    def gettac(self):
        return self.beacon.gettac()

    def loctype(self):
        return self.beacon.loctype()

    def fbits(self):
        return self.beacon.fbits()

    def testmsg(self):
        return self.beacon.testmsg()

    def getencpos(self):
        return self.beacon.getencpos()

    def get_country(self):
        return self.beacon.get_country()

    def get_mid(self):
        return self.beacon.get_mid()

def beaconcountry(hexcode):
    try:
        beacon = Beacon(hexcode)
        ctry = beacon.get_country()
    except HexError as e:
        ctry = e.message

    return ctry
