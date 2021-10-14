from flask import Flask, Response,flash,jsonify,request, render_template, Markup, redirect, url_for,make_response, session, abort
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DecimalField, SelectField,RadioField,SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from sgbform import SGB, SGB_g008, SGB_emergency, SGB_national, SGB_rls, SGB_cancel
from fgbform import FirstGenForm,FirstGenStd,FirstGenRLS, FirstGenELTDT,FirstGenNatLoc
from longfirstgenmsg import encodelongFGB
from decodefunctions import is_number, dec2bin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from bchcorrect import bch_check, bch_recalc, bch1_binarycalc, bch2_binarycalc
from botocore.errorfactory import ClientError
import re, uuid
import os, json, boto3
import contacts
import typeapproval
import decodehex2
import definitions
import bchlib
import testbchSGB
# version 2.0 April 14, 2021
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv('.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'Optional default value')
gmap_key = os.getenv('GMAP_KEY', 'Optional default value')
app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ['DATABASE_URL']
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
    lastname = db.Column(db.String(120), index=True, unique=False)
    firstname = db.Column(db.String(120), index=True, unique=False)
    password_hash = db.Column(db.String(128))
    def __repr__(self):
        return '<User {}>'.format(self.uname)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_uid(self,uid):
        self.u_id = uid

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

class Hexdecodes(db.Model):
    __tablename__ = 'hexdecodes'
    h_entryid = db.Column(db.Integer,primary_key=True)
    hex = db.Column(db.String(80), unique=False, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ipaddress=db.Column(db.String(30), nullable=True)
    def __repr__(self):
        return '<Hex {}>'.format(self.hex)

class LoginForm(Form):
    """User Login Form."""
    username = StringField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None


class RegistrationForm(Form):

    uname = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


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

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    #user=None
    next_page = request.args.get('next')
    print(next_page is None)

    if not next_page or url_parse(next_page).netloc != '':
        next_page = 'index'
        print(next_page + ' line147 no next page specified so default index')

    if request.method== 'POST' and form.validate():
        # Login and validate the user.
        # user should be an instance of your `Userlogin` class
        if next_page is None:
            next_page = 'index'
        user = Userlogin.query.filter_by(uname=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('ERROR! Invalid login credentials')

        else:
            session['logged_in']=True
            flash('Logged in successfully.')
            login_user(user, remember=True)



            return redirect(url_for(next_page.strip('/')))


    print(next_page + ' line 146 - rendering template')
    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Userlogin(uname=form.uname.data, email=form.email.data)
        user.set_password(request.form.get("password"))
        s=[int(user.u_id) for user in Userlogin.query.all()]
        if len(s)>0:
            nextid=max(s)+1
        else:
            nextid=1
        user.set_uid(nextid)
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
    forms={'0000': SGB_g008(request.form),
           '0001': SGB_emergency(request.form),
           '0010': SGB_rls(request.form),
           '0011': SGB_national(request.form),
           '1111' : SGB_cancel(request.form)}
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
    print(ptype)

    if ptype == 'National User':
        hexcodelong = encodelongFGB(hexcodeUIN,  '')
        return redirect(url_for('decoded', hexcode=hexcodelong))

    if beacon.protocolflag()=='User':
        ptype = 'User'
    print(ptype)
    forms={'User': (FirstGenForm(request.form),'encodelongfirstentryform.html'),
           'Standard Location':(FirstGenStd(request.form),'encodelongfirstentryform.html'),
           'Standard Location Protocol - Test':(FirstGenStd(request.form),'encodelongfirstentryform.html'),
           'Standard Location Protocol - PLB (Serial)':(FirstGenStd(request.form),'encodelongfirstentryform.html'),
           'Standard Location Protocol - EPIRB (Serial)': (FirstGenStd(request.form), 'encodelongfirstentryform.html'),
           'Std Loc. Serial ELT - Aircraft Operator Designator Protocol': (FirstGenStd(request.form), 'encodelongfirstentryform.html'),
           'National Location':(FirstGenNatLoc(request.form),'encodelongNATLOC.html'),
           definitions.RLS_LOC :(FirstGenRLS(request.form),'encodelongfirstRLS.html'),
           definitions.ELT_DT_LOC:(FirstGenELTDT(request.form),'encodelongELTDT.html')}
    form = forms[ptype][0]

    renderform = forms[ptype][1]

    if request.method == 'POST' and form.validate():

        hexcodelong = encodelongFGB(hexcodeUIN, request.form)

        return redirect(url_for('decoded', hexcode=hexcodelong))

    return render_template(renderform, hexcode=hexcodeUIN, ptype=ptype, form=form, error=error,showmenu=MENU)

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

@app.route("/binary/<msg>")
def binary(msg):
    return jsonify(testbchSGB.scramble_msg(msg))

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
    #ipaddress=str(request.remote_addr)
    #ipaddress = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    ipaddress = str(request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr))
    #if ipaddress in ['199.199.172.43','199.162.159.113']:
    #    return 'Automated script detected - blocked'
    geocoord = (0, 0)
    locationcheck = False
    try:
        beacon = decodehex2.Beacon(hexcode)
        error=''
        if len(beacon.errors)>0 :
            error = ', '.join(beacon.errors)

        if beacon.type=='uin':
            if beacon.gentype=='first':
                tmp = 'encodelongfirst.html'
                # redirect with the hexcode, beacon type - different inputs depending on type of first gen change 3
            elif beacon.gentype=='second':
                tmp = 'encodelongsecond.html'
                print('sgb uin')
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
        hexsave=Hexdecodes(hex=hexcode,ipaddress=ipaddress)

        db.session.add(hexsave)
        db.session.commit()

        return render_template(tmp, hexcode=hexcode.upper(),
                               decoded=beacon.tablebin,
                               errors=beacon.errors,
                               warnings=beacon.warnings,
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
                               showmenu=MENU,
                               gmap_key=gmap_key)
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


def decoded_beacon(hexcode,fieldlst=[]):

    try:
        beacon = decodehex2.Beacon(hexcode)
        #res = db.get_item(Key={'id': 'counter'})
        #value = res['Item']['counter_value'] + 1
        #res = db.update_item(Key={'id': 'counter'}, UpdateExpression='set counter_value=:value',
        #                     ExpressionAttributeValues={':value': value}, )
        #hextable.put_item(Item={'entry_id': str(value), 'hexcode': hexcode, })
    except decodehex2.HexError as err:
        return {'error':[err.value, err.message]}
    if beacon.errors:
        has_errors=True
    else:
        has_errors=False

    decodedic={    'country':beacon.get_country()
                }


    dispatch = {'hexcode':hexcode,
                'has_errors':has_errors,
                'country': beacon.get_country(),
                'msgtype':beacon.type,
                'tac':beacon.gettac(),
                'lat':beacon.lat(),
                'long':beacon.long(),
                'beacontype':beacon.btype(),
                'first_or_second_gen':beacon.gentype,
                'errors' : beacon.errors,
                'mid':beacon.get_mid(),
                'cancellation': beacon.cancellation,
                'msg_note':beacon.genmsg,
                'loc_prot_fixed_bits':beacon.fbits(),
                'protocol_type':beacon.loctype(),
                'uin':beacon.hexuin(),
                'location':'{}, {}'.format(beacon.location[0], beacon.location[1]),
                'bch_match': beacon.bchmatch(),
                'bch_correct' : bch_check(hexcode),
                'bch_recompute' : bch_recalc(hexcode),
                'beacon_id' : beacon.get_id(),
                'vessel_id' : beacon.get_id(),
                'beacon_sn' : beacon.get_sn(),
                '3ld' : beacon.threeletter,
                'threeLD' : beacon.threeletter,
                'altitude': beacon.beacon.altitude,
                'bch1_binarycalc':bch1_binarycalc(hexcode),
                'bch2_binarycalc':bch2_binarycalc(hexcode),
                'kitchen_sink': beacon.tablebin
            }
    for fld in fieldlst:
        if dispatch.__contains__(fld):
            decodedic[fld]=dispatch[fld]
        else:
            decodedic[fld] = '{} does not exist'.format(fld)

    return decodedic


@app.route('/json', methods=['PUT'])
def jsonhex2():
    #start = timeit.timeit()
    decodelst=[]
    decodedic = {}
    item={}
    fieldlst= []
    req_data = request.get_json()
    if type(req_data)== list:
        hexcode = req_data
    elif type(req_data) == dict:
        try:
            hexcode = req_data['hexcode']
        except KeyError:
            return jsonify(error=['bad json header request', 'hexcode key not found'])
        try:
            fieldlst= req_data['decode_flds']
            if type(fieldlst)==str:
                fieldlst =[req_data['decode_flds']]

        except KeyError:
            pass

    else:
        return jsonify(error=['bad json header request','hexcode key not found'])

    if type(hexcode)==str:
        item=decoded_beacon(hexcode,fieldlst)
        item['inputmessage']=hexcode
        decodelst.append(item)


    elif type(hexcode)==list:
        i=0
        for h in hexcode:
            item={}

            i+=1

            try:
                item = decoded_beacon(h, fieldlst)
                item['inputmessage'] = h



            except TypeError:
                item = decoded_beacon(str(h), fieldlst)
                item['inputmessage'] = str(h)

            except KeyError:
                item={}
                item['error'] = 'bad hexcode key'
                item['inputmessage'] = h


            decodelst.append(item)

    #end = timeit.timeit()
    #decodelst.append({'seconds': str(end - start)})
    #print(end,start,str(end - start))
    return jsonify(decodelst)



# Listen for GET requests to yourdomain.com/account/
@app.route("/account")
@login_required
def account():
    user = Userlogin.query.filter_by(uname='craig').first()
    if user is not None:
        return render_template('account.html')
    else:
        return redirect(url_for('decode'))


# Listen for POST requests to yourdomain.com/submit_form/
@app.route("/submit-form/", methods = ["POST"])
def submit_form():
  # Collect the data posted from the HTML form in account.html:
  username = request.form["username"]
  full_name = request.form["full-name"]


  # Provide some procedure for storing the new details
  #update_account(username, full_name, avatar_url)

  # Redirect to the user's profile page, if appropriate
  return redirect(url_for('decode')) #redirect(url_for('profile'))


# Listen for GET requests to yourdomain.com/sign_s3/
#
# Please see https://gist.github.com/RyanBalfanz/f07d827a4818fda0db81 for an example using
# Python 3 for this view.
@app.route('/sign-s3/')
def sign_s3():
  # Load necessary information into the application
  S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

  # Load required data from the request
  file_name = '{}{}'.format(uuid.uuid4(),request.args.get('file-name'))
  file_type = request.args.get('file-type')

  # Initialise the S3 client
  s3 = boto3.client('s3')

  # Generate and return the presigned URL
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = { "Content-Type": file_type},
    Conditions = [
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )

  # Return the data to the client
  return json.dumps({
    'data': presigned_post,
    'filename': file_name,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  })



@app.route('/sign-s3-target/')
@login_required
def sign_s3_target():
  # Load necessary information into the application
  S3_BUCKET_TARGET = os.environ.get('S3_BUCKET_TARGET')

  # Load required data from the request
  file_name = request.args.get('file-name')

  # Initialise the S3 client
  s3 = boto3.client('s3')

  # Generate and return the presigned URL
  presigned = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': S3_BUCKET_TARGET,
                                                            'Key': file_name},
                                                    ExpiresIn=3600)
  # Return the data to the client
  return json.dumps(presigned)


@app.route('/exists/')
def exists():
    S3_BUCKET_TARGET = os.environ.get('S3_BUCKET_TARGET')
    file_name = request.args.get('file-name')
    s3 = boto3.client('s3')
    try:
        response= s3.head_object(Bucket=S3_BUCKET_TARGET, Key=file_name)
        response = jsonify( True)
    except ClientError:
        response = jsonify( False)

    return response


if __name__ == "__main__":
    app.secret_key = 'my secret'
    app.run(debug=True,host='0.0.0.0', port=5555, threaded=True)
