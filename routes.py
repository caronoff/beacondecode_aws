
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
