"""The capabilities package is a :py:mod:`nameko` microservice which describes available capabilities.

To run this microservice it needs to connect to a message broker - RabbitMQ is used here. Besides this server no other
components are required for a minimal setup - the service neither connects to an other microservices nor uses a
database.

But a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with `OEO_` (short hand for OpenEO). The full list
of required environment variables can be found in :py:class:`~capabilities.dependencies.settings.SettingKeys`. It should
be mentioned that NO defaults are defined.

In general settings are validated on start up. Appropriate errors will be raise if settings are missing. Please consider
that some settings are used BEFORE validation can take place - e.g. connection to RabbitMQ - in this case a missing
setting can raise a connection error not validation error.

This package can be run in docker using the provided Dockerfile. The Dockerfile only prepares a Debian based container
and installs requirements. It does not copy the code, handle environment variables, nor handle volume mounts. This needs
to be done separately. The root folder of the OpenEO-EODC-Driver provides a docker-compose.yml file which does all that
for all microservices, their databases, the RabbitMQ and the gateway.
"""
