"""The users package is a `nameko`_ microservice which manages users.

To run this microservice it only  needs to connect to a message broker (`RabbitMQ`_) and relational database
(`PostgreSQL`_).

Also a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with ``OEO_`` (short hand for OpenEO). The full
list of required environment variables can be found in :py:class:`~users.dependencies.settings.SettingKeys`. It
should be mentioned that NO defaults are defined.

Besides this similar considerations apply as for the :mod:`~capabilities`.

.. _RabbitMQ: https://www.rabbitmq.com/
.. _PostgreSQL: https://www.postgresql.org/
.. _nameko: https://nameko.readthedocs.io/en/stable/
"""
