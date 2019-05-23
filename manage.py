from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand







app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
app.secret_key = 'my secret'
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)





class Userlogin(db.Model):
    __tablename__ = 'userlogin'
    u_id = db.Column(db.Integer,primary_key=True)
    uname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.uname)

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





if __name__ == '__main__':
    manager.run()