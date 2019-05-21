from flask import Flask, Response,flash,jsonify,request, render_template, Markup, redirect, url_for,make_response, session, abort
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DecimalField, SelectField,RadioField,SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from sgbform import SGB, SGB_g008, SGB_emergency
from fgbform import FirstGenForm,FirstGenStd,FirstGenRLS, FirstGenELTDT
from longfirstgenmsg import encodelongFGB
from decodefunctions import is_number, dec2bin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user
import re
import os
import contacts
import typeapproval
import decodehex2
import definitions
import requests

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#db = SQLAlchemy(app)
app.secret_key = 'my secret'
login_manager = LoginManager()
login_manager.init_app(app)
MENU = False

COUNTRIES=[]
country=open('countries2.csv')
for line in country.readlines():
    COUNTRIES.append(line)
COUNTRIES.sort()

class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"), "JaneDoe": ("JaneDoe", "Jane")}
    def __init__(self, username, password):
        self.id = username
        self.password = password
    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

class LoginForm(FlaskForm):
    """User Login Form."""
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        #rv = Form.validate(self)
        #if not rv:
        #    return False
        #user = User.query.filter_by(username=self.username.data).first()
        user = User(self.username.data,self.password.data)
        print(user.self.username.data)
        if user(self.username.data) is None:
            self.username.errors.append('Unknown username')
            return False

        #if not user.check_password(self.password.data):
        #    self.password.errors.append('Invalid password')
        #    return False

        self.user = user(self.username.data)
        return True

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')
    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None


@app.route("/protected/",methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(form.user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)

#
# class Book(db.Model):
#     title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
#     def __repr__(self):
#         return "<Title: {}>".format(self.title)

# @app.route("/add", methods=["GET", "POST"])
# def home():
#     if not session.get('logged_in'):
#         return render_template('login.html')
#     else:
#         # books = None
#         # if request.form:
#         #     try:
#         #         book = Book(title=request.form.get("title"))
#         #         db.session.add(book)
#         #         db.session.commit()
#         #     except Exception as e:
#         #         print("Failed to add book")
#         #         print(e)
#         # books = Book.query.all()
#         #return render_template("books.html", books=books)
#         return redirect(url_for('decode'))
#


@app.route('/validatehex', methods=['GET'])
def validatehex():
    ret_data =  str(request.args.get('hexcode')).strip()
    vlengths=request.args.getlist('lenval[]')
    hexaPattern = re.findall(r'([A-F0-9])', ret_data,re.M|re.I)
    statuscheck='length'
    message = 'Enter a valid beacon hex message'
    new_data=ret_data.upper()
    if len(ret_data) > 0:
        if len(hexaPattern)==len(ret_data):
            message='Valid hexadecimal message.'
            if str(len(ret_data)) in vlengths:
                statuscheck = 'valid'
            else:

                message = 'Bad length '+str(len(ret_data)) + ' Valid lengths: {}'.format(','.join(vlengths))
        else:
            statuscheck='not valid'
            new_data=re.sub(r'[^.a-fA-F0-9]', "", ret_data)
            message='Invalid hexadecimal character (A-F-0-9)'
            new_data=new_data.upper()

    return jsonify(echostatus=statuscheck, message=message,newdata=new_data)


@app.route("/autocomplete",methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results= [k for k in COUNTRIES if k.upper().startswith(search.upper())]
    return jsonify(matching_results=results)


@app.route("/getta",methods=['GET'])
def getta():
    s = request.args.get('a')
    sn= definitions.dec2bin(int(s),16)
    if len(sn) > 16:
        sn = '1' * 16

    return jsonify(tacbin=sn,tadec=int(sn,2))

@app.route("/getsn",methods=['GET'])
def getsn():
    s = request.args.get('a')
    sn= definitions.dec2bin(int(s),14)
    if len(sn)>14:
        sn='1'*14
    print(int(sn, 2))
    return jsonify(snbin=sn,sndec=int(sn, 2))


@app.route("/getmid",methods=['GET'])
def getmid():
    search = request.args.get('a')
    result=definitions.Country(search,{})
    resultdec=result.retmid()
    resultbin=result.getmid()

    return jsonify(mid=resultdec, midbin=resultbin)




## Encoder
@app.route("/encodehex")
def encodehex():
    countries=[]
    for key in definitions.countrydic:
        countries.append('{} ({})'.format(definitions.countrydic[key], key))
    countries.sort()
    return render_template("encodehexunique.html", countries=countries,showmenu=MENU)

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
    forms={'0000': SGB_g008(request.form), '0001': SGB_emergency(request.form)}
    form = forms[rotatefld]
    if request.method == 'POST' and form.validate():
        ## print('valid')
        # hexcodelong = request.form['homingdevice'] + request.form['rlsfunction'] + request.form['beacontype']
        # hexcodelong = encodelongFGB(hexcodeUIN, lat, latdir, long, longdir, suppdata)
        # print(form.encodelong(hexcodeUIN))
        return redirect(url_for('decoded', hexcode=form.encodelong(hexcodeUIN)))

    return render_template('encodelongSGBentryform.html', hexcode=hexcodeUIN, ptype=rotatefld, form=form, error=error,showmenu=MENU)

@app.route('/longfirstgen', methods=['GET','POST'])
def longfirstgen():
    hexcodeUIN = str(request.args.get('hex_code'))
    error = None
    beacon = decodehex2.BeaconFGB(hexcodeUIN)
    ptype = beacon.loctype()
    if ptype == 'National User':
        return redirect(url_for('decoded', hexcode=hexcodeUIN + '0' * 15))

    if beacon.protocolflag()=='User':
        ptype = 'User'

    forms={'User': FirstGenForm(request.form),'Standard Location':FirstGenStd(request.form),
           'Standard Location Protocol - Test':FirstGenStd(request.form),'Standard Location Protocol - PLB (Serial)':FirstGenStd(request.form),
           'National Location':FirstGenStd(request.form),'RLS Location':FirstGenRLS(request.form),'ELT-DT Location':FirstGenELTDT(request.form)}
    form = forms[ptype]

    if request.method == 'POST' and form.validate():

        lat = request.form['latitude']
        latdir=request.form['northsouth']
        long = request.form['longitude']
        longdir =request.form['eastwest']
        if ptype == 'User':
            suppdata = request.form['encodepos']

        elif ptype in ['Standard Location', 'National Location','Standard Location Protocol - Test','Standard Location Protocol - PLB (Serial)']:
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

    return render_template('encodelongfirstentryform.html', hexcode=hexcodeUIN, ptype=ptype, form=form, error=error,showmenu=MENU)

@app.route('/long',methods=['GET'])
def long():
    hexcode=str(request.args.get('hex_code'))
    return redirect(url_for('decoded', hexcode=hexcode))

## Decoder
@app.route("/decodedjson/<hexcode>")
def decodedjson(hexcode):
    # perform independent basic validation of hex code for length and specifications. Basic check
    # that hex code can be decoded.
    # if pass test, then make the beacon object
    beacon = decodehex2.Beacon(hexcode)
    # decode , FGB , SGB and if there is any error, describe errors (eg : BCH errors)
    # if message is valid, then complete the dictionary of all relevant keys.
    if beacon.type=='uin':
        if beacon.gentype=='first':
            tmp = 'FGB unique identifier'
        elif beacon.gentype=='second':
            tmp = 'SGB unique identifier'
    else:
        tmp='long message'
    if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
        geocoord = (float(beacon.location[0]),float(beacon.location[1]))
    else:
        geocoord = (0,0)
    beacondecode= {'type': tmp, 'loc': geocoord}
    return jsonify(beacondecode)

@app.route("/decode",methods=['GET','POST'])
def decode():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('decodehex.html', title='Home', user='',showmenu=MENU)

@app.route("/decoded/<hexcode>")
def decoded(hexcode):
    flds = [('Organization','name'),
            ('Address','address'),
            ('City','city'),
            ('Zip code','zipcode'),
            ('Phone','telephone1'),
            ('Alternate Phone:','telephone2'),
            ('Email:', 'email'),
            ('Contact Website','ci_webpage_1'),
            ('Other information','website_url')]
    contacttypes = ['PLB','ELT','EPIRB']
    tflds2 = [('Model','name'),
             ('',{'manufacturer_id':['name','short_name']}),
             ('Manufacturer', 'manufacturer_id'),
             ('ID','id'),
             ('Sub TAC','database_id'),
             ('Other name','model_add_names'),
             ('Battery','battery'),
             ('Protocols Tested','protocols_tested')]
    tflds = [('Model', 'name')]

    # send POST request to jotforms for logging
    ipaddress=str(request.remote_addr)
    #print(request.remote_addr)
    geocoord = (0, 0)
    locationcheck = False
    try:
        beacon = decodehex2.Beacon(hexcode)
        error=''
        if len(beacon.errors)>0 :
            error = ', '.join(beacon.errors)
        # r = requests.post(
        #     "https://api.jotform.com/form/81094797858275/submissions?apiKey=b552ce4b21da2fe219a06fea0a9088c5&submission[3]="
        #     + hexcode + "&submission[4]=" + ipaddress+ "&submission[5]=" + error)
        #print(beacon.type=='uin')
        if beacon.type=='uin':
            if beacon.gentype=='first':
                tmp = 'encodelongfirst.html'
                # redirect with the hexcode, beacon type - different inputs depending on type of first gen
            elif beacon.gentype=='second':
                tmp = 'encodelongsecond.html'
            elif beacon.gentype=='secondtruncated':
                tmp = 'output.html'
        else:

            tmp='output.html'

        if beacon.has_loc() and is_number(beacon.location[0]) and is_number(beacon.location[1]):
            geocoord = (float(beacon.location[0]),float(beacon.location[1]))
            locationcheck=True
        mid=str(beacon.get_mid())
        #print([c[0] for c in contacttypes])
        #print(contacts.contact(mid,[f[1] for f in flds],[c[0] for c in contacttypes]))
        taclist=typeapproval.tac(beacon.gettac(),[f[1] for f in tflds])
        taclist=[]
        tacdic={}
        if len(taclist)>0:
            for l in taclist:
                k=l['id']
                tacdic[k]=l

        return render_template(tmp, hexcode=hexcode.upper(),
                               decoded=beacon.tablebin,
                               locationcheck=locationcheck,
                               geocoord=geocoord,
                               genmsg=beacon.genmsg,
                               uin = beacon.hexuin(),
                               contact=contacts.contact(mid,[f[1] for f in flds],contacttypes),
                               types=contacttypes,
                               flds=flds,
                               tac=beacon.gettac(),
                               tacdetail=tacdic,
                               tacflds=tflds,
                               showmenu=MENU)
    except decodehex2.HexError as err:
        print(err.value,err.message)
        return render_template('badhex.html',errortype=err.value,errormsg=err.message)

@app.route("/bch/<hexcode>")
def download_bch(hexcode):
    beacon = decodehex2.Beacon(hexcode)
    bchout=beacon.bchstring
    response = make_response(bchout)
    cd = 'attachment; filename=mybch.txt'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response

@app.route("/about")
def about():
    return render_template("about.html",showmenu=MENU)

@app.route("/contact/<num>")
def contact(num):
    flds=['name','address','city','zipcode','telephone1','telephone2','ci_webpage_1','website_url']
    types = ['PLB','ELT','EPIRB']
    return render_template("contact.html",contact=contacts.contact(num,flds,types),types=types,flds=flds,showmenu=MENU)


@app.route("/whereregister/<hexcode>")
def whereregister(hexcode):
    beacon = decodehex2.Beacon(hexcode)
    return render_template('whereregister.html', hexcode=hexcode.upper(), decoded=beacon.tablebin, genmsg=beacon.genmsg+beacon.get_country(),showmenu=MENU)


@app.route('/ibrdallowed',methods=['GET','POST'])
def ibrdallowed():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()

        return redirect(url_for('whereregister',hexcode=hexcode))
    return render_template('ibrdallowed.html', title='Home', user='',showmenu=MENU)

@app.route("/",methods=['GET','POST'])
@app.route("/index")
def index():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('indx.html', title='Home', user='',showmenu=MENU)

if __name__ == "__main__":
    app.secret_key = 'my secret'
    app.run(debug=True,host='0.0.0.0', port=5555, threaded=True)
