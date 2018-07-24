from flask_script import Manager
from unittest import TestLoader, TextTestRunner
from gateway import create_gateway

GATEWAY = create_gateway()
MANAGER = Manager(GATEWAY)

@MANAGER.command
def test():
    ''' Runs Unit tests. '''

    tests = TestLoader().discover('tests', pattern='test*.py')
    result = TextTestRunner(verbosity=2).run(tests)
    
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    MANAGER.run()
