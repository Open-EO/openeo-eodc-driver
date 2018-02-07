''' Exceptions of the EODC Template Engine '''

class TemplateException(Exception):
    ''' Template Exception raises if the template could not be parsed or excecuted. '''
    pass

class ValidationException(Exception):
    ''' Deploy Exception raised if Deployment could not be completed. '''
    pass

class BuildException(Exception):
    ''' Build Exception raised if Build could not be completed. '''
    pass

class DeployException(Exception):
    ''' Deploy Exception raised if Deployment could not be completed. '''
    pass
