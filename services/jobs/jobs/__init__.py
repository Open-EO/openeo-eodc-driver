"""The jobs package is a :py:mod:`nameko` microservice which manages processing.

To run this microservice it needs to connect to a message broker (`RabbitMQ`_), relational database (`PostgreSQL`_) and
also the :mod:files service is required.
persistent file storage needs to be mounted to the service to manage user files. In case the whole
EODC-OpenEO-Driver setup is used this file storage also needs to be available to the gateway service. Besides this the
service does not directly connect to another microservice and also does not need a database.

Also a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with ``OEO_`` (short hand for OpenEO). The full list
of required environment variables can be found in :py:class:`~jobs.dependencies.settings.SettingKeys`. It should
be mentioned that NO defaults are defined.

Besides this similar considerations apply as for the :mod:`~capabilities`.

.. _RabbitMQ: https://www.rabbitmq.com/
.. _PostgreSQL: https://www.postgresql.org/
"""
