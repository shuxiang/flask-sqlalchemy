#coding=utf8

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager, Shell

from sa_test import app, db

print db.Model._metadata
print db.Model._metadata['b1'].tables
print db.get_metadata('b1')
db.init_app(app)
print db.get_metadata('b1')
print '---------------------------'

manager = Manager(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)





if __name__ == "__main__":
    manager.run()


"""
https://flask-migrate.readthedocs.io/en/latest/

flask db init --multidb

cp env.py ./migrations/

flask db migrate

flask db upgrade
"""