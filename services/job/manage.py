''' Manager for Job Service '''

from unittest import TestLoader, TextTestRunner
from flask import current_app
from flask_script import Manager
from flask_migrate import MigrateCommand
from service import create_service, DB
from service.model.job import Job

SERVICE = create_service()
MANAGER = Manager(SERVICE)
MANAGER.add_command('db', MigrateCommand)

@MANAGER.command
def test():
    ''' Runs Unit Tests '''

    tests = TestLoader().discover("service/tests", pattern="test*.py")
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

    DB.session.add(Job(
        user_id='1',
        task={}
    ))

    DB.session.commit()

    print("Added job to database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

@MANAGER.command
def drop_db():
    ''' Drop the database '''
    
    DB.drop_all()

    print("Dropped database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

if __name__ == "__main__":
    MANAGER.run()
