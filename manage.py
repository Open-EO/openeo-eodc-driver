''' Manager for EODC Job Service '''

from unittest import TestLoader, TextTestRunner
from flask_script import Manager
from service import create_service

SERVICE = create_service()
MANAGER = Manager(SERVICE)

@MANAGER.command
def test():
    ''' Runs unit tests. '''

    tests = TestLoader().discover("service/tests", pattern="test*.py")
    result = TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    MANAGER.run()
