from flask import Flask, jsonify,request, render_template, Markup, redirect, url_for
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import re
import decodehex2
import definitions
import sys
from decodefunctions import is_number, dec2bin
app = Flask(__name__)

COUNTRIES=[]
for key in definitions.countrydic:
    COUNTRIES.append('{} ({})'.format(definitions.countrydic[key], key))
COUNTRIES.sort()

@app.route('/processhex', methods=['GET'])
def processhex():

    btype=request.args.get('beacontype')
    ctry=request.args.get('country')
    midpat = re.compile(r'(\d{3})')
    ccode=int(midpat.search(ctry).groups()[0])
    binctry=dec2bin(ccode)
    gen=str(request.args.get('optgen'))
    tano = str(request.args.get('tano'))
    beaconnoinput = str(request.args.get('beaconnoinput'))
    radio_last3     =str(request.args.get('radio_last3'))
    auxdeviceinput = str(request.args.get('auxdeviceinput'))
    in1 = str(request.args.get('input1'))
    protocol=str(request.args.get('protocol'))
    retdata = btype+ctry+gen+in1+protocol+'  '+tano+ 'Aux :'+auxdeviceinput + beaconnoinput + radio_last3 + str(ccode) + ' '+str(binctry)
    statuscheck = 'valid'
    return jsonify(returndata=retdata,echostatus=statuscheck)


@app.route('/filterlist', methods=['GET'])
def filterlist():
    protocol=str(request.args.get('a'))
    beacontype=str(request.args.get('b'))
    print('protocol: '+protocol+' and beacon: '+beacontype)
    selectdic={"---select new---":"0"}
    for l in definitions.pselect[protocol][beacontype]:
        selectdic[l[0]]=l[1]
    statuscheck='valid'
    return jsonify(returndata=selectdic,echostatus=statuscheck)


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
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('child.html', title='Home', user='')

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
    geocoord=(0,0)
    locationcheck=False
    beacon=decodehex2.Beacon(hexcode)
    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        print(geocoord)
        locationcheck=True


    return render_template('output.html', hexcode=hexcode.upper(), decoded=beacon.tablebin, locationcheck=locationcheck,geocoord=geocoord)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5555)
