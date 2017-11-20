#!/usr/bin/python
#print("Content-Type: text/html\n")
#print()
###########################################
# Second Generation Beacon Decode Program #
###########################################

import Gen2functions as Func
import Gen2rotating as rotating


class Gen2Error(Exception):
    def __init__(self, value, message):
        self.value = value
        self.message = message

    def __str__(self):
        return repr(self.value, self.message)


class SecondGen(Gen2Error):

    def __init__(self, hexCode=None):
        self.bits = '0' * 250
        if hexCode:
            self.processHex(hexCode)
    def processHex(self, strhex):

        ##All second generation beacon messages must be EXACTLY 250 bits
        ##in length for the program to function properly.
        self.bits = Func.hex2bin(strhex)
        self.tablebin = []
        self.rotatingbin = []
        self.longitude=self.latitude=0
        self.location=(0,0)


        if len(self.bits) == 252 or len(self.bits) == 202 or len(self.bits) == 204 or len(self.bits) == 250 :

            self.type="Complete message"
            ##Add an additional bit to ensure that bits in array line up with bits in documentation
            self.bits = "0" + self.bits

            ##BIT 1-20  Type Approval Certificate #
            self.tac = Func.bin2dec(self.bits[1:21])
            self.tablebin.append(['1-20',
                                  self.bits[1:21],
                                  'Type Approval Certificate #:',
                                  str(self.tac)])

            ##BIT 21-30 Serial Number
            self.serialNum = Func.bin2dec(self.bits[21:31])
            self.tablebin.append(['21-30',
                                  self.bits[21:31],
                                  'Serial Number:',
                                  str(self.serialNum)])

            ##BIT 31-40 Country code
            self.countryCode = Func.bin2dec(self.bits[31:41])
            self.countryName = Func.countryname(self.countryCode)
            self.tablebin.append(['31-40',
                                  self.bits[31:41],
                                  'Country code:',
                                  str(self.countryCode)+' '+str(self.countryName)])

            ##BIT 41 Status of homing device
            self.status = Func.homing(self.bits[41])
            self.tablebin.append(['41',
                                  self.bits[41],
                                  'Status of homing device:',
                                  self.status])

            ##BIT 42 Self-test function
            self.selfTestStatus = Func.selfTest(self.bits[42])
            self.tablebin.append(['42',
                                  self.bits[42],
                                  'Self-test function:',
                                  self.selfTestStatus])

            ##BIT 43 User cancellation
            self.cancel = Func.cancellation(self.bits[43])
            self.tablebin.append(['43',
                                  self.bits[43],
                                  'User cancellation:',
                                  self.cancel])

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




            ##BIT 138-154 Spare bits [137-154]
            if Func.checkones(self.bits[138:155]):
                self.tablebin.append(['138-154',
                                      self.bits[138:155],
                                      'Spare:',
                                      'OK'])
            else:
                self.tablebin.append(['138-154',
                                      self.bits[138:155],
                                      'Spare:',
                                      'ERROR: Bits 138-154 should be 1s'])



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
            # Rotating Field 2: RLS #
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
            # All other roating fields spare #
            ##################################

            else:
                self.tablebin.append(['155-158 (Rotating field 1-4)',
                                      self.bits[155:159],
                                      'Rotating Field Type:',
                                      'Spare'])


            ##Add rotating field data to our list
            self.tablebin.extend(self.rotatingbin)



            ####################
            # BEACON 23 HEX ID #
            ####################
            self.hexID = []

            ##Hex ID BIT 1 = fixed binary 1
            self.hexID.append('1')

            ##Hex ID BIT 2-11 = BITS 31-40 (C/S Country Code)
            self.hexID.append(self.bits[31:41])

            ##Hex ID BIT 12 = fixed binary 1
            self.hexID.append('1')

            ##Hex ID BIT 13 = fixed binary 0
            self.hexID.append('0')

            ##Hex ID BIT 14 = fixed binary 1
            self.hexID.append('1')

            ##Hex ID BIT 15-34 = BITS 1-20 (C/S TAC No)
            self.hexID.append(self.bits[1:21])

            ##Hex ID BIT 35-44 = BITS 21-30 (Beacon Serial Number)
            self.hexID.append(self.bits[21:31])

            ##Hex ID BIT 45-47 = BITS 91-93 (Aircraft/Vessel ID Type)
            self.hexID.append(self.bits[91:94])

            ##Hex ID BIT 48-91 = BITS 94-137 (Aircraft/Vessel ID)
            self.hexID.append(self.bits[94:138])

            ##Hex ID BIT 92 = fixed binary 1
            self.hexID.append('1')


            ##Join list together and convert to Hexadecimal
            self.beaconHexID = Func.bin2hex(''.join(self.hexID))

            ##Add the 23 Hex ID to our table
            self.tablebin.append(['',
                                  '',
                                  'Beacon 23 Hex ID:',
                                  self.beaconHexID])


            ####################################
            # 48-BIT BCH ERROR CORRECTING CODE #
            ####################################
            if len(self.bits) == 253:
                self.tablebin.append(['203-250',
                                      self.bits[203:],
                                      'Encoded BCH',
                                      'Encoded BCH'])
                ##Calculate the BCH
                self.calculatedBCH = Func.calcBCH(self.bits[1:], 0, 202, 250)

                self.tablebin.append(['Calculated',
                                      self.calculatedBCH,
                                      'Computed',
                                      ''])
                ##Compare to the BCH in the beacon message
                self.BCHerrors = Func.errors(self.calculatedBCH, self.bits[203:])

                ##Write the number of errors to our table
                self.tablebin.append(['',
                                      '',
                                      'Number of BCH errors:',
                                      str(self.BCHerrors)])

                self.tablebin.append(['251-252 (padding)',
                                      self.bits[251:],
                                      '00',
                                      '63 hex code of 252 bits'])





        elif len(self.bits) == 92:
            self.type = ('Hex string length of {}. \nBit length of {}. \nThis is a second generation beacon UIN'.format(str(len(strhex)),str(len(self.bits))))
            self.type='uin'
            ##Add an additional bit to ensure that bits in array line up with bits in documentation
            self.bits = "0" + self.bits

            self.latitude = self.longitude = 'No latitude data available'
            self.tablebin.append(['Unique ID','Second Generation','',''])
            self.tablebin.append(['1',
                                  self.bits[1],
                                  'should be 1',
                                  ['ERROR', 'OK'][int(self.bits[1])]])
            ##BIT 2-11 Country code
            self.countryCode = Func.bin2dec(self.bits[2:12])
            self.countryName = Func.countryname(self.countryCode)
            self.tablebin.append(['2-11',
                                  self.bits[2:12],
                                  'Country code:',
                                  str(self.countryCode) + ' ' + str(self.countryName)])
            ##BIT 12-14 Should be 101
            if self.bits[12:15] == '101':
                status_check = 'OK'
            else:
                status_check = 'ERROR'
            self.tablebin.append(['12-14',
                                  self.bits[12:15],
                                  'Should be 101',
                                  status_check])
            ##BIT 15-34  Type Approval Certificate #
            self.tac = Func.bin2dec(self.bits[15:35])
            self.tablebin.append(['15-34',
                                  self.bits[15:35],
                                  'Type Approval Certificate #',
                                  str(self.tac)])
            ##BIT 35-44 Beacon Serial Number
            self.serialNum = Func.bin2dec(self.bits[35:45])
            self.tablebin.append(['35-44',
                                  self.bits[35:45],
                                  'Serial Number',
                                  str(self.serialNum)])

            ##BIT 45-91 Aircraft / Vessel ID
            self.vesselIDfill(46, self.bits[45:92])




            ##BIT 92 Fixed value 1
            self.tablebin.append(['92',
                                  self.bits[92],
                                  'Fixed 1',
                                  self.bits[92]=='1'])

        else:
            self.type = ('Hex string length of ' + str(len(strhex)) + '.'
                         + '\nBit string length of ' + str(len(self.bits)) + '.'
                         + '\nLength of First Gen Beacon Hex String must be 15, 22 or 30'
                         + '\nLength of Second Gen Beacon Bit String must be 252 bits')
            raise Gen2Error('LengthError', self.type)
    def bitlabel(self,a,b,c):
        return str(int(a)-int(c))+'-'+str(int(b)-int(c))

    def vesselIDfill(self,deduct_offset,bits):


        self.vesselID = bits[0:3]
        self.tablebin.append([self.bitlabel(91,93,deduct_offset), self.vesselID , 'Vessel ID Type', Func.getVesselid(self.vesselID)])

        ##############################################
        # Vessel 0: No aircraft or maritime identity #
        ##############################################

        if self.vesselID == '000':


            if Func.checkzeros(bits[3:47]):

                self.tablebin.append([self.bitlabel(94,137,deduct_offset),
                                      bits[3:47],
                                      'Spare:',
                                      'All 0 - OK'])
            else:
                self.tablebin.append([self.bitlabel(94, 137,deduct_offset),
                                      bits[3:47],
                                      'Spare:',
                                      'Error! Should be all 0'])
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
                                      'Unique ship station identity MIDxxYYYY:',
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
                                  self.callsign])
            if Func.checkzeros(bits[45:47]):
                status_check='OK'
            else:
                status_check = 'ERROR'
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
            if Func.checkzeros(bits[45:47]):
                status_check = 'OK'
            else:
                status_check = 'ERROR'
            self.tablebin.append([self.bitlabel(136,137,deduct_offset),
                                  self.bits[45:47],
                                  'Spare should be 0',
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
                                  'Aircraft operator:',
                                  self.operator])
            self.tablebin.append([self.bitlabel(112,123,deduct_offset),
                                  bits[21:33],
                                  'Serial number:',
                                  str(self.serialnum)])


            if Func.checkones(bits[33:47]):
                status_check = 'OK'
            else:
                status_check = 'ERROR'
            self.tablebin.append([self.bitlabel(124,137,deduct_offset),
                                  bits[33:47],
                                  'Spare all should be 1',
                                  status_check])




    def country(self):
        return (('Country Code:', self.countryCode), ('Country Name:', self.countryName))

    def has_loc(self):
        if self.latitude == 'No latitude data available' or self.latitude == 'Invalid Latitude' or self.longitude == 'No longitude data available' or self.longitude == 'Invalid Longitude':
            return False
        else:
            return True




