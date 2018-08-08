from flask_script import Manager
from unittest import TestLoader, TextTestRunner
from gateway import gateway

manager = Manager(gateway.get_service())

@manager.command
def test():
    ''' Runs Unit tests. '''

    tests = TestLoader().discover('tests', pattern='test*.py')
    result = TextTestRunner(verbosity=2).run(tests)
    
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
