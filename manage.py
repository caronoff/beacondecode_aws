import os
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








if __name__ == '__main__':
    manager.run()