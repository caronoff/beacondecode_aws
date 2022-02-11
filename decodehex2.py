#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
import decodefunctions as Fcn
import Gen2functions as Func
### -*- coding: utf-8 -*-
import Gen2secondgen as Gen2
import definitions
import time
import bch1correct as bch1
import bch2correct as bch2



UIN = 'unique hexadecimal ID'
BCH1='BCH-1 error correcting code'
BCH2='BCH-2 error correcting code'
BCH_ERRORS_PRESENT ='BCH errors present in message'
INVALID_UIN =' (INVALID UIN) Per DDP section 4.2.1.1.4, due to errors in message, cannot construct valid UIN therefore bits 26-85 not defaulted'
SHORT_MSG = 'Short Msg'
LONG_MSG = 'Long Msg'
SHORT_OR_LONG_MSG = 'Short Msg/Long Msg'
UIN = 'unique hexadecimal ID'
INVALID_HEX = 'Not a valid Hex ID'
LOCATION_PROTOCOL_FLAG = 'Location, further information provided in "Protocol Code" '
USER_PROTOCOL_FLAG = 'User, further information provided in "Protocol Code" '

class Bch:
    def __init__(self, testbin, mtype):
        bch1 = bch2 = bch1error = bch2error = 'na'
        self.complete = '0'
        bch1errors=bch2errors=0

        if mtype in [SHORT_MSG, LONG_MSG,SHORT_OR_LONG_MSG]:
            bch1 = Fcn.calcbch(testbin, "1001101101100111100011", 25, 86, 107)
            bch1errors = self.errors(testbin[86:107], bch1)

        if mtype in [LONG_MSG,SHORT_OR_LONG_MSG]:
            bch2 = Fcn.calcbch(testbin, '1010100111001', 107, 133, 145)
            bch2errors = self.errors(testbin[133:145], bch2)
            if bch2errors == 0:
                self.complete = '1'

        self.bch = (bch1, bch2, testbin[86:107], testbin[133:145], bch1errors, bch2errors)
        self.bch1errors=bch1errors
        self.bch2errors = bch2errors

    def errors(self, b1, b2):
        e = 0
        for n, bit in enumerate(b1):
            e = e + abs(int(bit) - int(b2[n]))

        return e

    def bcherror(self, n):
        return 'BCH-{} errors: {}'.format(str(n), self.bch[3+int(n)])

    def bch1calc(self):
        result=''
        if self.bch[4]==0:
            result='BCH-1 code in message matches the recalculated BCH-1 from the PDF-1 field'
        else:
            result='ERROR! BCH-1 code in message does not match the recalculated BCH-1 from the PDF-1 field. (recalculated value:{bchcalc})'.format(bchcalc=self.bch[0])
        return result

    def bch2calc(self):
        result = ''
        if self.bch[5] == 0:
            result = 'BCH-2 code in message matches the recalculated BCH-2 from the PDF-2 field'
        else:
            result = 'ERROR! BCH-2 code in message does not match the recalculated BCH-2 from the PDF-2 field. (recalculated value:{bchcalc})'.format(bchcalc=self.bch[1])
        return result

    def writebch1(self):
        return 'BCH-1 Encoded: {bch1enc}   BCH-1 Calculated:  {bchcalc} BCH 1 errors: {e}'.format(bch1enc=self.bch[2], bchcalc=self.bch[0], e=self.bch[4])
    def writebch2(self):
        return 'BCH-2 Encoded: {bch2enc}   BCH-2 Calculated:  {bchcalc}  BCH 2 errors: {e}'.format(bch2enc=self.bch[3], bchcalc=self.bch[1], e=self.bch[5])





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
            cname = definitions.countrydic[str(mid)]
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
        self.strhex=strhex
        self.bchstring = ''
        self.hex15 =''
        self.bad='bad call'
        self.bch_valid = 'na'
        self.bch1 = self.bch2 = self.tac = 'na'
        self.courseloc = ('na', 'na')
        self.location = ('na', 'na')
        self.latitude='na'
        self.threeletter ='na'
        self.altitude = 'na'
        self.errors=[]
        self.warnings=[]
        self.typeapproval=('','','na')
        self.longitude='na'
        self.testprotocol='na'
        self.selftest='Normal mode transmission (not self-test i.e., operational mode)'
        self.fixedbits = ''
        self.hex = str(strhex)
        self.count = 1
        self._loc = False
        self.cancellation = False
        self.sgb_spare_bits = 'na'
        self.tablebin = []
        self.type=''
        self.tac=''
        self._loctype=''
        self._sn='na'
        self._id='na'
        bitsynch=''
        framesynch=''
        correct_bch_errors=strhex
        if Fcn.hextobin(strhex):
            if len(strhex) == 15:
                #   15 Hex does not use bit 25 - framesynch 24 bits 0 prefix plus bit 25 0 needs to be padded for bit range to match T.001
                self.type = 'uin'
                pad = '0'* 25
            elif len(strhex) == 22:
                # if user does not enter framesynch 6 hex prefix, then need to prefix 24 bits 0
                self.type = SHORT_MSG
                pad = '0' * 24
            elif len(strhex) == 28:
                # if user enters 28 hex including the 6 hex characters for 24 bit frame synch, then a short message type
                self.type = SHORT_MSG
                pad = ''

            elif len(strhex) == 30:
                self.type = LONG_MSG
                ## Error correction attempt for when BCH portion does not match recomputed
                _pdf1 = (Fcn.hextobin(strhex))[:61]
                _bch1 = (Fcn.hextobin(strhex))[61:82]
                bitflips1,newpdf1,newbch1 = bch1.pdf1_to_bch1(_pdf1,_bch1)
                _pdf2=(Fcn.hextobin(strhex))[82:108]
                _bch2=(Fcn.hextobin(strhex))[108:]
                bitflips2,newpdf2,newbch2 = bch2.pdf2_to_bch2(_pdf2,_bch2)
                if bitflips1 ==-1 or bitflips2 ==-1:
                    self.bch_valid = 'Message has too many bit errors to correct on bch'
                #     self.errors.append('Too many bit errors to correct')
                elif bitflips1>0 or bitflips2 > 0:
                    _newbin=newpdf1 + newbch1 + newpdf2 + newbch2
                    self.bch_valid = '{} bit errors corrected.  Corrected Msg` ,{}'.format(bitflips1 + bitflips2,Fcn.bin2hex(_newbin))
                    # self.errors.append(' {} bad pdf1 bit and {} bad pdf2 bit'.format(bitflips1, bitflips2))
                    # self.errors.append('Corrected Message: {} '.format(Fcn.bin2hex(_newbin)))
                    # print(_newbin,len(_newbin),len(newpdf1),len(newbch1),len(newpdf2),len(newbch2))
                else:
                    self.bch_valid='Message has no bch errors'

                pad = '0' * 24
            elif len(strhex) == 36:
                pad = ''
                self.type = LONG_MSG

            else:
                self.type = 'Hex length of ' + str(len(strhex)) + '.' + '\nLength of First Generation Beacon Hex Code must be 15, 22,28, 30 or 36'
                raise HexError('LengthError', self.type)
            self.hexcode=str(strhex)

        else:
            self.type = INVALID_HEX
            raise HexError('FormatError',self.type)         
     
        # make a standard 144 bit (36 Hex) binary string.  '_' in front is to make string operations march the numbering and not start at position 0
        self.bin = '_' + pad + Fcn.hextobin(strhex) + (144 - len(pad + Fcn.hextobin(strhex)))*'0'
        if self.bin[37:40] =='101' and self.bin[26]=='1':
        # illegal protocol for FGB user protocol
            self.type = 'Bits 37-39 are 101 which is reserved for SGB but the valid hex length should be 51 or 63'
            raise HexError('Beacon Generation conflict', self.type)

        if pad=='':
            bitsynch = self.bin[1:16]
            framesynch = self.bin[16:25]
            self.tablebin.append(['1-15', bitsynch, 'Bit-synchronization pattern consisting of "1"s shall occupy the first 15-bit positions', str(bitsynch=='111111111111111')])
            if self.bin[16:25]== '011010000':
                self.selftest='Test protocol message coded for non-operational use'
                self.tablebin.append(['16-24', framesynch,'Frame Synchronization Pattern',self.selftest])
            elif self.bin[16:25]== '000101111':
                self.selftest='Normal beacon operation'
                self.tablebin.append(['16-24', framesynch, 'Frame Synchronization Pattern', self.selftest])
            else:
                self.selftest='INVALID FRAME SYNCHRONIZATION'
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
            pflag=LOCATION_PROTOCOL_FLAG
        else:
            pflag=USER_PROTOCOL_FLAG

        self.tablebin.append(['26',self.bin[26],'Protocol Flag',pflag])
        self.tablebin.append(['27-36',self.bin[27:37],'Country code:',self.countrydetail.cname,definitions.moreinfo['country_code']])
        self.tablebin.append(['', '', 'For associated SAR Points of Contact (SPOC) related to {} :'.format(self.countrydetail.cname), '<a href="https://cospas-sarsat.int/en/contacts-pro/contacts-details-all"  > Search Contact list here </a>'])

        if 'Unknown MID' in self.countrydetail.cname:
            self.errors.append('Unknown Country Code')

        if self.type == SHORT_MSG and self.bin[25] == '1':
            #Long message format should be 30 Hex or 36 Hex but the format flag is long.  Therefore, set type to Long Msg
            self.type = LONG_MSG
        elif self.type == LONG_MSG and self.bin[25]=='0':
            ## Long message format should be 30 Hex or 36 Hex but the format flag takes priority to define method type.
            # Therefore, in this case bit 25 is 0 even though length size appears long, we deem this Short Msg
            self.type = SHORT_MSG

        if protocolflag == '0' and self.type != SHORT_MSG:
            self.bch = Bch(self.bin, self.type)
            self.locationProtocol()
        #   protocol == '1' 'User Protocol'
        #   type of user protocol located at bits 37-39    
        elif protocolflag == '1' and self.type != SHORT_MSG :
            self.bch = Bch(self.bin, self.type)
            self.userProtocol()

        if protocolflag == '0' and self.type == SHORT_MSG:
            e='Location protocol (bit 26 is 0) for short message not allowed'
            self.errors.append(e)
            #self.tablebin.append(['Inconsistent', 'Error', 'Incomplete', e])
            self.type=SHORT_OR_LONG_MSG
            self.bch = Bch(self.bin, self.type)
            self.locationProtocol()

        elif protocolflag == '1' and self.type == SHORT_MSG:
            #self.tablebin.append(['Short Message type', '', '', ''])
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

    def bchmatch(self):
        e='No errors'
        e1=e2=""
        if len(self.bin) >= 60 and (self.bch.bch1errors > 0 or self.bch.bch2errors > 0) :
            e=''
            if (self.bch.bch1errors > 0):
                e1='COMPUTED BCH1 DOES NOT MATCH ENCODED BCH1!!'
            elif (self.bch.bch2errors > 0):
                e2='COMPUTED BCH2 DOES NOT MATCH ENCODED BCH2!!'
        return e + e1 + ":" +e2


    def get_country(self):
        return Country(self.bin[27:37]).cname

    def get_mid(self):
        return Country(self.bin[27:37]).mid

    def get_id(self):
        return self._id

    def get_sn(self):
        return self._sn

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
        self._loctype="User"
        self.encpos='na'
        btype='Unknown Beacon'
        tano='na'
        typeuserprotbin = self.bin[37:40]
        if (self.bch.bch1errors > 0 or self.bch.bch2errors>0) and len(self.strhex)>28 and typeuserprotbin!='000':
            self.errors.append(BCH_ERRORS_PRESENT)

        #############################################################################
        #       Bit 37-39: 011: Serial User Protocol                                #
        #       011:    Serial User Protocol                                        #
        #############################################################################


        self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])

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
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code','Serial user'])
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
                tacert='Bit 43 not assisgned - no type approval number assigned in message.  Bits 64-83 are reserved for national use and control'
                tano='na  Nationally Assigned - bit 43 is Zero'

            self.tablebin.append(['43',str(self.bin[43]),'TAC',tacert])


            #   Bits 40-42 : 000 : ELT with Serial Identification
            #   Bits 40-42 : 010 : Float-free EPIRB with Serial Identification
            #   Bits 40-42 : 100 : Non float-free EPIRB with Serial Identification
            #   Bits 40-42 : 110 : PLB with Serial Identification
            #   Bit 43 : value 1 -> Yes for type approval certificate : value 0 -> national use
            #   bit 44-63 : Serial ID
            
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
                self._sn =str(Fcn.bin2dec(self.bin[44:64]))
                self.tablebin.append(['44-63',str(self.bin[44:64]),'Serial Number',self._sn])
                if self.bin[43] == '1':
                    self.tablebin.append(['64-73',str(self.bin[64:74]),'All Zero or National use',str(Fcn.bin2dec(self.bin[64:74]))])
                    self.tablebin.append(['74-83', str(self.bin[74:84]), 'Type Approval Cert. No:', tano])
                else:
                    self.tablebin.append(['64-83', str(self.bin[64:84]), ' National use', 'National use'])
             
            #   For Serial User Protocol - Bit 37-39 : =011
            #   Bit 40-42 : =011:   ELT with Aircraft 24-bit Address
            if susertype == '011' : 
                btype,s1,s2=('ELT','Aircraft 24 bit Address (bits 44-67) :Dec value: '+ str(Fcn.bin2dec(self.bin[44:68]))+ '  Hex Value  : '+ Fcn.bin2hex(self.bin[44:68]),
                            'Number of Additional ELTs (bits 68-73):'+str(Fcn.bin2dec(self.bin[68:74])))
                auxradiodevice='Aux Radio Device: '+self.bin[84:86]+' '+definitions.auxlocdevice[self.bin[84:86]]
                emergencycode='Emergency Code (109-112): '
                self._id='{} hex ({} decimal)'.format(str(Fcn.bin2hex2(self.bin[44:68],6)),Fcn.bin2dec(self.bin[44:68]))
                self.tablebin.append(['44-67',str(self.bin[44:68]),
                                      'AirCraft 24 bit identification',self._id ])
                self._sn=str(Fcn.bin2dec(self.bin[68:74]))
                self.tablebin.append(['68-73', str(self.bin[68:74]), 'Specific beacon serial number',self._sn  ])

                self.tablebin.append(['74-83', str(self.bin[74:84]), 'Type Approval Cert. No:', tano])



                #   Bit 40-42 : 001 : Aircraft operator designator and serial number
            #   Aircraft Operator is in bits 44-61
            #   Serial ID is from bit 62-73
            
            if susertype == '001' :
                self._id = Fcn.baudot(self.bin, 44, 62)
                self._sn=str(Fcn.bin2dec(self.bin[62:74]))
                btype,s1,s2=('ELT','AirCraft Operator Designator : '+ self._id,
                          'Serial # Assigned by Operator: ' + self._sn)
                auxradiodevice='Aux Radio Device: '+self.bin[84:86]+' '+definitions.auxlocdevice[self.bin[84:86]]
                self.tablebin.append(['44-61',str(self.bin[44:62]),'Aircraft Operator Designator',self._id])
                self.tablebin.append(['62-73',str(self.bin[62:74]),'Serial No Assigned by Operator',self._sn])
            if susertype in ['111','101']:
                if self.bin[43]=='1':
                    self.tablebin.append(['44-73',str(self.bin[44:74]),'Unknown Serial type','No information in T.001 to decode'])
                    self.tablebin.append(['74-83', str(self.bin[74:84]), 'Type Approval Cert. No:', tano])
                else:
                    self.tablebin.append(['44-83', str(self.bin[44:84]), 'Unknown Serial type', 'No information in T.001 to decode'])

            
            self._protocol=('Protocol Flag (Bit 26) :'+ self.bin[26],
                           definitions.protocol[self.bin[26]],
                           typeuserprotbin,definitions.userprottype[typeuserprotbin],
                           susertype,serialtype)

            self.typeapproval=(tacert,'Type Approval ',str(tano))
            self.tac=str(tano)
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
                 
        #############################################################################
        #       Bit 37-39: 000 Orbitography User Protocol                           #
        #############################################################################
        elif typeuserprotbin=='000' :
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code',definitions.userprottype[typeuserprotbin]])
            btype='Orbitography beacon'
            self._id=str(Fcn.bin2hex(self.bin[40:88]))
            orbitspec="""
            Seven character orbitography beacon clear text identifier using the modified 
            Baudot code (see C/S T.001). The seven characters shall be right justified. 
            Characters not used shall be filled with the "space" character (100100)
            """
            self.tablebin.append(['40-81',str(self.bin[40:82]), orbitspec,Fcn.baudot(self.bin,40,82)])
            self.tablebin.append(['82-85', str(self.bin[82:86]), 'Defined as 4 binary 0 by T.006', ''])
            if self.type!='uin':
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                self.tablebin.append(['107', str(self.bin[107]), 'National use defined by T.006', 'Set bit to 0'])
                self.tablebin.append(['108-112', str(self.bin[108:113]), 'National use defined by T.006', 'National use'])
            if self.type not in ['uin','Short Msg']:
                self.tablebin.append(['113-144',str(self.bin[113:]),'Optional long message','Reserved for national use'])
                #if int(self.bin[113:])!=0 :
                #    self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2,str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])

        #############################################################################
        #       Bit 37-39: 001 ELT Aviation User Protocol                           #
        #############################################################################
        elif typeuserprotbin=='001' :
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code','ELT Aviation User'])
            aircraftid=Fcn.baudot(self.bin,40,82)
            self.tablebin.append(['40-81',str(self.bin[40:82]),'Aircraft ID',aircraftid])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'ELT No',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            btype='ELT'
            self._loctype = 'User: ELT Aviation User'
            self._id=aircraftid
        #############################################################################
        #       Bit 37-39: 111 : Test User protocol                                 #
        #############################################################################
        elif typeuserprotbin=='111':
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code','Test user'])
            self.tablebin.append(['40-85',str(self.bin[40:86]),'Test Beacon Data',''])
            btype = 'Test'
            self.testprotocol ='test protocol mode transmission'

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

            first4chars = ''
            last3char=''

            for s in range(40,64,6) :
                char=Fcn.baudot(self.bin,s,s+6)
                first4chars = first4chars + char
                if char == '?':
                    e="Invalid radio call-sign value of '{}' for bit range {}-{} (baudot not decodable)".format(self.bin[s:s+6],str(s),str(s+6))
                    self.errors.append(e)


            for s in range(64,76,4) :
                char=Fcn.bin2dec(self.bin[s:s+4])
                if char<10:
                    last3char = last3char + str(char)
                elif char == 10:
                    last3char = last3char + '_'
                elif char > 10:
                    e="Invalid radio call-sign value of '{}' for bit range {}-{}".format(self.bin[s:s+4],str(s),str(s+4))
                    self.errors.append(e)
                    last3char = last3char + '?'

            radiocallsign=first4chars+last3char
            if '_' in radiocallsign:
                radiocallsign = radiocallsign + "   (padding spaces '_') "
            if '?' in radiocallsign:
                radiocallsign = ' Errors present: ' + radiocallsign


            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code',definitions.userprottype[typeuserprotbin]])
            self.tablebin.append(['40-75',str(self.bin[40:76]),'Radio call sign',radiocallsign])
            self.tablebin.append(['76-81',str(self.bin[76:82]),'Beacon No',self.bin[76:82]+': ' + Fcn.baudot(self.bin,76,82)])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'Spare No',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])
            self._id=radiocallsign
        #############################################################################
        #   Bit 37-39: 010 Maritime User Protocol                                   #
        #############################################################################               
        elif typeuserprotbin=='010' :
            mmsi='MMSI: '+ Fcn.baudot(self.bin,40,76)
            btype='EPIRB'
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code',definitions.userprottype[typeuserprotbin]])
            self.tablebin.append(['40-75',str(self.bin[40:76]),'MMSI or radio call sign',Fcn.baudot(self.bin,40,76)])
            self.tablebin.append(['76-81',str(self.bin[76:82]),'Specific beacon', Fcn.baudot(self.bin,76,82)])
            self.tablebin.append(['82-83',str(self.bin[82:84]),'Spare bits',str(Fcn.bin2dec(self.bin[82:84]))])
            self.tablebin.append(['84-85',str(self.bin[84:86]),'Auxiliary radio device',definitions.auxlocdevice[self.bin[84:86]]])
            self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])
            self._id='{}-{}'.format(Fcn.baudot(self.bin,40,76),Fcn.baudot(self.bin,76,82))
        ##############################################################################
        #   Bit 37-39: 100  National User Protocol                                   #
        ##############################################################################        
        elif typeuserprotbin=='100' :
            self._loctype = 'User: National User'
            self._protocol=(self.bin[26],definitions.protocol[self.bin[26]],typeuserprotbin,definitions.userprottype[typeuserprotbin])
            
            self.tablebin.append(['37-39',str(self.bin[37:40]),'Protocol Code',definitions.userprottype[typeuserprotbin]])
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
            #self._loctype = 'User: {}'.format(definitions.userprottype[typeuserprotbin])


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

        if self.type == 'Short Msg' and typeuserprotbin!='000':
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
                    btype='RLS Location unknown beacon type (Spare or Test)'
                    self.testprotocol = 'test protocol mode transmission ' + btype
                    trunc='[Unkown beacon type]'  # beacon type unknown so therefor indeterminable leading digit
            else:
                if self.bin[41:43] == '00':
                    btype='First EPIRB'
                elif self.bin[41:43] == '01':
                    btype = 'Second EPIRB'
                elif self.bin[41:43] == '10' :
                    btype='PLB'
                elif self.bin[41:43]=='11':
                    btype = 'RLS Test Location'
                    self.testprotocol = 'test protocol mode transmission ' + btype
                
        else:
            btype='Unknown'

        if typelocprotbin[:3]=='111':
            self.testprotocol = 'test protocol mode transmission ' + btype

        self._protocold={'pflag':definitions.protocol[self.bin[26]],
                       'ptype' :definitions.locprottype[typelocprotbin],'serial':''                     
                       }
       
        self._protocol=('Protocol Flag (Bit 26) :'+ self.bin[26],definitions.protocol[self.bin[26]],
                       'Location Protocol type (bits 37-40) : '+typelocprotbin,
                       definitions.locprottype[typelocprotbin],typelocprotbin)
   
                

        ident=('')
        # undefined location protocol types
        if typelocprotbin in ['0000','0001']:
            default = '011111111101111111111'
            if self.bch.bch1errors > 0 or (self.bch.bch2errors > 0 and int(self.bin[113:]) != 0):
                self.errors.append(BCH_ERRORS_PRESENT)
            self._loctype = "Location: {}".format(definitions.locprottype[typelocprotbin])
            self._loc = False
            self.tablebin.append(['37-40', str(self.bin[37:41]), 'Protocol Code', definitions.locprottype[typelocprotbin]])
            self.tablebin.append(['41-85', str(self.bin[41:86]), 'Undefined - Spare ', 'Undefined for undefined location type'])
            latdelta, longdelta, ltoffset, lgoffset,signlat,signlong = Fcn.latlongresolution(self.bin, 113, 133)
            lat, declat, latdir, ltminutes = Fcn.latitude(self.bin[65], self.bin[66:73], self.bin[73:75])
            lng, declng, lngdir, lgminutes = Fcn.longitude(self.bin[75], self.bin[76:84], self.bin[84:86])
            self.courseloc = (declat, declng)
            self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()), definitions.moreinfo['bch1']])
            self.tablebin.append(['107-132', str(self.bin[107:133]), 'Undefined - Spare ', 'Undefined for undefined location type'])
            self.tablebin.append(['133-144', str(self.bin[133:145]), BCH2, str(self.bch.bch2calc()), definitions.moreinfo['bch2']])
            declat='na'
        #Standard Location protocols
        if typelocprotbin in definitions.stdloctypes : #['0010','0011','0100','0101','0110','0111','1100','1110']
            default = '011111111101111111111'
            if self.bch.bch1errors>0 or (self.bch.bch2errors>0 and int(self.bin[113:])!=0):
                self.errors.append(BCH_ERRORS_PRESENT)
            self._loctype = "Location: {}".format(definitions.locprottype[typelocprotbin])
            self._loc = False
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Protocol Code', definitions.locprottype[typelocprotbin]])

            #self.tablebin.append(['26-85',self.bin[26:65]+default,UIN,self.hex15])
            latdelta,longdelta,ltoffset,lgoffset,signlat,signlong = Fcn.latlongresolution(self.bin,113,133)
            lat,declat, latdir,ltminutes=Fcn.latitude(self.bin[65],self.bin[66:73],self.bin[73:75])
            lng,declng, lngdir,lgminutes=Fcn.longitude(self.bin[75],self.bin[76:84],self.bin[84:86])          
            self.courseloc=(declat,declng)
            
            #   EPIRB MMSI
            if typelocprotbin=='0010':                
                ident=('MMSI ID Number: ',str(Fcn.bin2dec(self.bin[41:61])),'Specific Beacon :',str(Fcn.bin2dec(self.bin[61:65])))
                self.tablebin.append(['41-60',str(self.bin[41:61]),'MMSI ID No',str(Fcn.bin2dec(self.bin[41:61]))])
                self.tablebin.append(['61-64',str(self.bin[61:65]),'Specific beacon No',str(Fcn.bin2dec(self.bin[61:65]))])
                self._id='{}-{}'.format(str(Fcn.bin2dec(self.bin[41:61])),str(Fcn.bin2dec(self.bin[61:65])))
            #   ELT 24 bit address
            elif typelocprotbin=='0011':
                self._id='{} hex ({} decimal)'.format(str(Fcn.bin2hex2(self.bin[41:65],6)),str(Fcn.bin2dec(self.bin[41:65])))
                self.tablebin.append(['41-64',str(self.bin[41:65]),
                                      'Aircraft 24 bit address', self._id])
            #   ELT - Aircraft Operator Designator Standard Location Protocol
            elif typelocprotbin=='0101':
                self._id = str(Fcn.baudot(self.bin, 41, 56, True))
                self._sn = str(Fcn.bin2dec(self.bin[56:65]))
                self.tablebin.append(['41-55',str(self.bin[41:56]),'15 bit Operator designator',self._id])
                if '?' in self._id:
                    self.errors.append('"?" in 15 bit Operator Designator means invalid bits in field.' )

                self.tablebin.append(['56-64', str(self.bin[56:65]),
                                      '9 bit Serial Number Assigned (1-511)', self._sn])
            
            #   PLB, ELT and EBIRB Serial
            elif typelocprotbin in ['0100','0110','0111']:
                tano = str(Fcn.bin2dec(self.bin[41:51]))
                self.tablebin.append(['37-40',str(self.bin[37:41]),'Beacon type','{}'.format(btype)])
                self.tablebin.append(['41-50',str(self.bin[41:51]),'Type Approval Cert. No:',tano])
                self._sn = str(Fcn.bin2dec(self.bin[51:65]))
                self.tablebin.append(['51-64',str(self.bin[51:65]),'Serial No',str(Fcn.bin2dec(self.bin[51:65]))])
                self.typeapproval=('','',tano)
                self.tac = str(tano)
            elif typelocprotbin == '1110':                
                self.tablebin.append(['41-64',str(self.bin[41:65]),'Test protocol','No Decode information in bits 41 to 64'])

            if self.type not in ['uin','Short Msg']:
                self.tablebin.append(['65-74',str(self.bin[65:75]),'Latitude','{} ({})'.format(lat,declat)])
                self.tablebin.append(['75-85',str(self.bin[75:86]),'Longitude','{} ({})'.format(lng,declng)])
                
                if self.bin[107:111]=='1101':
                    computed='107-110 should be 1101'
                else:
                    if typelocprotbin in ['0000','0001']:
                        computed= '107-110 : derived ('  + self.bin[107:111] + ')  Normally 1101 for operational beacon but valid for undefined location type (spare)'
                    else:
                        computed = '107-110 : derived (' + self.bin[107:111] + ') Error - Should be 1101 for operational location protocol beacon'
                        self.errors.append(computed)

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
                #if int(self.bin[113:]) != 0 :
                self.tablebin.append(['113-122',str(self.bin[113:123]),'Latitude offset', ltoffset])
                self.tablebin.append(['123-132', str(self.bin[123:133]),'Longitude offset', lgoffset])
                self.tablebin.append(['133-144', str(self.bin[133:145]),BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            
            elif self.type=='uin':
                if default==str(self.bin[65:86]):
                    valid='Valid'
                else:
                    valid='Bits not default'
                    self.errors.append(valid)
                self.tablebin.append(['65-85',default,'Default bits required','Defined by T.001 for Unique identifier'])
                self.tablebin.append(['65-85', str(self.bin[65:86]), 'Default bits in hex', valid])
                self._loc=False
            if self.errors:
                self.hex15 = Fcn.bin2hex(self.bin[26:86]) #+ INVALID_UIN
                self.errors.append(Fcn.bin2hex(self.bin[26:86]) + INVALID_UIN)
            else:
                self.hex15 = Fcn.bin2hex(self.bin[26:65] + default )


        #   National Location protocols - PLB, ELT and EPIRB
        elif typelocprotbin in definitions.natloctypes: #['1000','1010','1011','1111']:

            self._loctype='Location: National Location'
            default = '011111110000001111111100000'
            if self.bch.bch1errors > 0 or self.bch.bch2errors > 0:
                self.hex15 = Fcn.bin2hex(self.bin[26:86]) #+ INVALID_UIN
                self.errors.append(BCH_ERRORS_PRESENT)
                self.errors.append(Fcn.bin2hex(self.bin[26:86]) + INVALID_UIN)
            else:
                self.hex15 = Fcn.bin2hex(self.bin[26:59] + default)

            self.tablebin.append(['37-40',str(self.bin[37:41]),'Protocol Code','{} {}'.format(btype,self._loctype),definitions.moreinfo['natloc']])

            #59-85 default data 27 bit binary (to construct 15 Hex UIN when no location present)
            #self.hex15=Fcn.bin2hex(self.bin[26:59]+default)
            #self.tablebin.append(['26-85',self.bin[26:59]+default,UIN,self.hex15])
            self._sn=str(Fcn.bin2dec(self.bin[41:59]))

            self.tablebin.append(['41-58',str(self.bin[41:59]),'Identification Data (decimal)','#{}'.format(self._sn),definitions.moreinfo['natloc']])
            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset,signlat,signlong =(0, 0, 0, 0, 0, 0, 0, 0,0,0)
            lat,declat,latdir,ltminutes =  Fcn.latitude(self.bin[59],self.bin[60:67],self.bin[67:72])
            lng,declng,lngdir,lgminutes =  Fcn.longitude(self.bin[72],self.bin[73:81],self.bin[81:86])
            self.courseloc=(declat,declng)
            if self.type not in ['uin', 'Short Msg']:
                self.tablebin.append(['59-71',str(self.bin[59:72]),'Latitude','{} ({})'.format(lat,declat)])
                self.tablebin.append(['72-85',str(self.bin[72:86]),'Longitude','{} ({})'.format(lng,declng)])
                self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                if 'Error' in lng:
                    self.errors.append('Bad logitude location ' + lng)
                if 'Error' in lat:
                    self.errors.append('Bad latitude locaton  ' + lat)
                if self.bin[107:110]=='110':
                    computed='Bits 107-109 should be 110.  Passed.'
                else:
                    computed= 'Bits 107-109 :'  + self.bin[107:110] + '.Bits should be 110 for this beacon protocol. Message not valid'
                    self.errors.append(computed)
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
                    latdelta,longdelta,ltoffset,lgoffset,signlat,signlong = Fcn.latlongresolution(self.bin,113,127)
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
                    #if int(self.bin[113:]) != 0:
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
                    valid='Not a valid uin (bits 59-85 not defaulted)'
                    self.errors.append(valid)
                self.tablebin.append(['59-85',default,'Default bits required','Defined by T.001 for Unique identifier'])
                self.tablebin.append(['59-85', str(self.bin[59:86]), 'Default bits in hex', valid])
                self._loc=False
            
        # RLS Location Protocol 
        elif typelocprotbin =='1101':
            default='0111111110111111111' #67-85 default 19 bit binary (to construct 15 Hex)
            if self.bch.bch1errors > 0 or self.bch.bch2errors > 0:
                self.hex15 = Fcn.bin2hex(self.bin[26:86]) #+ INVALID_UIN
                self.errors.append(BCH_ERRORS_PRESENT)
                self.errors.append(Fcn.bin2hex(self.bin[26:86]) + INVALID_UIN)
            else:
                self.hex15 = Fcn.bin2hex(self.bin[26:67] + default)

            self._loctype = "Location: {}".format(definitions.locprottype[typelocprotbin])

            self.tablebin.append(['37-40',str(self.bin[37:41]),'Protocol Code','{}'.format(self._loctype)])
            tano=str(Fcn.bin2dec(self.bin[43:53])).zfill(3)
            self.tablebin.append(['41-42',str(self.bin[41:43]),'Beacon type',btype])
            if self.bin[43:47]=='1111':
            # RLS for MMSI
                idtype='RLS protocol coded with MMSI last 6 digits'
                self.tablebin.append(['43-46', str(self.bin[43:47]), 'Identification type', idtype])
                self._id=str(Fcn.bin2dec(self.bin[47:67])).zfill(6)
                self.tablebin.append(['47-66', str(self.bin[47:67]), 'Last 6 digits MMSI','{}'.format(self._id)])
            else:
            # RLS for TAC number or National RLS with serial number
                idtype = 'RLS protocol coded with TAC or National RLS and Serial Number'
                self.tablebin.append(['43-46', str(self.bin[43:47]), 'Identification type', idtype])
                self.tablebin.append(['43-52',str(self.bin[43:53]),'RLS TAC# truncated or national assigned RLS','{}'.format(tano),definitions.moreinfo['rls_trunc']])
                self.tablebin.append(['', '', 'RLS TAC included missing leading digit prefix', '{}{}'.format(trunc,tano)])
                tano ='RLS: {}+{}'.format(trunc,tano)
                self._sn=str(Fcn.bin2dec(self.bin[53:67])).zfill(5)
                self.tablebin.append(['53-66',str(self.bin[53:67]),'Production or National assigned serial No','{}'.format(self._sn)])

            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset,signlat,signlong =(0,0,0,0,0,0,0,0,0,0)
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
                #if int(self.bin[113:]) != 0:
                self.tablebin.append(['113-114', str(self.bin[113:115]), 'RLS Provider Identification', {'00':'Spare','11':'Spare','01':'GALILEO Return Link Service Provider','10':'GLONASS Return Link Service Provider'}[str(self.bin[113:115])]])

                latdelta,longdelta,ltoffset,lgoffset,signlat,signlong = Fcn.latlongresolution(self.bin,115,133)
                self.tablebin.append(['115-123',str(self.bin[115:124]),'Latitude offset',ltoffset])
                self.tablebin.append(['124-132',str(self.bin[124:133]),'Longitude offset',lgoffset])
                self.tablebin.append(['133-144',str(self.bin[133:145]),BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
            elif self.type=='uin':
                if default == str(self.bin[67:86]):
                    valid = 'Valid'
                else:
                    valid = 'Bits not default'
                    self.errors.append(valid)
                self.tablebin.append(['67-85', default, 'Default bits required', 'Defined by T.001 for Unique identifier'])
                self.tablebin.append(['67-85', str(self.bin[67:86]), 'Default bits in hex', valid])
                self._loc = False

            elif self.type=='Short Msg':
                self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])

        # ELT-DT Location Protocol   
        elif typelocprotbin == '1001':

            default = '0111111110111111111'  # 67-85 default 19 bit binary (to construct 15 Hex)
            if self.bch.bch1errors > 0 or (self.bch.bch2errors > 0 and int(self.bin[113:]) != 0):
                self.errors.append(BCH_ERRORS_PRESENT)


            #self.tablebin.append(['26-85',self.bin[26:67]+default,UIN,self.hex15])
            #'ELT-DT Location'
            self._loctype = "Location: {}".format(definitions.locprottype[typelocprotbin])
            self.tablebin.append(['37-40',str(self.bin[37:41]),'Protocol Code','{} - {}'.format(btype,self._loctype)])
            self.tablebin.append(['41-42',str(self.bin[41:43]),'ELT Identity Type',definitions.eltdt[str(self.bin[41:43])]])

            if (str(self.bin[43:67]) == '0' * 24 or str(self.bin[43:67]) == '1' * 24) and str(self.bin[41:43]) != '11':
                self.tablebin.append(['43-66', str(self.bin[43:67]), 'ELT(DT) test beacon','Test beacon type since bits 43-66 are all 0 or All 1, designates Test Protocol'])
                self.testprotocol = 'test protocol mode transmission ' + btype
            else:
                if str(self.bin[41:43])=='10':
                # 10 bit TAC & Serial No
                    tano=str(Fcn.bin2dec(self.bin[43:53]))
                    self._sn=str(Fcn.bin2dec(self.bin[53:67]))
                    self.tablebin.append(['43-52',str(self.bin[43:53]),'Tac No','#{}'.format(tano)])
                    self.tablebin.append(['53-66',str(self.bin[53:67]),'Serial No','#{}'.format(self._sn)])
                elif str(self.bin[41:43])=='00':
                #24 bit aircraft address
                    self._id= '{} hex ({} decimal)'.format(str(Fcn.bin2hex2(self.bin[43:67],6)),str(Fcn.bin2dec(self.bin[43:67])))
                    self.tablebin.append(['43-66',str(self.bin[43:67]),'Aircraft 24 bit address', self._id])

                elif str(self.bin[41:43])=='01':
                # Aircraft operator designator
                    self._id=Fcn.baudot(self.bin,43,58,True)
                    self._sn=str(Fcn.bin2dec(self.bin[58:67]))
                    self.tablebin.append(['43-57',str(self.bin[43:58]),'Aircraft Operator Designator (15 bit)',self._id,definitions.moreinfo['elt_dt_aircraftoperator']])
                    self.tablebin.append(['58-66',str(self.bin[58:67]),'Serial No Assigned by Operator',self._sn])
                    self.threeletter=self._id
            if str(self.bin[41:43]) == '11':
                self.tablebin.append(['43-66', str(self.bin[43:67]), 'Identification data','Undefined for ELT Identity type - Spare'])
                if str(self.bin[43:67]) == '0' * 24 or str(self.bin[43:67]) == '1' * 24:
                    self.tablebin.append(['-', '-', 'ELT(DT) test beacon','Test beacon type since bits 43-66 are all 0 or All 1, designates Test Protocol'])
                    self.testprotocol = 'test protocol mode transmission '
            #elif str(self.bin[41:43])=='11' prior to CSC-62:
            # ELT(DT) Location Test Protocol

            latdelta,longdelta,ltmin,ltsec,lgmin,lgsec,ltoffset,lgoffset,signlat,signlong =(0,0,0,0,0,0,0,0,0,0)
            lat,declat,latdir =  Fcn.latitudeRLS(self.bin[67],self.bin[68:76])           
            lng,declng,lngdir =  Fcn.longitudeRLS(self.bin[76],self.bin[77:86])
            if 'Error' in lat:
                pass
                #self.errors.append(lat)
            if 'Error' in lng:
                pass
                #self.errors.append(lng)
            self.courseloc=(declat,declng)

            if self.type!='uin':
                if str(self.bin[67:86]) == '1111110101111111010': #type is ELT-DT cancellation message
                    self.cancellation = True
                    self.tablebin.append(['67-75', str(self.bin[67:76]), 'ELT-DT Cancellation message pattern: {}'.format('1 11111010'),'Cancellation message'])
                    self.tablebin.append(['76-85', str(self.bin[76:86]),  'ELT-DT Cancellation message pattern: {}'.format('1 111111010'),'Cancellation message'])
                    self.tablebin.append(['86-106', str(self.bin[86:107]), BCH1, str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                    if str(self.bin[107:133]) == '00111100011110000011110000': #make sure pattern is correct
                        self.tablebin.append(['107-132', str(self.bin[107:133]), 'Bit pattern valid for cancellation message', 'Cancellation message'])
                    else:
                        self.tablebin.append(['107-132', str(self.bin[107:133]), 'Bit pattern invalid','Cancellation message wrong'])
                        self.errors.append('Invalid cancellation message')
                    if int(self.bin[113:])!=0:
                        self.tablebin.append(['133-144', str(self.bin[133:145]), BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])
                else: #proceed to decode location
                    if 'Error' in lat:
                        pass
                        self.errors.append(lat)
                    if 'Error' in lng:
                        pass
                        self.errors.append(lng)


                    self.tablebin.append(['67-75',str(self.bin[67:76]),'Latitude','{} ({})'.format(lat,declat)])
                    self.tablebin.append(['76-85',str(self.bin[76:86]),'Longitude','{} ({})'.format(lng,declng)])
                    self.tablebin.append(['86-106',str(self.bin[86:107]),BCH1,str(self.bch.bch1calc()),definitions.moreinfo['bch1']])
                    means = {'01':'automatic activation by the beacon','11':'spare','00':'manual activation by user','10':'automatic activation by external means'}
                    meansbin = str(self.bin[107:109])
                    self.tablebin.append(['107-108',meansbin,'means of activation',means[meansbin]])
                    enc_altbin=str(self.bin[109:113])
                    self.altitude = definitions.enc_alt[enc_altbin]
                    self.tablebin.append(['109-112',enc_altbin,'encoded altitude',self.altitude])
                    finallat=finallng='Not Used'
                    enc_loc_fresh = {'00':'PDF-2 rotating field indicator',
                                     '01':'Encoded location in message more than 60 seconds old or the default encoded position is transmitted',
                                     '10': 'Encoded location in message is greater than two seconds and equal or less than 60 seconds old',
                                     '11':'Encoded location in message is current (i.e., the encoded location freshness is less or equal to 2 seconds)'
                                     }
                    enc_freshbin=str(self.bin[113:115])
                    #if int(self.bin[113:]) != 0 :
                    self.tablebin.append(['113-114', enc_freshbin, 'Encoded location freshness or PDF-2 rotating field indicator', enc_loc_fresh[enc_freshbin]])

                    if enc_freshbin!='00':

                        latdelta,longdelta,ltoffset,lgoffset,signlat,signlong = Fcn.latlongresolution(self.bin,115,133)
                        self.tablebin.append(['115-123',str(self.bin[115:124]),'Latitude offset',ltoffset])
                        self.tablebin.append(['124-132',str(self.bin[124:133]),'Longitude offset',lgoffset])

                    elif enc_freshbin=='00':
                        # for rotating field designator
                        if str(self.bin[115:118])=='000':
                            op3ld = ''
                            for e in [(118, 123), (123, 128), (128, 133)]:
                                try:
                                    l = definitions.baudot['1' + str(self.bin[e[0]:e[1]])]
                                except KeyError:
                                    l = '*'
                                op3ld = op3ld + l
                                if '*' in op3ld:
                                    self.errors.append('Unable to decode Aircraft 3LD in bits 115-132 (See * )')
                            ldtype='Aircraft operator 3LD designation'
                            self.tablebin.append(['115-117', str(self.bin[115:118]), 'Aircraft operator 3LD designator or Spare', ldtype])
                            self.tablebin.append(['118-132', str(self.bin[118:133]), 'Aircraft operator 3LD', op3ld])
                            self.warnings.append('WARNING: Location is a coarse position only, and hence has less resolution/accuracy than a message without the rotating field')
                            self.threeletter = op3ld
                        else:
                            ldtype = 'Spare'
                            self.tablebin.append(['115-117', str(self.bin[115:118]), 'Aircraft operator 3LD designator or Spare',ldtype])
                            self.tablebin.append(['118-132', str(self.bin[118:133]), 'Spare','Reserved for future development'])

                    self.tablebin.append(['133-144', str(self.bin[133:145]), BCH2, str(self.bch.bch2calc()),definitions.moreinfo['bch2']])


            elif self.type=='uin':
                if default == str(self.bin[67:86]):
                    valid = 'Valid'
                else:
                    valid = 'Not a valid uin (bits 67-85 not defaulted)'
                    self.errors.append(valid)
                self.tablebin.append(['67-85', default, 'Default bits required', 'Defined by T.001 for Unique identifier'])
                self.tablebin.append(['67-85', str(self.bin[67:86]), 'Default bits in hex', valid])

                self._loc = False
            if self.errors:
                self.hex15 = Fcn.bin2hex(self.bin[26:86]) #+ INVALID_UIN
                self.errors.append(Fcn.bin2hex(self.bin[26:86]) + INVALID_UIN )
            else:
                self.hex15 = Fcn.bin2hex(self.bin[26:67] + default )

        if Fcn.is_number(declat) and Fcn.is_number(latdelta) and Fcn.is_number(declng) and Fcn.is_number(longdelta):
            self._loc=True
            if latdelta==0 and signlat <0 and self.type!='uin':
                self.warnings.append('Latitude offset minutes and seconds are all zeroes.  Delta bit 113 in pdf-2 should be 1')

            if longdelta==0 and signlong<0 and self.type!='uin':
                self.warnings.append('Longitude offset minutes and seconds are all zeroes.  Delta bit 123 in pdf-2 should be 1')
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
            self.location = ('NA', 'NA')
            self.latitude = 0
            self.longitude = 0
        self._btype=btype
        self.tac=str(tano)



class Beacon(HexError):
    def __init__(self,hexcode):
        genmsgdic={'63':'The code consists of 63 hexadecimal characters representing a 252 bit messgage format from a second generation beacon, including 48 bits of BCH error correcting bit as defined by T.018 Issue 1 - Rev.8.',
                   '15sgb':'The code consists of first 15 hexadecimal characters of Hex ID for an SGB.  Due to ignored last 8 hex characters, vehicle identification cannot be decoded as per specification in T.018 - Issue 1. Rev.8. ',
                   '22':'The code consists of 22 hexadecimal characters representing a first gerneration beacon short message as defined by T.001 Issue 4 - Rev.6).',
                   '22long': 'The code consists of 22 hexadecimal characters representing a first generation beacon message with a Long format flag(30 hex trunctated to 22 excluding BCH-2).  Forrmat specifications are defined by T.001 Issue 4 - Rev.6).',
                   '30short': 'The code consists of 30 hexadecimal characters representing a first generation beacon message with format flag set to Short.   FGB short message format specifications 22 hex and truncate last 8 hex digits (as per T.001 Issue 4 - Rev.6).',
                   '15':'Hex data entered is a 15 Hex ID unique identifier based on FGB specifications (as per T.001 Issue 4 - Rev.5).',
                   '23': 'Hex data length of 23 consistent with Hex unique identifier based on SGB specifications (as per T.018 Issue 1 - Rev.8).',
                   '51': 'Hex data entered is a length of 51 characters representing a 204 bit (00 + 202 bit) consistent with SGB specifications, excluding BCH (as per T.018 Issue 1 - Rev.8).  The decoded message below computes the BCH portion of the message and associated hex characters for information purposes.',
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
                beacon = Gen2.SecondGen(hexcode) # version 2.02 was padded with 8*'0' to make 23 size
                self.genmsg = genmsgdic['15sgb']
            else:
                self.gentype = 'first'
                beacon = BeaconFGB(hexcode)
                self.genmsg = genmsgdic['15']+' Computed Checksum : '+Fcn.getFiveCharChecksum(hexcode)

        elif len(hexcode) == 30 :
            beacon=BeaconFGB(hexcode)
            self.gentype='first'
            if beacon.type == SHORT_MSG:
                self.genmsg = genmsgdic['30short']
            else:
                self.genmsg = genmsgdic['30']

        elif len(hexcode) == 22 :
            # check if this is a short message or a long message without the BCH2
            beacon=BeaconFGB(hexcode)
            self.gentype='first'

            if beacon.type == LONG_MSG:
                self.genmsg = genmsgdic['22long']
            else:
                self.genmsg = genmsgdic['22']

        elif len(hexcode) == 28:
            beacon = BeaconFGB(hexcode)
            self.gentype = 'first'
            if beacon.type == LONG_MSG:
                self.genmsg = genmsgdic['28long']
            else:
                self.genmsg = genmsgdic['28']

        elif len(hexcode) == 36:
            beacon=BeaconFGB(hexcode)
            self.gentype = 'first'
            if beacon.type in [SHORT_MSG,SHORT_OR_LONG_MSG]:
                self.genmsg = genmsgdic['36short']
            else:
                self.genmsg = genmsgdic['36']

        else:
            self.type = 'Hex length of ' + str(
                len(hexcode)) + '.' + '\nValid Lengths: FGB: 15,22,28 30 or 36.  SGB: 15, 23 or 63'
            raise HexError('Length Error', self.type)
            self.beacon=None



        self.beacon=beacon
        self.cancellation = self.beacon.cancellation
        self.sgb_spare_bits = self.beacon.sgb_spare_bits
        self.latitude=self.beacon.latitude
        self.longitude=self.beacon.longitude
        self.location=self.beacon.location
        self.courseloc=self.beacon.courseloc
        self.tablebin=self.beacon.tablebin
        self.bchstring=self.beacon.bchstring
        self.type = self.beacon.type
        self.errors = self.beacon.errors
        self.threeletter = self.beacon.threeletter
        self.altitude = self.beacon.altitude
        self.warnings = self.beacon.warnings

    def has_loc(self):
        if self.beacon.type=='uin' or self.beacon.location==(0,0):
            return False
        elif self.beacon.latitude in ['No latitude data available','Invalid Latitude','na','Default - no location (Default - no location)'] or\
                        self.beacon.longitude in ['No longitude data available', 'Invalid Longitude','Default - no location (Default - no location)','na']:
            return False
        else:
            return True

    def lat(self):
        if self.has_loc():
            return self.beacon.latitude
        else:
            return "n/a"

    def long(self):
        if self.has_loc():
            return self.beacon.longitude
        else:
            return "n/a"

    def btype(self):
        return self.beacon.btype()

    def hexuin(self):
        return self.beacon.hexuin()

    def bchmatch(self):
        return  self.beacon.bchmatch()

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

    def get_id(self):
        return self.beacon.get_id()

    def get_sn(self):
        return self.beacon.get_sn()

    def __getattr__(self, name):
        return 'Beacon does not have {} attribute.'.format(str(name))

def beaconcountry(hexcode):
    try:
        beacon = Beacon(hexcode)
        ctry = beacon.get_country()
    except HexError as e:
        ctry = e.message

    return ctry
