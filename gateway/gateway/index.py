''' / '''

from flask import redirect
from flask_restful import Resource

class Index(Resource):
    def get(self):
        return redirect("/capabilities")
