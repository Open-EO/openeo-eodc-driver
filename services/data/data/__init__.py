"""The data package is a :py:mod:`nameko` microservice which describes available EO data.

To run this microservice it needs to connect to a message broker - RabbitMQ is used here. Besides this server no other
components are required for a minimal setup - the service neither connects to an other microservices nor uses a
database but it uses a set of dependencies.

Also a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with `OEO_` (short hand for OpenEO). The full list
of required environment variables can be found in :py:class:`~data.dependencies.settings.SettingKeys`. It should
be mentioned that NO defaults are defined.

Besides this similar considerations apply as for the :mod:`~capabilities`.
"""
