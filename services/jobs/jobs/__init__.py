"""The jobs package is a :py:mod:`nameko` microservice which manages processing.

To run this microservice it needs to connect to a message broker (`RabbitMQ`_), relational database (`PostgreSQL`_) and
also the :mod:`~files` and :mod:`~processes` service is required. Additionally the complete Airflow-Celery setup must
be running - including webserver, scheduler, `PostgreSQL`_ and `Celery`_ workers.

Make sure all volumes are set correctly.

Also a set of configuration settings needs to be provided. Settings are excepted to be made available as
environment variables. All environment variables need to be prefixed with ``OEO_`` (short hand for OpenEO). The full list
of required environment variables can be found in :py:class:`~jobs.dependencies.settings.SettingKeys`. It should
be mentioned that NO defaults are defined.

Besides this similar considerations apply as for the :mod:`~capabilities`.

.. _RabbitMQ: https://www.rabbitmq.com/
.. _PostgreSQL: https://www.postgresql.org/
.. _Celery: https://docs.celeryproject.org/en/stable/index.html
"""
