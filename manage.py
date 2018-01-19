''' Manager for Jobs Service '''

import unittest
from flask_script import Manager
from flask_migrate import MigrateCommand

from service import create_app, db
from service.model.job import Job


app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    ''' Runs unit tests. '''

    tests = unittest.TestLoader().discover("service/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1

@manager.command
def drop_db():
    ''' Drop database '''

    db.drop_all()

@manager.command
def recreate_db():
    ''' Recreates a database. '''

    db.drop_all()
    db.create_all()
    db.session.commit()

@manager.command
def seed_db():
    ''' Seeds the database. '''

    db.session.add(Job(1, {}))
    db.session.commit()

if __name__ == "__main__":
    manager.run()
