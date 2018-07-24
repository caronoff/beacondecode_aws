from wtforms import Form, BooleanField, StringField, IntegerField, PasswordField, validators, DecimalField, SelectField,RadioField


class FirstGenForm(Form):

    northsouth=RadioField(label='', choices = [('0', 'North'),('1', 'South')],validators=[validators.DataRequired()])
    eastwest=RadioField(label='', choices = [('0', 'East'),('1', 'West')],validators=[validators.DataRequired()])
    latitude = DecimalField(label='Latitude (0-90)',places=10, validators=[validators.DataRequired(),validators.NumberRange(min=0,max=90, message='latitude needs to be 0-90 degrees')])
    longitude = DecimalField(label='Longitude (0-180)', places=10, validators=[validators.DataRequired(),
                                                                           validators.NumberRange(min=0, max=180,
                                                                                                  message='longitude needs to be 0-180 degrees')])


    encodepos = SelectField(label='Source of Encoded location:', choices = [('0', 'External source of encoded location'),
                                                                            ('1', 'Internal source of encoded location')], default='0')

class FirstGenStd(FirstGenForm):
    auxdevice = SelectField(label='Auxiliary device:',
                            choices=[('0', 'No auxiliary radio locating device included in beacon'),
                                     ('1', '121.5 MHz auxiliary radio locating device included in beacon')], default='0')


class FirstGenRLS(FirstGenForm):
    auxdevice = SelectField(label='Auxiliary device:', choices = [('0', 'No auxiliary radio locating device included in beacon'),
                                                                  ('1', '121.5 MHz auxiliary radio locating device included in beacon')], default='0')

    rlmtypeone = SelectField(label='Capability to process automatic RLM Type-1:',
                             choices = [('0', 'Type-1 not requested and not accepted by this beacon'),
                                        ('1', 'Acknowledgement Type-1 automatic acknowledgement accepted by this beacon')],
                             default='0')

    rlmtypetwo = SelectField(label='Capability to process manual RLM Type-2:',
                             choices=[('0', 'Manually generated RLM such as Acknowledgement Type-2 not requested and not accepted by this beacon'),
                                      ('1', 'Manually generated RLM such as Acknowledgement Type-2 accepted by this beacon')],
                             default='0')

    feedbacktype1 = SelectField(label='Beacon feedback reception of the RLM Type-1:',choices=[('0', 'Acknowledgement Type-1 not (yet) received by this beacon'),
                                                                               ('1', 'Acknowledgement Type-1 (automatic acknowledgement) received by this beacon')], default='0')

    feedbacktype2 = SelectField(label='Beacon feedback reception of the RLM Type-2:',
                                choices=[('0', 'Acknowledgement Type-2 not (yet) received by this beacon'),
                                         ('1', 'Acknowledgement Type-2 received by this beacon')],
                                default='0')



    rlsprovider = SelectField(label='RLS Provider Identification:',
                                choices=[('00','Spares (for other RLS providers)'),
                                         ('01', 'GALILEO Return Link Service Provider'),
                                         ('10', 'GLONASS Return Link Service Provider'),
                                         ],
                              default='00')


class FirstGenELTDT(FirstGenForm):
    meansactivation=SelectField(label='Means of activation', choices=[('00','Manual activation by user'),('01','Automatic activation by the beacon'),('10','Automatic activation by external means'),('11','Spare')])

    encodedaltitude= SelectField(label='Encoded altitude', choices=[('0000', 'altitude is less than 400 m (1312 ft)'),
                                                                    ('0001', 'altitude is between 400 m (1312 ft) and 800 m (2625 ft)'),
                                                                    ('0010', 'altitude is between 800 m (2625 ft) and 1200 m (3937 ft)'),
                                                                     ('0011','altitude is between 1200 m (3937 ft) and 1600 m (5249 ft)'),
                                                                     ('0100','altitude is between 1600 m (5249 ft) and 2200 m (7218 ft)'),
                                                                     ('0101','altitude is between 2200 m (7218 ft) and 2800 m (9186 ft)'),
                                                                     ('0110','altitude is between 2800 m (9186 ft) and 3400 m (11155 ft)'),
                                                                     ('0111','altitude is between 3400 m (11155 ft) and 4000 m (13123 ft)'),
                                                                     ('1000','altitude is between 4000 m (13123 ft) and 4800 m (15748 ft)'),
                                                                     ('1001','altitude is between 4800 m (15748 ft) and 5600 m (18373 ft)'),
                                                                    ('1010','altitude is between 5600 m (18373 ft) and 6600 m (21654 ft)'),
                                                                    ('1011','altitude is between 6600 m (21654 ft) and 7600 m (24934 ft)'),
                                                                    ('1100','altitude is between 7600 m (24934 ft) and 8800 m (28871 ft)'),
                                                                    ('1101','altitude is between 8800 m (28871 ft) and 10000 m (32808 ft)'),
                                                                    ('1110','altitude is greater than 10000 m (32808 ft)'),
                                                                    ('1111','default value if altitude information is not available')])
    freshness = BooleanField(label='encoded location is fresh')

