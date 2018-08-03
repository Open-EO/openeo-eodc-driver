""" /jobs """

from flask_restful_swagger_2 import Resource, swagger, Schema #TODO: Delete?
from flask_restful.reqparse import RequestParser
from flask_restful.utils import cors
from flask import send_from_directory
from os import path, listdir

from . import rpc
from .src.auth import auth
from .src.response import *
from .src.request import ModelRequestParser
from .src.cors import CORS
from .src.parameters import job_body, job_id
from .src.models import process_graph, output, job_val


class JobsApi(Resource):
    __res_parser = ResponseParser()
    __req_parser = ModelRequestParser(job_val)

    @cors.crossdomain(
        origin=["*"],
        methods=["POST"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__())
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["POST"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth(admin=True)
    @swagger.doc({
        "tags": ["Job Management"],
        "description": (
            "Creates a new job from one or more (chained) processes "
            "at the back-end. Jobs are initially always lazy jobs and "
            "will not run the computations until on demand  requests or "
            "separately queueing it. Queueing it converts a lazy job to "
            "a batch job.."),
        "parameters": [job_body],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("Details of the created job.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def post(self, user_id):
        try:
            args = self.__req_parser.parse_args()
            rpc_response = rpc.jobs.create_job(user_id, args["process_graph"],  args["output"])

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)


class JobDetailApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__([job_id]))
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["Job Management"],
        "description": "Returns detailed information about a submitted job including its current status and the underlying process graph.",
        "parameters": [job_id],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("Full job information.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "404": NotFound().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id, job_id):
        try:
            rpc_response = rpc.jobs.get_job(user_id, job_id)

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)

class BatchJobApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["PATCH"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__([job_id]))
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["PATCH"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["Job Management"],
        "description": "This request converts a job into a batch job and queues it for execution. A paused job can be resumed with this request.",
        "parameters": [job_id],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("The job has been successfully queued.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "404": NotFound().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def patch(self, user_id, job_id):
        try:
            rpc.jobs.process_job.call_async(job_id)
            return self.__res_parser.string(200, "The job has been successfully queued.")
        except Exception as exc:
            return self.__res_parser.error(exc)


class DownloadApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__([job_id]))
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["Result Access"],
        "description": "This request will provide links to download results of batch jobs. Depending on the Content-Type header, the response is either a simple JSON array with URLs as strings or a metalink XML document.",
        "parameters": [job_id],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("Valid download links have been returned. The download links doesn’t necessarily need to be located under the API base url.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "404": NotFound().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id, job_id):
        try:
            # rpc_response = rpc.jobs.get_job(user_id, job_id)
            # if rpc_response["status"] == "error":
            #     raise self.__res_parser.map_exceptions(rpc_response["exc_key"])

            job_directory = "c:/job_results/{0}".format(54)
            files_in_dir = listdir(job_directory)

            output = []
            for file_name in files_in_dir:
                output.append("http://127.0.0.1:3000/download/{0}/{1}".format(job_id, file_name))

            return self.__res_parser.data(200, output)
        except Exception as exc:
            return self.__res_parser.error(exc)


class DownloadFileApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    # @auth()
    def get(self, job_id, file_name):
        try:
            job_directory = "c:/job_results/{0}".format(54)
            return send_from_directory(directory=job_directory, filename=file_name)
        except Exception as exc:
            return self.__res_parser.error(exc)