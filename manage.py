import os
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy





from __init__ import db
from __init__ import app
#try:
#    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#except KeyError:
#    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Elephant$2017@localhost/beacon'


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)








if __name__ == '__main__':
    manager.run()