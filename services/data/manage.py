''' Manager for Data Service '''

from unittest import TestLoader, TextTestRunner
from service import create_service
from flask_script import Manager

SERVICE = create_service()
MANAGER = Manager(SERVICE)

@MANAGER.command
def test():
    ''' Run Unit Tests '''

    tests = TestLoader().discover("service/tests", pattern="test*.py")
    result = TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    MANAGER.run()
