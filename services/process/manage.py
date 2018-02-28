''' Manager for Process Service '''

from unittest import TestLoader, TextTestRunner
from flask_script import Manager
from flask_migrate import MigrateCommand
from service import create_service, DB
from service.model.process import Process
from flask import current_app

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
    ''' Seed the database '''

    DB.session.add(
        Process(
            user_id=1,
            process_id="min_time",
            description="Finds the minimum value of time series for all bands of the input dataset.",
            git_uri="git@git.eodc.eu:eodc-processes/min-time.git",
            git_ref="master",
            process_type="operation",
            args={
                "collections": {
                    "description": "array of input collections with one element",
                    "type": "array",
                    "required": True
                }
            }
        )
    )

    DB.session.commit()

    print("Added process 'min_time' to database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

@MANAGER.command
def drop_db():
    ''' Drop the database '''
    
    DB.drop_all()

    print("Dropped database with URI: {0}"\
          .format(current_app.config["SQLALCHEMY_DATABASE_URI"]))

if __name__ == "__main__":
    MANAGER.run()
