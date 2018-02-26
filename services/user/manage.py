''' Manager for EODC User Service '''

from unittest import TestLoader, TextTestRunner
from flask_script import Manager
from flask_migrate import MigrateCommand
from service import create_service, DB
from service.model.user import User
from flask import current_app

SERVICE = create_service()
MANAGER = Manager(SERVICE)
MANAGER.add_command('db', MigrateCommand)

@MANAGER.command
def test():
    ''' Runs Unit tests. '''

    tests = TestLoader().discover('service/tests', pattern='test*.py')
    result = TextTestRunner(verbosity=2).run(tests)
    
    if result.wasSuccessful():
        return 0
    return 1

@MANAGER.command
def recreate_db():
    ''' Recreates the database. '''

    DB.drop_all()
    DB.create_all()
    DB.session.commit()

    print("Recreated Database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

@MANAGER.command
def seed_db():
    ''' Seeds the database. '''

    DB.session.add(User(
        username='user',
        email='user@eodc.eu',
        password='eodcUser#1'
    ))

    DB.session.add(User(
        username='admin',
        email='admin@eodc.eu',
        password='eodcAdmin#1',
        admin=True
    ))

    DB.session.commit()

    print("Added users 'admin' and 'user' to database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

@MANAGER.command
def drop_db():
    ''' Drop the database '''

    DB.drop_all()

    print("Dropped database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

if __name__ == '__main__':
    MANAGER.run()
