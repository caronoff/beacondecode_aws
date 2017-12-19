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
    username = StringField('Username', [validators.Length(min=4, max=25)])


    northsouth=RadioField(label='Latitude direction:', choices = [('0', 'North'),('1', 'South')],validators=[validators.DataRequired()])
    eastwest=RadioField(label='Longitude direction:', choices = [('0', 'East'),('1', 'West')],validators=[validators.DataRequired()])
    latitude = DecimalField(label='Latitude (0-90)',places=5, validators=[validators.DataRequired(),validators.NumberRange(min=0,max=90, message='latitude needs to be 0-90 degrees')])
    longitude = DecimalField(label='Longitude (0-180)', places=5, validators=[validators.DataRequired(),
                                                                           validators.NumberRange(min=0, max=180,
                                                                                                  message='longitude needs to be 0-180 degrees')])


    encodepos = SelectField('Source of Encoded location:', choices = [('0', 'External'),('1', 'Internal')])
    auxdevice = SelectField('Auxiliary device:', choices = [('0', 'No auxiliary radio locating device included in beacon'),('1', '121.5 MHz auxiliary radio locating device included in beacon')])

    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])




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


@app.route('/longfirstgen', methods=['GET','POST'])
def longfirstgen():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None
    beacon = decodehex2.BeaconFGB(hexcodeUIN)
    loctype = beacon.protocolflag()
    if loctype == 'User':
        ptype= 'User'
    else:
        ptype = beacon.loctype()
    #various different forms required depending upon the beacon type.  All requiring coordinates for location plus various supplemental bits
    form = FirstGenForm(request.form)


    if request.method == 'POST' and form.validate():
        print(form.username.data)

        lat = request.form['latitude']
        latdir=request.form['northsouth']
        long = request.form['longitude']
        longdir =request.form['eastwest']
        if ptype =='User':
            suppdata=request.form['encodepos']

            # get all data and run longfirstgenmsg.py to compute the hexcode

        elif ptype =='Standard Location':
            suppdata='1101'+request.form['encodepos'] + request.form['auxdevice']
            hexcodelong=encodelongFGB(hexcodeUIN,lat,latdir,long,longdir, suppdata)


        print(suppdata)
        if request.form['username']=='craig':
            flash('You were successfully logged in'+ str(float(form.latitude.data)))
            return redirect(url_for('decoded', hexcode=hexcodelong))
        else:
            error = 'Invalid credentials'

    return render_template('encodelongfirstentryform.html', hexcode=hexcodeUIN, loctype=ptype, form=form, error=error)

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
