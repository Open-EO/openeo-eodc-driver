""" Models """
# TODO: Further normalize models

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, TEXT, DateTime, JSON, Boolean, Enum, Float, CheckConstraint, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

data_type_enum = Enum(
    'array',
    'boolean',
    'integer',
    'null',
    'number',
    'object',
    'string',
    name='data_type',
)


class ProcessGraph(Base):
    """ Base model for a process graph. """

    __tablename__ = 'process_graph'

    # Defined by user? how to set different one / add hash
    id = Column(Integer, primary_key=True)
    openeo_id = Column(String, unique=True)
    user_id = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    description = Column(TEXT, nullable=True)
    deprecated = Column(Boolean, default=False, nullable=True)
    experimental = Column(Boolean, default=False, nullable=True)
    process_graph = Column(JSON, default={})  # TODO also store as separate table!
    examples = Column(JSON, nullable=True)  # check either process_graph or argument is set TODO store as separate table
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    categories = relationship('Category', cascade='all, delete, delete-orphan')
    parameters = relationship('Parameter', foreign_keys='Parameter.process_graph_id', cascade='all, delete, delete-orphan')
    returns = relationship('Return', uselist=False, cascade='all, delete, delete-orphan')
    exceptions = relationship('ExceptionCode', cascade='all, delete, delete-orphan')
    links = relationship('Link', cascade='all, delete, delete-orphan')


class Parameter(Base):

    __tablename__ = 'parameter'

    id = Column(Integer, primary_key=True)
    process_graph_id = Column(Integer, ForeignKey('process_graph.id'), nullable=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=True)
    name = Column(String, nullable=False)
    description = Column(TEXT, nullable=False)
    optional = Column(Boolean, default=False, nullable=True)
    deprecated = Column(Boolean, default=False, nullable=True)
    experimental = Column(Boolean, default=False, nullable=True)
    default = Column(TEXT, nullable=True)  # could be any type - create separate column to store type?

    # can also be a List or a single one
    schemas = relationship('Schema', foreign_keys='Schema.parameter_id', cascade='all, delete, delete-orphan')


class Return(Base):

    __tablename__ = 'return'

    id = Column(Integer, primary_key=True)
    process_graph_id = Column(Integer, ForeignKey('process_graph.id'), nullable=False)
    description = Column(TEXT, nullable=True)

    # can also be a single one
    schemas = relationship('Schema', foreign_keys='Schema.return_id', cascade='all, delete, delete-orphan')


class Category(Base):

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    process_graph_id = Column(Integer, ForeignKey('process_graph.id'))
    name = Column(String, nullable=False)


class Schema(Base):

    __tablename__ = 'schema'

    id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey('parameter.id'), nullable=True)
    return_id = Column(Integer, ForeignKey('return.id'), nullable=True)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=True)
    subtype = Column(String, nullable=True)
    pattern = Column(String, nullable=True)
    minimum = Column(Float, nullable=True)
    maximum = Column(Float, nullable=True)
    min_items = Column(Float, default=0, nullable=True)
    max_items = Column(Float, nullable=True)

    types = relationship('SchemaType', cascade='all, delete, delete-orphan')  # can also be a single one
    enums = relationship('SchemaEnum', cascade='all, delete, delete-orphan')
    parameters = relationship('Parameter', foreign_keys='Parameter.schema_id', cascade='all, delete, delete-orphan')
    items = relationship('Schema', foreign_keys='Schema.schema_id', cascade='all, delete, delete-orphan')  # can also be a single one

    __table_args__ = (
        CheckConstraint(min_items >= 0, name='check_min_items_positive'),
        CheckConstraint(max_items >= 0, name='check_max_items_positive'),
        {})


class SchemaType(Base):

    __tablename__ = 'schema_type'

    id = Column(Integer, primary_key=True)
    schema_id = Column(Integer, ForeignKey('schema.id'))
    name = Column(data_type_enum, nullable=False)


class SchemaEnum(Base):

    __tablename__ = 'schema_enum'

    id = Column(Integer, primary_key=True, default='se-' + str(uuid4()))
    schema_id = Column(Integer, ForeignKey('schema.id'))
    name = Column(TEXT, nullable=False)


class ExceptionCode(Base):

    __tablename__ = 'exception'

    id = Column(Integer, primary_key=True)
    process_graph_id = Column(Integer, ForeignKey('process_graph.id'))
    description = Column(TEXT, nullable=True)
    message = Column(TEXT, nullable=False)
    http = Column(Integer, default=400)
    error_code = Column(Integer, nullable=False)


class Link(Base):

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)
    process_graph_id = Column(Integer, ForeignKey('process_graph.id'))
    rel = Column(String, nullable=False)
    href = Column(String, nullable=False)  # should be uri!
    type = Column(String, nullable=True)
    title = Column(String, nullable=True)
