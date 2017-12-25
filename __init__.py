from flask import Flask, flash,jsonify,request, render_template, Markup, redirect, url_for
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DecimalField, SelectField,RadioField
from longfirstgenmsg import encodelongFGB
import re
import decodehex2
import definitions
import sys
from decodefunctions import is_number, dec2bin
app = Flask(__name__)
app.secret_key = 'my secret'

COUNTRIES=[]
for key in definitions.countrydic:
    COUNTRIES.append('{} ({})'.format(definitions.countrydic[key], key))
COUNTRIES.sort()


class FirstGenForm(Form):

    northsouth=RadioField(label='', choices = [('0', 'North'),('1', 'South')],validators=[validators.DataRequired()])
    eastwest=RadioField(label='', choices = [('0', 'East'),('1', 'West')],validators=[validators.DataRequired()])
    latitude = DecimalField(label='Latitude (0-90)',places=10, validators=[validators.DataRequired(),validators.NumberRange(min=0,max=90, message='latitude needs to be 0-90 degrees')])
    longitude = DecimalField(label='Longitude (0-180)', places=10, validators=[validators.DataRequired(),
                                                                           validators.NumberRange(min=0, max=180,
                                                                                                  message='longitude needs to be 0-180 degrees')])


    encodepos = SelectField(label='Source of Encoded location:', choices = [('0', 'External source of encoded location'),
                                                                            ('1', 'Internal source of encoded location')], default='0')
class SGB(FirstGenForm):
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
    def extract(self,h):
        return str(self.homingdevice.data)+'hex'+h

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


@app.route('/processhex', methods=['GET'])
def processhex():
    protocol=str(request.args.get('protocol'))
    t = definitions.protocolspecific[protocol](request.args,protocol)
    retdata = t.getresult()
    beacon_gen = t.getgen()
    return jsonify(beacon_gen=beacon_gen,binary=retdata['binary'],hexcode=retdata['hexcode'],echostatus=retdata['status'], messages=retdata['message'], flderrors=retdata['flderrors'])



@app.route('/filterlist', methods=['GET'])
def filterlist():
    protocol=str(request.args.get('a'))
    beacontype=str(request.args.get('b'))
    print('protocol: '+protocol+' and beacon: '+beacontype)
    selectdic={"---select protocol---":"0"}
    for l in definitions.pselect[protocol][beacontype]:
        selectdic[l[0]]=l[1]
    statuscheck='valid'
    return jsonify(returndata=selectdic,echostatus=statuscheck)


@app.route('/longSGB', methods=['GET','POST'])
def longSGB():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None


    rotatefld=str(request.args.get('rotatingfield'))
    print(rotatefld,hexcodeUIN)
    forms={'0000': SGB_g008(request.form)}
    form = forms[rotatefld]

    if request.method == 'POST' and form.validate():
        lat = request.form['latitude']
        latdir=request.form['northsouth']
        long = request.form['longitude']
        longdir =request.form['eastwest']

        hexcodelong = request.form['homingdevice'] + request.form['selftest'] + request.form['beacontype'] + request.form['testprotocol']
        #hexcodelong = encodelongFGB(hexcodeUIN, lat, latdir, long, longdir, suppdata)
        print(form.extract(hexcodeUIN))
        #return redirect(url_for('decoded', hexcode=hexcodelong))

    return render_template('encodelongSGBentryform.html', hexcode=hexcodeUIN, ptype=rotatefld, form=form, error=error)

@app.route('/longfirstgen', methods=['GET','POST'])
def longfirstgen():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None
    beacon = decodehex2.BeaconFGB(hexcodeUIN)
    ptype = beacon.loctype()
    if ptype == 'National User':
        return redirect(url_for('decoded', hexcode=hexcodeUIN + '0' * 15))

    forms={'User': FirstGenForm(request.form),'Standard Location':FirstGenStd(request.form), 'National Location':FirstGenStd(request.form),'RLS Location':FirstGenRLS(request.form),'ELT-DT Location':FirstGenELTDT(request.form)}
    form = forms[ptype]

    if request.method == 'POST' and form.validate():

        lat = request.form['latitude']
        latdir=request.form['northsouth']
        long = request.form['longitude']
        longdir =request.form['eastwest']
        if ptype == 'User':
            suppdata = request.form['encodepos']

        elif ptype in ['Standard Location', 'National Location']:
            suppdata='1101'+request.form['encodepos'] + request.form['auxdevice']
        elif ptype == 'RLS Location' :
            suppdata = request.form['encodepos'] + \
                       request.form['auxdevice'] + \
                       request.form['rlmtypeone'] + \
                       request.form['rlmtypetwo'] + \
                       request.form['feedbacktype1'] + \
                       request.form['feedbacktype2'] + \
                       request.form['rlsprovider']
        elif ptype == 'ELT-DT Location':
            suppdata = request.form['meansactivation'] + request.form['encodedaltitude']
            if form.data.get('freshness')==True:
                suppdata = suppdata + '11'
            else:
                suppdata = suppdata + '00'

        hexcodelong = encodelongFGB(hexcodeUIN, lat, latdir, long, longdir, suppdata)
        print('hex', hexcodelong)
        return redirect(url_for('decoded', hexcode=hexcodelong))

    return render_template('encodelongfirstentryform.html', hexcode=hexcodeUIN, ptype=ptype, form=form, error=error)

@app.route('/long',methods=['GET'])
def long():

    hexcode=str(request.args.get('hex_code'))
    return redirect(url_for('decoded', hexcode=hexcode))




@app.route('/validatehex', methods=['GET'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()

    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='not valid'
    message = 'Enter a valid beacon hex message'
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):
            message='Valid hexidecimal message.'
            if len(ret_data) in [15,30,36,23,63]:
                statuscheck = 'valid'
            else:
                message = 'Bad length '+str(len(ret_data)) +  '  Valid lengths: 15 hex, 23 hex, 30 or 63 hex'
        else:
            statuscheck='not valid'
            message='Invalid Hexidecimal code  (A-F-0-9)'
    return jsonify(echostatus=statuscheck, message=message)


@app.route("/",methods=['GET','POST'])
@app.route("/index")
def index():
    if request.method == 'POST':
        print('post')
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('indx.html', title='Home', user='')


@app.route("/decode",methods=['GET','POST'])
def decode():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('decodehex.html', title='Home', user='')


@app.route("/autocomplete",methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results= [k for k in COUNTRIES if k.upper().startswith(search.upper())]
    return jsonify(matching_results=results)

@app.route("/encodehex")
def encodehex():
    countries=[]
    for key in definitions.countrydic:
        countries.append('{} ({})'.format(definitions.countrydic[key], key))
    countries.sort()
    return render_template("encodehex.html", countries=countries)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/decoded/<hexcode>")
def decoded(hexcode):
    geocoord = (0, 0)
    locationcheck = False
    beacon = decodehex2.Beacon(hexcode)
    print(beacon.type=='uin')
    if beacon.type=='uin':
        if beacon.gentype=='first':
            tmp = 'encodelongfirst.html'
            # redirect with the hexcode, beacon type - different inputs depending on type of first gen
        elif beacon.gentype=='second':
            tmp = 'encodelongsecond.html'
    else:
        print('default output.html')
        tmp='output.html'

    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        print(geocoord)
        locationcheck=True

    return render_template(tmp, hexcode=hexcode.upper(), decoded=beacon.tablebin, locationcheck=locationcheck,geocoord=geocoord)


if __name__ == "__main__":
    app.secret_key = 'my secret'
    app.run(debug=True,host='0.0.0.0', port=5555)
