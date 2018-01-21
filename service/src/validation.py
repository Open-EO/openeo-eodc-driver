''' Payload validation for EODC Job Service '''

class ValidationException(Exception):
    ''' Validation Exception raises if payload is not valid. '''
    pass

def validate_payload(payload):
    ''' Checks if input playload is valid and executable '''
    # TODO: Check if values are properly declared
    # TODO: Further Validation Checks

    # Check if payload is available
    if not payload:
        raise ValidationException("Invalid payload.")

    # Check if process_graph is available
    if "process_graph" not in payload:
        raise ValidationException("Process Graph Node is missing.")
    process_graph = payload.get("process_graph")

    return process_graph
