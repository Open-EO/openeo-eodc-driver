from flask_script import Manager, Command, Option
from unittest import TestLoader, TextTestRunner
from gateway import gateway

manager = Manager(gateway.get_service())

@manager.option('-h', '--host', dest='host', default='127.0.0.1')
@manager.option('-p', '--port', dest='port', type=int, default=3000)
@manager.option('-w', '--workers', dest='workers', type=int, default=3)
def gunicorn(host, port, workers):
    """Start the Server with Gunicorn"""
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(host, port),
                'workers': workers
            }

        def load(self):
            return gateway.get_service()

    application = FlaskApplication()
    return application.run()

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
