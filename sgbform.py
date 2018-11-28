from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators, DecimalField, SelectField,RadioField
from decodefunctions import is_number, dec2bin
from Gen2functions import encodeLatitude,encodeLongitude, bin2hex, hex2bin, calcBCH
#from writebch import calcBCH r

class SGB(Form):

    northsouth = RadioField(label='', choices=[('0', 'North'), ('1', 'South')], validators=[validators.DataRequired()],default='0')
    eastwest = RadioField(label='', choices=[('0', 'East'), ('1', 'West')], validators=[validators.DataRequired()], default='0')
    latitude = DecimalField(label='Latitude (0-90)', places=10, validators=[validators.optional(),
                                                                            validators.NumberRange(min=0, max=90,
                                                                                                   message='latitude needs to be 0-90 degrees')])
    longitude = DecimalField(label='Longitude (0-180)', places=10, validators=[validators.optional(),
                                                                               validators.NumberRange(min=0, max=180,
                                                                                                      message='longitude needs to be 0-180 degrees')])


    homingdevice = SelectField(label='Homing device:',
                            choices=[('0', 'No auxiliary locating device included in beacon'),
                                     ('1', 'Auxiliary locating device included in beacon')], default='1')

    rlsfunction = SelectField(label='RLS function:',
                               choices=[('0', 'No RLS capability or disabled'),
                                        ('1', 'RLS capability enabled')], default='0')


    beacontype = SelectField(label='Beacon type:',
                               choices=[('000', 'ELT (excludes ELT(DT))'),
                                        ('001', 'EPIRB'),
                                        ('010', 'PLB'),('011', 'ELT(DT)'),('100','Spare'),
                                        ('101', 'Spare'),
                                        ('110', 'Spare'),
                                        ('111', 'Spare')], default='000')

    def longSGB(form,h):
        binid = hex2bin(h)
        ctrybin = binid[1:11]
        tanobin = binid[14:30]
        snbin = binid[30:44]
        tprotocol= binid[44]
        idbin = binid[45:92]
        if form.latitude.data == None:
            latbin = '01111111000001111100000'
        else:
            latbin = form.northsouth.data + encodeLatitude(float(form.latitude.data))
        if form.longitude.data == None:
            longbin = '011111111111110000011111'
        else:
            longbin = form.eastwest.data + encodeLongitude(float(form.longitude.data))


        completebin = tanobin + snbin + ctrybin + form.homingdevice.data + \
                      form.rlsfunction.data + tprotocol + \
                      latbin + longbin + idbin + form.beacontype.data  +  14 * '1'
        return completebin


class SGB_g008(SGB):
    dops=[('0000','DOP <= 1'),
          ('0001','DOP > 1 and <= 2'),
          ('0010','DOP > 2 and <= 3'),
          ('0011','DOP > 3 and <= 4'),
          ('0100','DOP > 4 and <= 5'),
          ('0101','DOP > 5 and <= 6'),
          ('0110','DOP > 6 and <= 7'),
          ('0111','DOP > 7 and <= 8'),
          ('1000','DOP > 8 and <= 10'),
          ('1001','DOP > 10 and <= 12'),
          ('1010','DOP > 12 and <= 15'),
          ('1011','DOP > 15 and <= 20'),
          ('1100','DOP > 20 and <= 30'),
          ('1101','DOP > 30 and <= 50'),
          ('1110','DOP > 50 '),
          ('1111','DOP not available')]

    activation = [('00','Manual Activation by user'),
                  ('01','Automatic Activation by the beacon'),
                  ('10','Automatic Activation by external means')]
    battery = [('111','Battery Capacity Not Available'),
               ('000','<= 5% remaining'),
               ('001','> 5% and <= 10% remaining'),
               ('010','> 10% and <= 25% remaining'),
               ('011','> 25% and <= 50% remaining'),
               ('100','> 50% and <= 75% remaining'),
               ('101','> 75% and <= 100% remaining')]

    hours= IntegerField(label='0 - 63 hours since activation',
                        validators=[validators.NumberRange(min=0, max=63,
                                                           message='Needs to be 0-63')],default=0)
    minutes = IntegerField(label='0 - 2046 min since last encoded location or blank',
                        validators=[validators.optional(),validators.NumberRange(min=0, max=2046,
                                                           message='Needs to be 0-2046')])

    altitude = IntegerField(label='Altitude (-400 to 15,952 meters)',
                           validators=[validators.optional(),validators.NumberRange(min=-400, max=15952, message='range error')])
    hdop = SelectField(label='HDOP:', choices=dops,default='1111')
    vdop = SelectField(label='VDOP:', choices=dops, default='1111')
    act = SelectField(label='Activation method:', choices=activation, default='00')
    bat = SelectField(label='Baterry capacity:', choices=battery, default='111')
    fix = SelectField(label='GNSS location:', choices=[('00','No fix'),
                                                       ('01','2D location only'),
                                                       ('10','3D location')], default='00')
    def encodelong(form,h):


        hoursbin=dec2bin(int(form.hours.data),6)
        if form.minutes.data == None:
            minbin=dec2bin(2047,11)
        else:
            minbin=dec2bin(int(form.minutes.data),11)

        if form.altitude.data==None:
            altbin='1'*10
        else:
            a= round((float(form.altitude.data+ 400)/16),0)
            altbin = dec2bin(a,10)


        completebin = form.longSGB(h) + '0000' + hoursbin + minbin + altbin + form.hdop.data + form.vdop.data + form.act.data + form.bat.data + form.fix.data + '00'
        bch=calcBCH(completebin,0,202,250)
        print(completebin)
        return bin2hex('00'+completebin+bch)

