import random, string

class Job:
    def __init__(self, job_name, kind, image, status="Created"):
        self.job_name = job_name
        self.job_id = job_name + "_" + "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        self.kind = kind
        self.image = image
        self.status = status
        self.results = None

    def __str__(self):
        return self.job_id
