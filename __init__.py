from flask import Flask, jsonify,request, render_template, Markup, redirect, url_for
import re
import decodehex2
import definitions
import sys
import Gen2secondgen as Gen2
import Gen2functions
app = Flask(__name__)

COUNTRIES=[]
for key in definitions.countrydic:
    COUNTRIES.append('{} ({})'.format(definitions.countrydic[key], key))
COUNTRIES.sort()

@app.route('/processhex', methods=['GET'])
def processhex():
    ret_data1 = str(request.args.get('a')).strip()
    ret_data2 = str(request.args.get('b')).strip()
    btype=request.args.get('allform')['beacontype']

    retdata = ret_data1 + 'hello' + ret_data2 +  btype
    statuscheck = 'valid'
    return jsonify(returndata=retdata,echostatus=statuscheck)



@app.route('/validatehex', methods=['GET'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()

    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='not valid'
    message = 'Enter a valid beacon hex message'
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):

            message='Valid hexidecimal message.'
            if len(ret_data) in [15,30,23,63]:
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
    if len(hexcode) == 63 or len(hexcode) == 51 or len(hexcode) == 75 or len(hexcode) == 23:
        beacon = Gen2.SecondGen(hexcode)

    else:
        beacon = decodehex2.BeaconHex(hexcode)
    #

    decoded = beacon.tablebin
    if beacon.has_loc()==True:
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
        locationcheck=True

    return render_template('output.html', hexcode=hexcode.upper(), decoded=decoded, locationcheck=locationcheck,geocoord=geocoord)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5555)
