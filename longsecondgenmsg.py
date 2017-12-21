Second Generation Beacon Decode Program
import csv
import sys
import Gen2secondgen as Gen2
import decodefunctions as Func1
import Gen2functions as Func2
import wirtebch
import definitions
import math
next_step = False

f = open('outputfile.txt', 'w')
fhex = open('hexout.csv','a')

# test
#test 2
# test 3
# ldkskjdfskljdfsjkl
# abc
def printtxt(txt):
    print txt
    f.write(txt)


##BIT 1-20  Type Approval Certificate #
# Ask for the user input and store it in userInput
while next_step == False:
    try:
        userInput = raw_input('\nPlease enter TAC (0 to 1,048,575): ') or '1'
    except EOFError:
        userInput = 0
    try:
        tac = int(userInput)
    # Catch the exception if the input was not a number
    except ValueError:
        print 'Error: value must be an integer'
        tac = 0
    else:
        bits_tac = Func1.dec2bin(tac).zfill(20)
        if len(bits_tac) != 20:
            print 'Error: input too high.'
        else:
            break
printtxt('TAC# : {}  - binary: {}\n'.format(str(Func2.bin2dec(bits_tac)),bits_tac))



##BIT 21-30 Serial Number
while next_step == False:
    try:
        userInput = raw_input('\nPlease enter beacon serial number (0 to 1023): ') or '1'
    except EOFError:
        userInput = 0
    try:
        serialnum = int(userInput)
    except ValueError:
        print 'Error: value must be an integer'
        serialnum = 0
    else:
        bits_serialnum = Func1.dec2bin(serialnum).zfill(10)
        if len(bits_serialnum) != 10:
            print 'Error: input too high.'
        else:
            break
printtxt('Beacon serial number: {} - binary: {}\n'.format(str(Func2.bin2dec(bits_serialnum)),bits_serialnum))


##BIT 31-40 Country code
while next_step == False:
    try:
        userInput = raw_input('\nPlease enter country code: ')
    except EOFError:
        userInput = 0
    try:
        countrycode = int(userInput)
    except ValueError:
        print 'Error: value must be an integer'
        countrycode = 0
    else:
        bits_countrycode = Func1.dec2bin(countrycode).zfill(10)
        if len(bits_countrycode) != 10:
            print 'Error: input too high.'
        else:
            break
printtxt('Country: {} {} - binary: {}\n'.format(str(countrycode),Func2.countryname(countrycode),bits_countrycode))




################################
#  BIT 91-137 VESSEL ID FIELD  #
################################
while next_step == False:
    vesselID_list=['0: No aircraft or maritime identity',
                   '1: Maritime MMSI',
                   '2: Radio Call Sign',
                   '3: Aircraft Registration Marking (Tail Number)',
                   '4: Aircraft Aviation 24 Bit Address',
                   '5: Aircraft Operator and Serial Number',
                   '6: Spare',
                   '7: Spare']
    #91-93
    for i in vesselID_list:
        print i
    try:
        userInput = raw_input('\nPlease enter a vessel ID:') or '0'
    except EOFError:
        userInput=0
    try:
        vesselID = int(userInput)
    except ValueError:
        print 'Error: value must be an integer'
        vesselID = 0
    else:
        bits_vesselID = Func1.dec2bin(vesselID).zfill(3)
        if len(bits_vesselID) != 3:
            print 'Error: input too long.'
        elif not Func2.isBinary(bits_vesselID):
            print 'Error: invalid input'
        else:
            break

printtxt('\nVessel ID: {} {} \nbinary - {}\n'.format(vesselID, vesselID_list[vesselID],bits_vesselID))

##############################################
# Vessel 0: No aircraft or maritime identity #
##############################################
if vesselID == 0:
    print '\nVessel 0: No aircraft or maritime identity'

    vessel_bits = bits_vesselID + ('0' * 44)


###########################
# Vessel 1: Maritime MMSI #
###########################
elif vesselID == 1:
    print '\nVessel 1: Maritime MMSI'

    while next_step == False:
        userInput = raw_input('\nPlease enter the 6 digit unique vessel number. If there is no MMSI available, enter 111111: ') or '111111'
        try:
            ship_ID = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            ship_ID = 0
        else:
            if ship_ID == 111111:
                bits_shipID = Func1.dec2bin(ship_ID).zfill(30)
                break
            else:
                bits_shipID = Func1.dec2bin(ship_ID + (countrycode * 1000000)).zfill(30)

                printtxt('\nMMSI (MIDxxxxxx) :{}\nbinary: {}\n'.format(str(ship_ID + (countrycode * 1000000)),bits_shipID))

                if len(bits_shipID) != 30:
                    print 'Error: input too long.'
                elif not Func2.isBinary(bits_shipID):
                    print 'Error: invalid input'
                else:
                    break

    while next_step is False:
        userInput = raw_input('\nEnter only the last 4 digit of the EPIRB-AIS system. If no EPIRB-AIS system, enter 10922: ') or '10922'
        try:
            mmsi_ais = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            mmsi_ais = 0
        else:
            bits_mmsi_ais = Func1.dec2bin(mmsi_ais).zfill(14)
            if len(bits_mmsi_ais) != 14:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_mmsi_ais):
                print 'Error: invalid input'
            else:
                break
    printtxt('\nEPIRB-AIS :{}\nbinary: {}\n'.format(str(mmsi_ais), bits_mmsi_ais))
    vessel_bits = bits_vesselID + bits_shipID + bits_mmsi_ais


#############################
# Vessel 2: Radio Call Sign #
#############################
elif vesselID == 2:
    print '\nVessel 2: Radio Call Sign'

    while next_step is False:
        callsign = raw_input('\nPlease enter the 7 character radio call sign: ') or '       '
        if len(callsign) != 7:
            print 'Error: call sign must be 7 characters or blank'
        else:
            break
    callsign_bits = Func2.str2baudot(callsign).zfill(42)
    printtxt('Call sign: {}\nbinary - {}\n'.format(Func2.getCallsign(callsign_bits),callsign_bits))

    vessel_bits = bits_vesselID + callsign_bits + '00'


#########################################################
# Vessel 3: Aricraft Registration Marking (Tail Number) #
#########################################################
elif vesselID == 3:
    print '\nVessel 3: Aricraft Registration Marking (Tail Number)'

    while next_step is False:
        tailnum = raw_input('\nPlease enter the 7 character tail number: ') or '       '
        if len(tailnum) != 7:
            print 'Error: tail number must be 7 characters'
        else:
            break
    tailnum_bits = Func2.str2baudot(tailnum).zfill(42)
    printtxt('Tail number: {}\nbinary - {}\n'.format(Func2.getTailNum(tailnum_bits), tailnum_bits))


    vessel_bits = bits_vesselID + tailnum_bits + '00'


##############################################
# Vessel 4: Aircraft Aviation 24 Bit Address #
##############################################
elif vesselID == 4:
    print '\nVessel 4: Aircraft Aviation 24 Bit Addres'

    while next_step is False:
        userInput = raw_input('\nPlease enter the 24 bit aviation address in integer format: ') or '0'
        try:
            aviation_address = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            aviation_address = 0
        else:
            bits_aviation_address = Func1.dec2bin(aviation_address).zfill(24)
            if len(bits_aviation_address) != 24:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_aviation_address):
                print 'Error: inavlid input'
            else:
                break


    printtxt('24 bit address: {}\nbinary - {}\n'.format(str(Func1.bin2dec(bits_aviation_address)), bits_aviation_address))

    vessel_bits = bits_vesselID + bits_aviation_address + ('0' * 20)


#################################################
# Vessel 5: Aircraft Operator and Serial Number #
#################################################
elif vesselID == 5:
    print '\nVessel 5: Aircraft Operator and Serial Number'

    while next_step is False:
        operator = raw_input('\nPlease enter 3-letter aircraft operator designator: ') or '   '
        if len(operator) != 3:
            print 'Error: aircraft operator designator must be 3 characters'
        else:
            operator_bits = Func2.str2baudot(operator).zfill(18)
            break
    printtxt('Operator Designator: {}\nbinary - {}\n'.format(Func2.baudot2str(operator_bits, 3),operator_bits))

    while next_step is False:
        userInput = raw_input('\nPlease enter the serial number (1 to 4095) as designated by the aircraft operator: ') or '1'
        try:
            aircraft_serialnum = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            aircraft_serialnum = 0
        else:
            if aircraft_serialnum > 4095 or aircraft_serialnum < 1:
                print 'Error: invalid serial number'
            else:
                bits_aircraft_serialnum = Func1.dec2bin(aircraft_serialnum).zfill(12)
                break
    printtxt('Serial {}\nbinary - {}'.format(str(aircraft_serialnum),bits_aircraft_serialnum))

    vessel_bits = bits_vesselID + operator_bits + bits_aircraft_serialnum + ('1' * 14)


##########################
# Other Vessel IDs Spare #
##########################
else:
    print '\nOther Vessel IDs Spare'
    vessel_bits = bits_vesselID + ('0' * 44)
printtxt('\n\nComplete Vessel Bits: {}\n'.format(vessel_bits))

testbin = '1'+ bits_countrycode + '101' +bits_tac + bits_serialnum + vessel_bits +'1'
testhex=Func2.bin2hex(testbin)
printtxt('\nComplete binary UIN: {}\nHex 23 UIN: {}\n'.format(testbin,testhex))
fhex.write('\n'+testhex)


##BIT 138-139 Beacon type

while next_step is False:
    print '\nPlease select beacon type:'
    for x in definitions.beacon_type:
        print (x) + ': ' + definitions.beacon_type[x]
    bits_beacon_type = raw_input() or '00'
    try:
        definitions.beacon_type[bits_beacon_type]
    except KeyError:
        print 'Error: invalid input'
    else:
        break
        printtxt('Beacon: {}\n'.format(definitions.beacon_type[bits_beacon_type]))


##BIT 140-154 Spare bits [137-153]
bits_spare = '1' * 15

userInput = raw_input('\nWould you like to generate complete message? (y/n):') or 'n'
if userInput in 'Yy':
##BIT 41 Status of homing device
    while next_step == False:

        print '\nHoming Status\n0: Beacon is not equipped with any homing signals or deliberately disabled or if activated, homing device is nonfunctional'
        print '1: Beacon is equipped with at least one homing signal. If beacon has been activated, homing device is functional and transmitting'
        try:
            userInput = raw_input('\nEnter homing status: ') or '0'
        except EOFError:
            userInput=0
        try:
            status = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            status = 0
        else:
            bits_status = str(status)
            if len(bits_status) != 1:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_status):
                print 'Error: invalid input'
            else:
                break
    printtxt('Homing status: {} \nbinary - {}\n'.format(Func2.homing(bits_status),bits_status))


    ##BIT 42 Self-test function
    while next_step == False:
        print '\nSelf-test status: '
        print '0: Self-test transmission'
        print '1: Normal beacon operation (transmitting a distress)'
        try:
            userInput = raw_input('Enter self-test status:') or '0'
        except EOFError:
            userInput=0
        try:
            selftest = int(userInput) or '0'
        except ValueError:
            print 'Error: value must be an integer'
            selftest = 0
        else:
            bits_selftest = str(selftest)
            if len(bits_selftest) != 1:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_selftest):
                print 'Error: invalid input'
            else:
                break
    printtxt('Self test status: {} \nbinary - {}\n\n'.format(Func2.selfTest(bits_selftest),bits_selftest))


    ##BIT 43 User cancellation
    while next_step == False:

        usercancel_list=['\n0: Normal beacon operation (transmitting a distress or self-test message)',
                         '1: Test protocol message']
        for i in usercancel_list:
            print i
        try:
            userInput = raw_input('\nPlease enter message status:') or '0'
        except EOFError:
            userInput=0
        try:
            cancel = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            cancel = 0
        else:
            bits_cancel = str(cancel)
            if len(bits_cancel) != 1:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_cancel):
                print 'Error: invalid input'
            else:
                break
    printtxt('User cancellation: {} - binary {}\n'.format(usercancel_list[cancel],bits_cancel))


    ##BIT 44-66 Latitude
    while next_step == False:
        print '\nPlease enter N/S flag: '
        print '0: North'
        print '1: South'
        try:
            userInput = raw_input() or '0'
        except EOFError:
            userInput=0
        try:
            nsflag = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            nsflag = 0
        else:
            bits_latitude = str(nsflag)
            if len(bits_latitude) != 1:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_latitude):
                print 'Error: invalid input'
            else:
                break

    while next_step == False:
        try:
            userInput = raw_input('\nPlease enter latitude in degrees: ') or '127.0302734375'
        except EOFError:
            userInput = 0
        try:
            lat_degrees = float(userInput)
        except ValueError:
            print 'Error: value must be a decimal'
            lat_degrees = 0
        else:
            bits_lat_degrees = Func2.encodeLatitude(lat_degrees)
            if len(bits_lat_degrees) != 22:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_lat_degrees):
                print 'Error: invalid input'
            else:
                bits_latitude = bits_latitude + bits_lat_degrees
                break

    printtxt('\n\nLatitude: {} \nbinary - {}\n'.format(Func2.getlatitude(bits_latitude)[0],bits_latitude))


    ##BIT 67-90 Longitude
    while next_step == False:
        print '\nPlease enter E/W flag: '
        print '0: East'
        print '1: West'
        try:
            userInput = raw_input() or '0'
        except EOFError:
            userInput=0
        try:
            ewflag = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            ewflag = 0
        else:
            bits_longitude = str(ewflag)
            if len(bits_longitude) != 1:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_longitude):
                print 'Error: invalid input'
            else:
                break

    while next_step == False:
        try:
            userInput = raw_input('\nPlease enter longitude in degrees: ') or '255.969696044922'
        except EOFError:
            userInput=0
        try:
            lon_degrees = float(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            lon_degrees = 0
        else:
            bits_lon_degrees = Func2.encodeLongitude(lon_degrees)
            if len(bits_lon_degrees) != 23:
                print 'Error: input too long.'
            elif not Func2.isBinary(bits_lon_degrees):
                print 'Error: invalid input'
            else:
                bits_longitude = bits_longitude + bits_lon_degrees
                break
    printtxt('Longitude: {} \nbinary {}\n'.format(Func2.getlongitude(bits_longitude)[0],bits_longitude))



    #48 BIT ROTATING FIELD  #155-158
    while next_step is False:
        print '\nPlease enter a rotating ID: '
        rotatingfield_list = ['0: C/S G.008 Objective Requirements',
                              '1: Inflight Emergency',
                              '2: RLS',
                              '3: National Use',
                              '4: Spare',
                              '5: Spare',
                              '6: Spare',
                              '7: Spare',
                              '8: Spare',
                              '9: Spare',
                              '10: Spare',
                              '11: Spare',
                              '12: Spare',
                              '13: Spare',
                              '14: Spare',
                              '15: Cancellation Message']
        for i in rotatingfield_list:
            print i

        try:
            userInput = raw_input(':') or '0'
        except EOFError:
            userInput = 0
        try:
            rotatingID = int(userInput)
        except ValueError:
            print 'Error: value must be an integer'
            rotatingID = 0
        else:
            if rotatingID > 15 or rotatingID < 0:
                print 'Error: Invalid rotating ID'
            else:
                bits_rotatingID = Func1.dec2bin(rotatingID).zfill(4)
                break

    printtxt('\n\nRotating field: {} \nbinary - {}'.format(rotatingfield_list[rotatingID],bits_rotatingID))
    ##############################################################
    # Rotating Field Type: C/S G.008 Objective Requirements (#0) #
    ##############################################################
    if rotatingID == 0:
        print '\nRotating Field Type: C/S G.008 Objective Requirements (#0)'
        bits_rotating0 = bits_rotatingID

        ##BIT 5-10 (159-164) Elapsed time since activation (0 to 63 hours in 1 hour steps)
        while next_step is False:
            try:
                userInput = raw_input('\nPlease enter elapsed time since activation (0 to 63 hours): ') or '0'
            except EOFError:
                userInput = 0
            try:
                elapsed_time = int(userInput)
            except ValueError:
                print 'Error: value must be an integer'
                elapsed_time = 0
            else:
                if elapsed_time > 63 or elapsed_time < 0:
                    print 'Error: invalid time - set to 63 default'
                    bits_elapsed_time = Func1.dec2bin(63).zfill(6)
                    break

                else:
                    bits_elapsed_time = Func1.dec2bin(elapsed_time).zfill(6)
                    break
        print 'You entered: ' + str(Func1.bin2dec(bits_elapsed_time)) + ' hours'

        bits_rotating0 += bits_elapsed_time

        ##BIT 11-21 (165-175) Time from last encoded location (0 to 2046 minutes in 1 minute steps)
        while next_step is False:
            try:
                userInput = raw_input('\nPlease enter time from last encoded location (0 to 2046 minutes) enter -1 for default: ') or '0'
            except EOFError:
                userInput = 0
            try:
                last_encoded_loc = int(userInput)
            except ValueError:
                print 'Error: value must be an integer'
                last_encoded_loc = 0
            else:
                if last_encoded_loc < -1 or last_encoded_loc > 2046:
                    print 'Error: invalid time'
                elif last_encoded_loc == -1 :
                    bits_last_encoded_loc = Func1.dec2bin(2047).zfill(11)
                    break
                else:
                    bits_last_encoded_loc = Func1.dec2bin(last_encoded_loc).zfill(11)
                    break
        print 'You entered: ' + str(Func1.bin2dec(bits_last_encoded_loc)) + ' minutes'

        bits_rotating0 += bits_last_encoded_loc

        printtxt('\n\nTime elapsed since activation - (hours:minutes) - {}:{}\n'.format(elapsed_time,last_encoded_loc))
        printtxt('binary (bits 159-175): - {}{}'.format(str(bits_elapsed_time),str(bits_last_encoded_loc)))

        ##BIT 22-31 (176-185) Altitude of encoded location
        while next_step is False:

            try:
                userInput = raw_input('\nPlease enter altitude in metres (-400 to 15,952): ') or '0'
            except EOFError:
                userInput = 0
            try:
                altitude = int(userInput)
            except ValueError:
                print 'Error: value must be an integer between -400 and 15,952'
                altitude = 0

            else:
                bits_altitude = Func1.dec2bin(int(round(float(altitude + 400)/16))).zfill(10)
                if (altitude+400)>16352:
                    print 'Error: Input too long. Must be an integer between -400 and 15,952'
                elif not Func2.isBinary(bits_altitude):
                    print 'Error: invalid input'
                else:
                    break
        printtxt ('\n\nAltitute entered: {}'.format(str(altitude)))
        printtxt('\nAltitude rounded (meters):{}\nbinary (bits 176-185) - {}\n'.format(str(Func2.getaltitude(bits_altitude)),bits_altitude))
        bits_rotating0 += bits_altitude


        ##BIT 32-39 (186-193) Dilution of precision
        while next_step is False:
            try:
                userInput = raw_input('\nPlease enter Horizontal Dilution of Precision. If HDOP not available, enter 1111: ') or '1111'
            except EOFError:
                userInput = 0
            try:
                hdop = float(userInput)
            except ValueError:
                print 'Error: value must be an float'
                hdop = 1111
            else:
                if hdop == 1111:
                    bits_hdop = '1111'
                else:
                    bits_hdop = Func2.getDopRange(hdop)
                break
        printtxt('\nH{}\nbinary: {}\n'.format(Func2.getDOP(bits_hdop), bits_hdop))
        bits_rotating0 += bits_hdop

        while next_step is False:
            try:
                userInput = raw_input('\nPlease enter Vertical Dilution of Precision. If VDOP not available, enter 1111: ') or '1111'
            except EOFError:
                userInput = 0
            try:
                vdop = float(userInput)
            except ValueError:
                print 'Error: value must be a float'
                vdop = 1111
            else:
                if vdop == 1111:
                    bits_vdop = '1111'
                else:
                    bits_vdop = Func2.getDopRange(vdop)
                break
        printtxt('\nV{}\nbinary: {}\n'.format(Func2.getDOP(bits_vdop),bits_vdop))
        bits_rotating0 += bits_vdop


        ##BIT 40-41 (194-195) Automated/manual activation notification

        while next_step is False:

            print '\nPlease select activation method:\n'
            activation_method_list=['0: Manual activation by user',
                                    '1: Automatic activation by the beacon',
                                    '2: Automatic activation by external means',
                                    '3: Spare']

            for i in activation_method_list:
                print i
            try:
                selection = raw_input() or '0'
            except EOFError:
                bits_activation = '0'
            try:
                bits_activation = Func1.dec2bin(int(selection)).zfill(2)
            except ValueError:
                print "Invalid Entry"
            else:
                break
        printtxt('\n{}   {}   \nbinary - {}\n'.format(str(selection),activation_method_list[int(selection)],bits_activation))

        bits_rotating0 += bits_activation

        ##BIT 42-44 (196-198) Remaining battery capacity
        while next_step is False:

            try:
                userInput = raw_input('\nPlease enter remaining batter capacity (%). If unavailable, enter 111: ') or '111'
            except EOFError:
                userInput = ''
            try:
                battery = int(userInput)
            except ValueError:
                print 'Error: value must be an integer'
                battery = 111

            else:
                if battery <= 5:
                    bits_battery = '000'
                elif battery > 5 and battery <= 10:
                    bits_battery = '001'
                elif battery > 10 and battery <= 25:
                    bits_battery = '010'
                elif battery > 25 and battery <= 50:
                    bits_battery = '011'
                elif battery > 50 and battery <= 75:
                    bits_battery = '100'
                elif battery > 75 and battery <= 100:
                    bits_battery = '101'
                else:
                    bits_battery = '111'
                break
        printtxt('\nBattery Capacity: {} \nbinary - {}\n'.format(definitions.battery[bits_battery],bits_battery))

        bits_rotating0 += bits_battery

        ##BIT 45-46 (199-200) GNSS status
        while next_step is False:
            print '\nPlease select GNSS status:'
            gnss_status_list = ['0: No fix',
                                '1: 2D location only',
                                '2: 3D location',
                                '3: Reserved for future use']

            for x in gnss_status_list:
                print x
            try:
                gnss = raw_input() or '0'
            except EOFError:
                bits_gnss = ''
            try:
                bits_gnss=Func1.dec2bin(int(gnss)).zfill(2)
            except ValueError:
                print 'Error: invalid input'
            else:
                break
        printtxt('GNSS status: {} \nbinary {}'.format(gnss_status_list[int(selection)],bits_gnss))

        bits_rotating0 += bits_gnss

        ##BIT 47-48 (201-202) Spare
        bits_rotating0 += '00'

        rotatingfield = bits_rotating0


    ################################################
    # Rotating Field Type: Inflight Emergency (#1) #
    ################################################
    elif rotatingID == 1:
        print '\nRotating Field Type: Inflight Emergency (#1)'
        bits_rotating1 = bits_rotatingID

        ##BIT 5-21 (159-175) Time of last encoded location
        while next_step is False:
            encoded_loc_time = raw_input('Please enter time of last encoded location in the following format hh:mm:ss : ') or '00:00:00'
            try:
                encoded_loc_sec = int(encoded_loc_time[0:2]) * 3600 + int(encoded_loc_time[3:5]) * 60 + int(encoded_loc_time[6:])
            except ValueError:
                print 'Error: invalid input'
            else:
                bits_encoded_loc_time = Func1.dec2bin(encoded_loc_sec).zfill(17)
                break
        printtxt('\nTime: {}  \nbinary - {} '.format(Func2.sec2utc(bits_encoded_loc_time),bits_encoded_loc_time))

        bits_rotating1 += bits_encoded_loc_time


        ##BIT 22-31 (176-185) Altitude of encoded location
        while next_step is False:
            userInput = raw_input('\nPlease enter altitude in metres: ') or '0'
            try:
                altitude = int(userInput)
            except ValueError:
                print 'Error: value must be an integer'
                altitude = 0
            else:


                bits_altitude = Func1.dec2bin(int(round(float(altitude + 400) / 16))).zfill(10)
                if len(bits_altitude) != 10:
                    print 'Error: Input too long. Must be an integer between -400 and 15,952'
                elif not Func2.isBinary(bits_altitude):
                    print 'Error: invalid input'
                else:
                    break
        printtxt('\n\nAltitute entered: {}'.format(str(altitude)))
        printtxt('\nAltitude rounded (meters):{}\nbinary - {}\n'.format(str(Func2.getaltitude(bits_altitude)),bits_altitude))




        bits_rotating1 += bits_altitude


        ##BIT 32-35 (186-189) Triggering event
        while next_step is False:
            print '\nPlease select triggering event:'
            for x in definitions.triggering_event:
                print (x) + ': ' + definitions.triggering_event[x]
            bits_trigger = raw_input()
            try:
                definitions.triggering_event[bits_trigger]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
        printtxt('\nTriggering event:{} \nbinary {}'.format(definitions.triggering_event[bits_trigger],bits_trigger))

        bits_rotating1 += bits_trigger


        ##BIT 36-37 (190-191) GNSS Status
        while next_step is False:
            print '\nPlease select GNSS status:'
            for x in definitions.gnss_status:
                print (x) + ': ' + definitions.gnss_status[x]
            bits_gnss = raw_input()
            try:
                definitions.gnss_status[bits_gnss]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
        print 'You entered: ' + definitions.gnss_status[bits_gnss]

        bits_rotating1 += bits_gnss


        ##BIT 38-39 (192-193) Remaining battery capacity
        while next_step is False:
            print '\nPlease select remaining battery capacity:'
            for x in definitions.inflight_battery:
                print (x) + ': ' + definitions.inflight_battery[x]
            bits_inflight_battery = raw_input()
            try:
                definitions.inflight_battery[bits_inflight_battery]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
        print 'You entered: ' + definitions.inflight_battery[bits_inflight_battery]

        bits_rotating1 += bits_inflight_battery

        ##BIT 40-48 (194-202) Spare
        bits_rotating1 += (9 * '0')

        rotatingfield = bits_rotating1


    #################################
    # Rotating Field Type: RLS (#2) #
    #################################
    elif rotatingID == 2:
        print '\nRotating Field Type: RLS (#2)'
        bits_rotating2 = bits_rotatingID
        # length = 4


        ##BIT 5-6 (159-160) Beacon distress type
        while next_step is False:
            print '\nPlease select beacon distress type:'
            for x in definitions.beacon_distress_type:
                print (x) + ': ' + definitions.beacon_distress_type[x]
            bits_beacon_distress_type = raw_input() or '00'
            try:
                definitions.beacon_distress_type[bits_beacon_distress_type]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
                printtxt('Beacon: {}\n'.format(definitions.beacon_distress_type[bits_beacon_distress_type]))

        bits_rotating2 += bits_beacon_distress_type
        # length = 6

        ##BIT 7-12 (161-166) Beacon RLS Capability
        while next_step is False:
            print '\nRLS capability:'
            for x in definitions.beacon_rls:
                print (x) + ': ' + definitions.beacon_rls[x]
            bits_beacon_rls = raw_input() or '00'
            try:
                definitions.beacon_rls[bits_beacon_rls]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
        printtxt('RLS: {}\n'.format(definitions.beacon_rls[bits_beacon_rls]))
        bits_rotating2 += bits_beacon_rls + '0000'
        # length = 12


        while next_step is False:
            print '\nRLS provider:'
            for x in definitions.rls_provider:
                print (x) + ': ' + definitions.rls_provider[x]
            bits_beacon_rls_provider = raw_input() or '000'
            try:
                definitions.rls_provider[bits_beacon_rls_provider]
            except KeyError:
                print 'Error: invalid input'
            else:
                break

        printtxt('\nRLS provider: {}\n'.format(definitions.rls_provider[bits_beacon_rls_provider]))
        bits_rotating2 += bits_beacon_rls_provider
        # length = 15
        if bits_beacon_rls_provider=='001':
            while next_step is False:
                short_longb16 = raw_input('Select: 0 = Type 1 not received | OR 1 = Type 1 received :') or '0'
                if short_longb16 in '01' and len(short_longb16)==1:
                    bits_rotating2 += str(short_longb16)
                    break

            while next_step is False:
                short_longb17 = raw_input('Select: 0 = Type 2 not received | OR 1 = Type 2 received :') or '0'
                if short_longb17 in '01' and len(short_longb17)==1:
                    bits_rotating2 += str(short_longb17)
                    break
            bits_rotating2 += '0' * 20

        else:
            bits_rotating2 += '0'*22
        bits_rotating2 += '0' * 11
        # length = 48







        rotatingfield = bits_rotating2
        printtxt('\n Leghth of rotating field : {}'.format(len(rotatingfield)))
        printtxt(rotatingfield)
    ##########################################
    # Rotating Field Type: National Use (#3) #
    ##########################################
    elif rotatingID == 3:
        print '\nRotating Field Type: National Use (#3)'
        bits_rotating3 = bits_rotatingID + ('0' * 44)


        rotatingfield = bits_rotating3

    ###################################################
    # Rotating Field Type: Cancellation Message (#15) #
    ###################################################
    elif rotatingID == 15:
        print '\nRotating Field Type: Cancellation Message (#15)'

        bits_rotating15 = bits_rotatingID + ('1' * 42)

        while next_step is False:
            print '\nPlease select method of deactivation:'
            for x in definitions.deactivation:
                print (x) + ': ' + definitions.deactivation[x]
            bits_deactivation = raw_input()
            try:
                definitions.deactivation[bits_deactivation]
            except KeyError:
                print 'Error: invalid input'
            else:
                break
        print 'You entered: ' + definitions.deactivation[bits_deactivation]

        bits_rotating15 += bits_deactivation

        rotatingfield = bits_rotating15
        bits_spare = '0' * 17


    ####################################
    # All other rotating fields: SPARE #
    ####################################
    else:
        print '\nRotating Field Type: Spare'
        bits_rotating4 = bits_rotatingID + ('0' * 44)


        rotatingfield = bits_rotating4

    printtxt('\nSpare bits (138-154): {}\n'.format(bits_spare))
    ####################################################################################################################################################################################
    bits_maininfo = \
        bits_tac + \
        bits_serialnum + \
        bits_countrycode + \
        bits_status + \
        bits_selftest + \
        bits_cancel + \
        bits_latitude + \
        bits_longitude + \
        vessel_bits + \
        bits_beacon_type + \
        bits_spare
    ####################################################################################################################################################################################



    testbits = bits_maininfo + rotatingfield
    bchbase = bits_maininfo + rotatingfield
    BCH = Func2.calcBCH(bchbase, 0, 202, 250)
    bch2 = wirtebch.calcBCH(bchbase,0,202,250)
    print BCH == bch2

    print bchbase
    print BCH
    print bch2



    testhex = Func2.bin2hex(bchbase + BCH + '00')
    printtxt('\nYour complete beacon message is: ' + testhex)
    fhex.write('\n'+testhex)


try:
    x=raw_input("Done")
except EOFError:
    x=''

newBeacon1 = Gen2.SecondGen(testhex)
newBeacon1.processHex(testhex)



##Add Hex message to export file
newBeacon1.tablebin.append(['Beacon message:',
                            testhex,'',''])


for i in newBeacon1.tablebin:
    x='"'+i[1]
    i[1]=x

with open('my_beacon_excel.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Bit Range', 'Bit Value', 'Number of Bits', 'Field Name', 'Field Value'])
    [writer.writerow(r) for r in newBeacon1.tablebin]


