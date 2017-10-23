from flask import Flask, jsonify,request, render_template, Markup
import re
import decodehex2
import definitions
import sys
import Gen2secondgen as Gen2
import Gen2functions
app = Flask(__name__)



@app.route('/validatehex', methods=['GET','POST'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()
    print(ret_data)
    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='not valid'
    message = 'Enter a valid beacon hex message'
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):

            message='This is a valid hexidecimal message.'
            if len(ret_data) in [15,22,30,23,63]:
                statuscheck = 'valid'
            else:
                message += '  However, length '+str(len(ret_data)) + ' is not a valid message.  Valid message should be 15,22,23,30 or 63.'
        else:
            statuscheck='not valid'
            message='Invalid Hexidecimal code.  (A-F-0-9)'


    return jsonify(echostatus=statuscheck, message=message)

@app.route('/output', methods=['GET','POST'])
def output():
    ## output will only process if hexcode has been validated.
    outputdata="dummy"
    if request.method== 'GET' or request.method=='POST':
        hexcode= str(request.args.get('hexcode'))
        username = str(request.args.get('username'))
        if len(hexcode) == 63 or len(hexcode) == 51 or len(hexcode) == 75 or len(hexcode) == 23:
            beacon = Gen2.SecondGen(hexcode)
        else:
            beacon = decodehex2.BeaconHex(hexcode)
        print(hexcode)
        beacon.processHex(hexcode)
        ctry = beacon.country()
        mid = str(ctry[0][1])
        name = str(ctry[1][1])
        print(name)
        decoded = beacon.tablebin
        return render_template('output.html',hexcode=hexcode,decoded=decoded)
    else:
        return render_template('child.html', title='Home', user="")


@app.route("/")
@app.route("/index")
def index():
    user ={'nickname': 'Craig Aronoff3'}  # fake user
    return render_template('child.html',title='Home',user=user)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5555)
