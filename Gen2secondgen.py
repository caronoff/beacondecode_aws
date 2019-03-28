#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
###########################################
# Second Generation Beacon Decode Program #
###########################################

import Gen2functions as Func
import Gen2rotating as rotating
import writebch
import definitions


class Gen2Error(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message

    def __str__(self):
        return repr(self.value, self.message)


class SecondGen(Gen2Error):
    def __init__(self, hexCode=None):
        self.bits = '0' * 252
        self.validhex=True
        if hexCode:
            self.processHex(hexCode)


    def processHex(self, strhex):

        ##All second generation beacon messages must be EXACTLY 250 bits
        ##in length for the program to function properly.
        self.bits = Func.hex2bin(strhex)
        self.inputhex=strhex
        self.bchstring = ''
        self.tablebin = []
        self.rotatingbin = []
        self.longitude=self.latitude='na'
        self.location=(0,0)
        self.courseloc=('na','na')
        self.errors=[]
        self.fixedbits = ''
        self.testprotocol=''


        if len(self.bits) == 252 or len(self.bits) == 204 :
            self.type="Complete message"

            pbit=self.bits[0:2]
            if pbit=='00':
                padding='OK'
            else:
                padding = 'Left padding should be 00 unless this message self-test beacon transmission '
                self.errors.append(padding)
                self.tablebin.append(['left padding', pbit, '', padding])
                if pbit=='10':
                    self.tablebin.append(['', '', '', 'This is a self-test beacon transmission or bad message'])
                else:
                    self.tablebin.append(['', '', '', 'ERROR! Value is not self-test beacon transmission.'])


            ##Add an additional bit to ensure that bits in array line up with bits in documentation and only include important bits 1-202
            self.bits = "0" + self.bits[2:]
            ##Add the 23 Hex ID to our table
            self.beaconHexID = self.uinSgb()
            #self.tablebin.append(['','','Beacon 23 Hex ID:',self.beaconHexID])

            #self.tablebin.append(['left padding',pbit,'',padding])

            ##T018 Issue 1 - Rev 4:  Bit 1-16 Type Approval Certificate #   (previously BIT 1-20  Type Approval Certificate #)

            self.tac = Func.bin2dec(self.bits[1:17])
            if self.tac<10000:
                warn='<strong>{}</strong>  <br>WARNING!: SGB specifications stipulate TAC No >=10,000'.format(self.tac)
            else:
                warn=self.tac
            self.tablebin.append(['1-16',
                                  self.bits[1:17],
                                  'Type Approval Cert No: ',
                                  warn])

            ##T018 Issue 1 - Rev 4:  Bit 17-30 Serial Number (previously  bit 21-30 Serial Number)
            self.serialNum = Func.bin2dec(self.bits[17:31])
            self.tablebin.append(['17-30',
                                  self.bits[17:31],
                                  'Beacon Serial Number:',
                                  str(self.serialNum)])

            ##BIT 31-40 Country code
            self.countryCode = Func.bin2dec(self.bits[31:41])
            self.countryName = Func.countryname(self.countryCode)
            self.tablebin.append(['31-40',
                                  self.bits[31:41],
                                  'Country code:',
                                  str(self.countryCode)+' '+str(self.countryName),definitions.moreinfo['country_code']])

            ##BIT 41 Status of homing device
            self.status = Func.homing(self.bits[41])
            self.tablebin.append(['41',
                                  self.bits[41],
                                  'Status of homing device:',
                                  self.status])

            ####T018 Issue 1 - Rev 4: Bit 42: RLS Function ( previously Bit 42 Self-test function )

            self.tablebin.append(['42',
                                  self.bits[42],
                                  'RLS function capability:',
                                  Func.rls(self.bits[42])])

            ##BIT 43 Test protocol
            self.testprotocol = Func.testProtocol(self.bits[43])
            self.tablebin.append(['43',
                                  self.bits[43],
                                  'Test protocol flag:',
                                  self.testprotocol])

            ##BIT 44-90 Encoded GNSS location
            self.latitude = Func.getlatitude(self.bits[44:67])
            self.tablebin.append(['44-66',
                                  self.bits[44:67],
                                  'Latitude:',
                                  self.latitude[0]])

            self.longitude = Func.getlongitude(self.bits[67:91])
            self.tablebin.append(['67-90',
                                  self.bits[67:91],
                                  'Longitude:',
                                  self.longitude[0]])
            self.location = (self.latitude[1], self.longitude[1])



            ################################
            #                              #
            #  BIT 91-137 VESSEL ID FIELD  #
            #                              #
            ################################
            self.vesselIDfill(0,self.bits[91:138])

            ## T018 Iss.1 Rev.4 Bit 138-140 Beacon Type (previous (Bit 138-139  Beacon Type)
            self.tablebin.append(['138-140',
                                  self.bits[138:141],
                                  'Beacon Type:',
                                  Func.getBeaconType(self.bits[138:141])])
            ## T018 Iss.1 Rev.4 removed
            '''
            self.tablebin.append(['140',
                                  self.bits[140],
                                  'RLS capability:',
                                  Func.rls(self.bits[140])])

            '''
            ##BIT 141-154 Spare bits
            if Func.checkones(self.bits[141:155]) and not Func.checkones(self.bits[155:159]):
                self.tablebin.append(['141-154',
                                      self.bits[141:155],
                                      'Spare bits',
                                      'OK - all bits 1 and rotating field not a cancellation message'])
            elif Func.checkones(self.bits[141:155]) and Func.checkones(self.bits[155:159]):
                e='ERROR! - all bits 1 and rotatating field is a cancellation message (for a cancellation message these bits should be set to 0)'
                self.errors.append(e)
                self.tablebin.append(['141-154',
                                      self.bits[141:155],
                                      'Spare bits',
                                      e])

            elif Func.checkzeros(self.bits[141:155]) and Func.checkones(self.bits[155:159]):
                self.tablebin.append(['141-154',
                                      self.bits[141:155],
                                      'Spare bits',
                                      'OK - all bits 0 and rotating field is cancellation message (unless this is a cancellation message, these bits should be set to 1'])

            elif Func.checkzeros(self.bits[141:155]) and not Func.checkones(self.bits[155:159]):
                e= 'ERROR!- all bits 0 and rotating field is not cancellation message'
                self.errors.append(e)
                self.tablebin.append(['141-154',
                                      self.bits[141:155],
                                      'Spare bits',
                                      e])

            else:
                e = 'ERROR: Bits 141-154 should be set to all 1 or all 0 in the case that the rotating field is a cancellation message'
                self.errors.append(e)
                self.tablebin.append(['141-154',
                                      self.bits[141:155],
                                      'Cancellation message status:',
                                      e])



            #######################################
            #                                     #
            #  BIT 155-202 48 BIT ROTATING FIELD  #
            #                                     #
            #######################################

            self.rotatingID = Func.bin2dec(self.bits[155:159])


            ######################################################
            # Rotating Field 0: C/S G.008 Objective Requirements #
            ######################################################

            if self.rotatingID == 0:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      '(#0) C/S G.008 Objective Requirements'])
                self.rotatingbin = rotating.rotating0(self.bits[155:203])


            ########################################
            # Rotating Field 1: Inflight Emergency #
            ########################################

            elif self.rotatingID == 1:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      '(#1) Inflight Emergency'])
                self.rotatingbin = rotating.rotating1(self.bits[155:203])


            #########################
            # Rotating Field 2: RLS  #
            #########################

            elif self.rotatingID == 2:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      '(#2) RLS'])
                self.rotatingbin = rotating.rotating2(self.bits[155:203])


            ##################################
            # Rotating Field 3: National Use #
            ##################################

            elif self.rotatingID == 3:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      '(#3) National Use'])
                self.rotatingbin = rotating.rotating3(self.bits[155:203])


            ###########################################
            # Rotating Field 15: Cancellation Message #
            ###########################################

            elif self.rotatingID == 15:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      '(#15) Cancellation Message'])
                self.rotatingbin = rotating.rotating15(self.bits[155:203])


            ##################################
            # All other rotating fields spare #
            ##################################

            else:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      'Spare'])


            ##Add rotating field data to our list
            self.tablebin.extend(self.rotatingbin)





            ####################################
            # 48-BIT BCH ERROR CORRECTING CODE #
            ####################################
            if len(self.bits) == 251:
                # 251 length means 250 plus the stub 0, minus the extra 2 digits of front padding in self.bits
                self.tablebin.append(['203-250',
                                      self.bits[203:],
                                      'Encoded BCH',
                                      'Encoded BCH'])
                ##Calculate the BCH
                self.calculatedBCH = Func.calcBCH(self.bits[1:], 0, 202, 250)
                self.bchstring=writebch.calcBCH(self.bits[1:], 0, 202, 250)[1]

                self.tablebin.append(['Calculated',
                                      self.calculatedBCH,
                                      'Computed',
                                      ''])
                #self.tablebin.append(['','','','self.calculatedBCH {} : self.bchstring {} {}'.format(self.calculatedBCH,self.bchstring,self.calculatedBCH==self.bchstring)])
                ##Compare to the BCH in the beacon message
                bcherr= self.BCHerrors = Func.errors(self.calculatedBCH, self.bits[203:])
                if bcherr > 0 :
                    bcherror='ERROR! COMPUTED BCH DOES NOT MATCH ENCODED BCH!!'
                else:
                    bcherror = 'VALID BCH: COMPUTED BCH MATCHES'
                self.errors.append(bcherror)
                self.tablebin.append(['','','',bcherror])
            elif len(self.bits)==203:
                # if user enters a hex 51 excluding bch, then this ,means 202 information bits plus stub 0 minues the 2 digits of front padding
                self.tablebin.append(['203-250','NA','Encoded BCH','Not provided in a 51 Hex.  Computed below'])
                self.calculatedBCH =Func.calcBCH(self.bits[1:], 0, 202, 250)
                hexBCH= Func.bin2hex(self.calculatedBCH)
                self.tablebin.append(['203-250', self.calculatedBCH, 'Calculated BCH', 'Hex Value: {}'.format(hexBCH)])
                self.tablebin.append(['Complete Message', '', 'Hex Value: {}{}'.format(self.inputhex,hexBCH),''])






        elif len(self.bits) == 92 :
            self.type='uin'
            ##Add an additional bit to ensure that bits in array line up with bits in documentation
            self.bits = "0" + self.bits

            self.latitude = self.longitude = 'No data available'
            self.tablebin.append(['Unique ID','Second Generation','',''])
            self.tablebin.append(['1',
                                  self.bits[1],
                                  'should be 1',
                                  ['ERROR', 'OK'][int(self.bits[1])]])
            if self.bits[1]=='0':
                self.validhex = False

            ##BIT 2-11 Country code
            self.countryCode = Func.bin2dec(self.bits[2:12])
            self.countryName = Func.countryname(self.countryCode)
            if self.countryName=='Unknown MID':
                self.validhex=False
            self.tablebin.append(['2-11',
                                  self.bits[2:12],
                                  'Country code:',
                                  str(self.countryCode) + ' ' + str(self.countryName),definitions.moreinfo['country_code']])
            ##BIT 12-14 Should be 101 status check for SGB
            if self.bits[12:15] == '101':
                status_check = 'OK'
            else:
                status_check = 'ERROR'
                self.validhex = False
            self.tablebin.append(['12-14',
                                  self.bits[12:15],
                                  'Should be 101',
                                  status_check])
            ##BIT 15-30  Type Approval Certificate #
            self.tac = Func.bin2dec(self.bits[15:31])
            if self.tac<10000:
                warn='<strong>{}</strong><br> WARNING! SGB specifications requires TAC No >=10,000'.format(self.tac)
                self.validhex = False
            else:
                warn=str(self.tac)
            self.tablebin.append(['15-30',
                                  self.bits[15:31],
                                  'Type Approval Cert No: ',
                                  warn])
            ##BIT 31-44 Beacon Serial Number
            self.serialNum = Func.bin2dec(self.bits[31:45])
            self.tablebin.append(['31-44',
                                  self.bits[35:45],
                                  'Serial Number',
                                  str(self.serialNum)])

            self.testprotocol = Func.testProtocol(self.bits[45])
            self.tablebin.append(['45',
                                  self.bits[45],
                                  'Test protocol flag:',
                                  str(self.testprotocol)])

            if self.bits[45]=='1':
                self.validhex = False
            if self.bits[61:] == '0'*32:

                self.tablebin.append(['46-48', self.bits[46:49], 'Vessel ID Type',Func.getVesselid(self.bits[46:49])])
                self.tablebin.append(['49-60', self.bits[49:61], 'Partial vessel ID', 'WARNING!! = No Identification information or Truncated SGB 15Hex UIN (incomplete partial vessel ID. '])
                self.tablebin.append(['61-92', self.bits[61:], 'Remaining bits', ''])
                #self.vesselIDfill(46, self.bits[46:93])
            else:
            ##BIT 45-91 Aircraft / Vessel ID
                self.vesselIDfill(45, self.bits[46:93])

                ##T018 Iss.1 Rev 4 removed :  (was BIT 92 Fixed value 1)
            '''
                if self.bits[92]=='1':
                    status_check = 'OK'
                else:
                    status_check = 'ERROR'

                self.tablebin.append(['92',
                                      self.bits[92],
                                      'Fixed 1',
                                      status_check])
            '''
        else:
            self.type = ('Hex string length of ' + str(len(strhex)) + '.'
                         + '\nBit string length of ' + str(len(self.bits)) + '.'
                         + '\nLength of First Gen Beacon Hex String must be 15, 22 or 30'
                         + '\nLength of Second Gen Beacon Bit String must be 204 or 252 bits')
            raise Gen2Error('LengthError', self.type)

    def testmsg(self):
        return (Func.selfTest(self.bits[42]),Func.testProtocol(self.bits[43]))

    def getencpos(self):
        return 'Of course! This is an SGB'

    def hexuin(self):
        if self.type=='uin':
            return 'Message is a UIN'
        return self.uinSgb()

    def uinSgb(self):
        ####################
        # BEACON 23 HEX ID #
        ####################
        hexID = []

        ##Hex ID BIT 1 = fixed binary 1
        hexID.append('1')

        ##Hex ID BIT 2-11 = BITS 31-40 (C/S Country Code)
        hexID.append(self.bits[31:41])

        ##Hex ID BIT 12 = fixed binary 1
        hexID.append('1')

        ##Hex ID BIT 13 = fixed binary 0
        hexID.append('0')

        ##Hex ID BIT 14 = fixed binary 1
        hexID.append('1')

        ##Hex ID BIT 15-30 = BITS 1-16 (C/S TAC No)
        hexID.append(self.bits[1:17])

        ##Hex ID BIT 31-44 = BITS 17-30 (Beacon Serial Number)
        hexID.append(self.bits[17:31])

        ##Test protocol flag = Bit 45  = Bit 43
        hexID.append(self.bits[43])

        ##Hex ID BIT 46-48 = BITS 91-93 (Aircraft/Vessel ID Type)
        hexID.append(self.bits[91:94])

        ##Hex ID BIT 49-92 = BITS 94-137 (Aircraft/Vessel ID)
        hexID.append(self.bits[94:138])



        ##Join list together and convert to Hexadecimal
        beaconHexID = Func.bin2hex(''.join(hexID))
        return beaconHexID

    def bitlabel(self,a,b,c):
        return str(int(a)-int(c))+'-'+str(int(b)-int(c))

    def btype(self):
        if self.type!='uin':
            return Func.getBeaconType(self.bits[138:140])
        else:
            return 'UIN s/n: {}'.format(self.serialNum)

    def vesselIDfill(self,deduct_offset,bits):


        self.vesselID = bits[0:3]
        self.tablebin.append([self.bitlabel(91,93,deduct_offset), self.vesselID , 'Vessel ID Type', Func.getVesselid(self.vesselID)])
        if self.vesselID == '111' and self.bits[43]=='0':
            self.tablebin.append(['','','Reserved for system testing','ERROR! Test protocol bit 43 is zero'])
            self.validhex=False

        ##############################################
        # Vessel 0: No aircraft or maritime identity #
        ##############################################

        if self.vesselID == '000':


            if Func.checkzeros(bits[3:47]):

                self.tablebin.append([self.bitlabel(94,137,deduct_offset),
                                      bits[3:47],
                                      'Vessel ID type is none',
                                      'All 0 - OK'])
            else:
                self.tablebin.append([self.bitlabel(94, 137,deduct_offset),
                                      bits[3:47],
                                      'Vessel ID type is none',
                                      'Unless national assigned, should be all 0'])
                self.validhex = False
        ###########################
        # Vessel 1: Maritime MMSI #
        ###########################
        elif self.vesselID == '001':

            self.mmsi = Func.bin2dec(bits[3:33])

            if self.mmsi == 111111:
                self.tablebin.append([self.bitlabel(94,123,deduct_offset),
                                      bits[3:33],
                                      'MMSI:',
                                      'No MMSI available'])
            else:
                self.mmsi_string = str(self.mmsi).zfill(9)

                self.tablebin.append([self.bitlabel(94,123,deduct_offset),
                                      bits[3:33],
                                      'Unique ship station identity where the first 3 digits are MID (MIDxxxxxx):',
                                      self.mmsi_string])
                self.mmsi_country = Func.countryname(int(self.mmsi_string[0:3]))
                self.tablebin.append(['',
                                      '',
                                      'Flag state of vessel:',
                                      self.mmsi_string[0:3] + ' ' + self.mmsi_country])
                self.tablebin.append(['',
                                      '',
                                      'Unique vessel number',
                                      self.mmsi_string[3:]])

            self.epirb_ais = Func.bin2dec(bits[33:47])

            if self.epirb_ais == 10922:
                self.tablebin.append([self.bitlabel(124,137,deduct_offset),
                                      bits[33:47],
                                      'EPIRB-AIS System Identity:',
                                      'No EPIRB-AIS System'])
            else:
                self.epirb_ais_str = str(self.epirb_ais).zfill(4)

                self.epirb_ais_str = '974xx' + self.epirb_ais_str
                self.tablebin.append([self.bitlabel(124,137,deduct_offset),
                                      bits[33:47],
                                      'EPIRB-AIS System Identity',
                                      self.epirb_ais_str])
        #############################
        # Vessel 2: Radio Call Sign #
        #############################
        elif self.vesselID == '010':
            self.callsign = Func.getCallsign(bits[3:45])
            self.tablebin.append([self.bitlabel(94,135,deduct_offset),
                                  bits[3:45],
                                  'Radio Callsign',
                                  self.callsign,
                                  definitions.moreinfo['sgb_radio_callsign']])
            if Func.checkzeros(bits[45:47]):
                status_check='OK'
            else:
                status_check = 'ERROR'
                self.validhex = False
            self.tablebin.append([self.bitlabel(136,137,deduct_offset),
                                  bits[45:47],
                                  'Spare should be 0',
                                  status_check])

        #########################################################
        # Vessel 3: Aricraft Registration Marking (Tail Number) #
        #########################################################
        elif self.vesselID == '011':
            self.tailnum = Func.getTailNum(bits[3:45])
            self.tablebin.append([self.bitlabel(94,135,deduct_offset),
                                  bits[3:45],
                                  'Aircraft Registration Marking:',
                                  self.tailnum])
            if bits[45:47]=='00':
                status_check = 'OK'
            else:
                status_check = 'ERROR'
                self.validhex = False
            self.tablebin.append([self.bitlabel(136,137,deduct_offset),
                                  bits[45:47],
                                  'Spare should be 00',
                                  status_check])
        ##############################################
        # Vessel 4: Aircraft Aviation 24 Bit Address #
        ##############################################
        elif self.vesselID == '100':

            self.aviationBitAddress = Func.bin2dec(bits[3:27])
            self.tablebin.append([self.bitlabel(94,117,deduct_offset),
                                  bits[3:27],
                                  'Aviation 24 bit address',
                                  str(self.aviationBitAddress)])
            if Func.checkzeros(bits[27:47]):
                status_check = 'OK'
            else:
                status_check = 'ERROR'
                self.validhex = False
            self.tablebin.append([self.bitlabel(118,137,deduct_offset),
                                  bits[27:47],
                                  'Spare should be 0',
                                  status_check])
        #################################################
        # Vessel 5: Aircraft Operator and Serial Number #
        #################################################

        elif self.vesselID == '101':


            self.operator = Func.baudot2str(bits[3:21], 3)
            self.serialnum = Func.bin2dec(bits[21:33])
            self.tablebin.append([self.bitlabel(94,111,deduct_offset),
                                  bits[3:21],
                                  'Aircraft operator designator:',
                                  self.operator])
            self.tablebin.append([self.bitlabel(112,123,deduct_offset),
                                  bits[21:33],
                                  'Aircraft Serial number:',
                                  str(self.serialnum)])


            if Func.checkones(bits[33:47]):
                status_check = 'OK'
            else:
                status_check = 'ERROR'
                self.validhex = False
            self.tablebin.append([self.bitlabel(124,137,deduct_offset),
                                  bits[33:47],
                                  'Spare all should be 1',
                                  status_check])

        elif self.vesselID == '111' and self.bits[43]=='1':

            self.tablebin.append([self.bitlabel(94, 137, deduct_offset),
                                  bits[3:47],
                                  'Reserved for system testing','OK. Test protocol bit 43 set to 1. May contain information; default  bits 94-137 - 0s'])
        elif self.vesselID == '111' and self.bits[43]=='0':
            self.tablebin.append([self.bitlabel(94, 137, deduct_offset),
                                  bits[3:47],
                                  'Reserved for system testing',
                                  ''])
        elif self.vesselID == '110':
            self.tablebin.append([self.bitlabel(94, 137, deduct_offset),
                                  bits[3:47],
                                  'Spare',
                                  'ERROR! Not defined by T.018.  Should not be used'])
            self.validhex = False


    def gettac(self):
        return self.tac



    def loctype(self):
        return 'na - SGB'

    def get_country(self):
        return str(self.countryCode) + ' ' + str(self.countryName)
    def get_mid(self):
        return str(self.countryCode)
    def bchmatch(self):
        if len(self.bits)>=249:
            if Func.errors(Func.calcBCH(self.bits[1:], 0, 202, 250), self.bits[203:])>0:
                return 'COMPUTED BCH DOES NOT MATCH ENCODED BCH!!'
            else:
                return 'SGB BCH matches encoded'
        return ''

    def fbits(self):
        return 'na for SGB'

    def country(self):
        return (('Country Code:', self.countryCode), ('Country Name:', self.countryName))

    def has_loc(self):
        if self.latitude == 'No data available' or self.latitude == 'Invalid Latitude' or self.longitude == 'No longitude data available' or self.longitude == 'Invalid Longitude' or self.latitude == 'No latitude data available' :
            return False
        else:
            return True




