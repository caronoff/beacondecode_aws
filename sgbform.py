from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators, DecimalField, SelectField,RadioField

class SGB(Form):

    northsouth = RadioField(label='', choices=[('0', 'North'), ('1', 'South')], validators=[validators.DataRequired()])
    eastwest = RadioField(label='', choices=[('0', 'East'), ('1', 'West')], validators=[validators.DataRequired()])
    latitude = DecimalField(label='Latitude (0-90)', places=10, validators=[validators.DataRequired(),
                                                                            validators.NumberRange(min=0, max=90,
                                                                                                   message='latitude needs to be 0-90 degrees')])
    longitude = DecimalField(label='Longitude (0-180)', places=10, validators=[validators.DataRequired(),
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
    hours= IntegerField(label='0 to 63 hours in one hour steps since activation, shall be truncated, not rounded',
                        validators=[validators.DataRequired(),validators.NumberRange(min=0, max=63,
                                                           message='Needs to be 0-63')])
    minutes = IntegerField(label='0 to 2047 in one minute steps since last encoded location, truncated, not rounded',
                        validators=[validators.DataRequired(),validators.NumberRange(min=0, max=2047,
                                                           message='Needs to be 0-2047')])

    def encodelong(self,h):
        return str(self.homingdevice.data)+'hex'+h + str(self.minutes.data)
