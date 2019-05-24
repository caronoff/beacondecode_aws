from flask import Flask, Response,flash,jsonify,request, render_template, Markup, redirect, url_for,make_response, session, abort
from functools import wraps
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DecimalField, SelectField,RadioField,SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from sgbform import SGB, SGB_g008, SGB_emergency
from fgbform import FirstGenForm,FirstGenStd,FirstGenRLS, FirstGenELTDT
from longfirstgenmsg import encodelongFGB
from decodefunctions import is_number, dec2bin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import re
import os
import contacts
import typeapproval
import decodehex2
import definitions

import requests


app = Flask(__name__)
app.secret_key = 'my secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/postgres' #os.environ['DATABASE_URL']
db = SQLAlchemy(app)

migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


MENU = False

COUNTRIES=[]
country=open('countries2.csv')
for line in country.readlines():
    COUNTRIES.append(line)
COUNTRIES.sort()



class Userlogin(db.Model):
    __tablename__ = 'userlogin'
    u_id = db.Column(db.Integer,primary_key=True)
    uname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.uname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """Return the username to satisfy Flask-Login's requirements."""
        return str(self.u_id)


class LoginForm(Form):
    """User Login Form."""
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None



class RegistrationForm(Form):
    u_id = StringField('User identity number', validators=[DataRequired()])
    uname = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_u_id(self, u_id):
        user = Userlogin.query.filter_by(u_id=u_id.data).first()
        if user is not None:
            raise ValidationError('Please use a different number.')


    def validate_uname(self, uname):
        user = Userlogin.query.filter_by(uname=uname.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Userlogin.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


@login_manager.user_loader
def load_user(user_id):
    return Userlogin.query.filter_by(u_id =int(user_id)).first()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['logged_in']=False
    flash('Logged out')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm(request.form)
    user=None

    if request.method== 'POST' and form.validate():
        # Login and validate the user.
        # user should be an instance of your `Userlogin` class

        user = Userlogin.query.filter_by(uname=form.username.data).first()
        if user is not None:
            login_user(user)
            session['logged_in']=True
            flash('Logged in successfully.')
            next_page = request.args.get('next').strip('/')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(url_for( next_page))
        else:
            flash('ERROR! Invalid login credentials')

    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        user = Userlogin(u_id=request.form.get("u_id"),username=request.form.get("uname"), email=request.form.get("email"))
        user.set_password(request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)





@app.route("/adduser", methods=["GET", "POST"])
def home():
    users = None
    if request.form:
        try:
            user = Userlogin(u_id=request.form.get("u_id"),uname=request.form.get("uname"))
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print("Failed to add user")
            print(e)
    users = Userlogin.query.all()
    return render_template("users.html", users=users)



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
@login_required
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


@app.route("/decode",methods=['GET','POST'])
def decode():
    if request.method == 'POST':
        hexcode = str(request.form['hexcode']).strip()
        return redirect(url_for('decoded',hexcode=hexcode))
    return render_template('decodehex.html', title='Home', user='',showmenu=MENU)

if __name__ == "__main__":
    app.secret_key = 'my secret'
    app.run(debug=True,host='0.0.0.0', port=5555, threaded=True)
