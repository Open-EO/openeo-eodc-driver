#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='openeo-service-data',
    version='0.0.1',
    description='Data Service for openEO',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'nameko==2.8.5',
        'nameko-sqlalchemy==1.3.0',
        'alembic==0.9.9',
        'marshmallow==3.0.0b8',
        'psycopg2==2.7.4',
    ],
    extras_require={
        'dev': [
            'pytest==3.1.1',
            'coverage==4.4.1',
            'flake8==3.3.0'
        ],
    },
    zip_safe=True
)