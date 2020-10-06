"""The users package is a :py:mod:`nameko` microservice which manages users.

To run this microservice it only  needs to connect to a message broker (`RabbitMQ`_) and relational database
(`PostgreSQL`_).

Also a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with ``OEO_`` (short hand for OpenEO).

Besides this similar considerations apply as for the :mod:`~capabilities`.

.. _RabbitMQ: https://www.rabbitmq.com/
.. _PostgreSQL: https://www.postgresql.org/
"""
