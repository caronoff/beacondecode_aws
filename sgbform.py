from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators, DecimalField, SelectField,RadioField
from decodefunctions import is_number, dec2bin
from Gen2functions import encodeLatitude,encodeLongitude

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

    selftest = SelectField(label='Self-Test:',
                               choices=[('0', 'Normal beacon operation'),
                                        ('1', 'Self-test transmition')], default='0')

    testprotocol = SelectField(label='Test protocol:',
                           choices=[('0', 'Normal beacon operation'),
                                    ('1', 'Test protocol transmition')],default='0')

    beacontype = SelectField(label='Beacon type:',
                               choices=[('00', 'ELT'),
                                        ('01', 'EPIRB'),
                                        ('10', 'PLB')], default='00')


class SGB_g008(SGB):
    hours= IntegerField(label='0 - 63 hours since activation',
                        validators=[validators.NumberRange(min=0, max=63,
                                                           message='Needs to be 0-63')],default=0)
    minutes = IntegerField(label='0 - 2047 min since last encoded location',
                        validators=[validators.optional(),validators.NumberRange(min=0, max=2046,
                                                           message='Needs to be 0-2047')])

    altitude = IntegerField(label='Altitude (-400 to 15,952 meters)',
                           validators=[validators.optional(),validators.NumberRange(min=-400, max=15952, message='range error')])

    def encodelong(form,h):
        if form.latitude.data == None:
            latbin='01111111000001111100000'
        else:
            latbin=form.northsouth.data+encodeLatitude(float(form.latitude.data))
        if form.longitude.data == None:
            longbin='011111111111110000011111'
        else:
            longbin=form.eastwest.data+encodeLongitude(float(form.longitude.data))
        hoursbin=dec2bin(int(form.hours.data),6)
        if form.minutes.data == None:
            minbin=dec2bin(2047,11)
        else:
            minbin=dec2bin(int(form.minutes.data),11)




        if form.altitude.data==None:
            altbin='1'*10
        else:
            alt = round(float((form.altitude.data+ 400)/16),0)
            altbin = dec2bin(alt,10)
        return (str(altbin),latbin)
