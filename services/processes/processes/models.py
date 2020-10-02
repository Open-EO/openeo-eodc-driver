"""This domain module provides the database model for the processes database.

This includes all required table definitions and auxiliary data structures.
"""

import enum
from datetime import datetime
from typing import Any, Tuple

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String,\
    TEXT, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: Any = declarative_base()

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


class ProcessDefinitionEnum(enum.Enum):
    """Enum providing possible types of processes - predefined / user_defined."""

    predefined = 'predefined'
    user_defined = 'user_defined'


process_definition_enum = Enum(
    ProcessDefinitionEnum,
    name='process_definition',
)


class ProcessGraph(Base):
    """Base model for a process graph."""

    __tablename__ = 'process_graphs'

    id = Column(String, primary_key=True)  # noqa A003
    """Unique string identifier of a process_graph."""
    id_openeo = Column(String, nullable=False)
    """String identifier used by the user.

    Two users can both store a process graph using the same id_openeo. e.g. 'ndvi'.
    """
    process_definition = Column(process_definition_enum, nullable=False)
    """:class:`~processes.models.ProcessDefinitionEnum` whether this is a predefined or user-defined process graph."""
    user_id = Column(String, nullable=True)
    """The user's identifier (string) owning the process graph."""
    summary = Column(String, nullable=True)
    """A short summary of what the process does (optional)."""
    description = Column(TEXT, nullable=True)
    """Detailed description to explain the entity (optional)."""
    deprecated = Column(Boolean, default=False, nullable=True)
    """Whether the process graph is deprecated (False)."""
    experimental = Column(Boolean, default=False, nullable=True)
    """Whether the process graph is experimental (False)."""
    process_graph = Column(JSON, default={})  # TODO also store as separate table!
    """The complete process graph stored as JSON ({})."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    """UTC datetime the job was created (current UTC datetime)."""
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    """UTC datetime any column of this job was last updated (current UTC datetime)."""

    categories = relationship('Category', cascade='all, delete, delete-orphan')
    """A list of categories of type :py:class:`~processes.models.Category`."""
    parameters = relationship('Parameter', foreign_keys='Parameter.process_graph_id',
                              cascade='all, delete, delete-orphan')
    """A list of :py:class:`~processes.models.Parameter`."""
    returns = relationship('Return', uselist=False, cascade='all, delete, delete-orphan')
    """The data that is returned from this process as :py:class:`~processes.models.Return`."""
    exceptions = relationship('ExceptionCode', cascade='all, delete, delete-orphan')
    """A dictionary of :py:class:`~processes.models.Exception` that might occur while processing."""
    links = relationship('Link', cascade='all, delete, delete-orphan')
    """A list of :py:class:`~processes.models.Link` related to this process."""
    examples = relationship('Example', cascade='all, delete, delete-orphan')
    """A list of :py:class:`~processes.models.Example`."""

    UniqueConstraint('id_openeo', 'user_id', name='uq_process_graph_user_id')


class Example(Base):
    """Model storing examples."""

    __tablename__ = 'example'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the example."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    arguments = Column(JSON, nullable=False)
    """Arguments used for the process in JSON format."""
    title = Column(String, nullable=True)
    """A title for the example (optional)."""
    description = Column(String, nullable=True)
    """Detailed description to explain the example (optional)."""
    returns = Column(String, nullable=True)
    """The return value as string (optional)."""
    return_type = Column(String, nullable=True)
    """The return type to later convert the return value back to the original type (optional)."""


class Parameter(Base):
    """Model storing parameter descriptions."""

    __tablename__ = 'parameter'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the parameter."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    schema_id = Column(Integer, ForeignKey('schema.id'))
    """The id of the schema (ForeignKey) associated to the parameter."""
    name = Column(String, nullable=False)
    """A name for the parameter."""
    description = Column(TEXT, nullable=False)
    """Detailed description to explain the entity."""
    optional = Column(Boolean, default=False, nullable=True)
    """Determines whether this parameter is optional to be specified even when no default is given (False)."""
    deprecated = Column(Boolean, default=False, nullable=True)
    """Specifies that the parameter is deprecated - can be removed in a next versions (False)."""
    experimental = Column(Boolean, default=False, nullable=True)
    """Declares the parameter to be experimental - can change / may produce unpredictable behaviour (False)."""
    default = Column(TEXT, nullable=True)
    """The default value for this parameter as string (optional)."""
    default_type = Column(String, nullable=True)
    """The data type of the default value to later convert the default value back to the original type (optional)."""

    schemas = relationship('Schema', foreign_keys='Schema.parameter_id', cascade='all, delete, delete-orphan')
    """A list of data types :py:class:`~processes.models.Schema`."""


class Return(Base):
    """Model storing the return entity."""

    __tablename__ = 'return'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the return entity."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    description = Column(TEXT, nullable=True)
    """Detailed description to explain the entity (optional)."""

    schemas = relationship('Schema', foreign_keys='Schema.return_id', cascade='all, delete, delete-orphan')
    """A list of data types :py:class:`~processes.models.Schema`."""


class Category(Base):
    """Model to map a list of categories to a single process graph."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the category."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    name = Column(String, nullable=False)
    """The name of the category."""


class Schema(Base):
    """Model describing a data type."""

    __tablename__ = 'schema'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the schema."""
    parameter_id = Column(Integer, ForeignKey('parameter.id'), nullable=True)
    """The id of the corresponding parameter (ForeignKey) - (optional)."""
    return_id = Column(Integer, ForeignKey('return.id'), nullable=True)
    """The id of the corresponding return entity (ForeignKey) - (optional)."""
    subtype = Column(String, nullable=True)
    """The allowed sub data type for a value (optional)."""
    pattern = Column(String, nullable=True)
    """The regular expression a string value must match against (optional)."""
    minimum = Column(Float, nullable=True)
    """The minimum value (inclusive) allowed for a numerical value (optional)."""
    maximum = Column(Float, nullable=True)
    """The maximum value (inclusive) allowed for a numerical value (optional)."""
    min_items = Column(Float, default=0, nullable=True)
    """The minimum number of items required in an array (0 - optional)."""
    max_items = Column(Float, nullable=True)
    """The maximum number of items required in an array (optional)."""
    items = Column(JSON, nullable=True)
    """Specifies schemas for the items in an array as JSON (optional)."""
    additional = Column(JSON, nullable=True)
    """Any additional properties as JSON (optional)."""

    types = relationship('SchemaType', cascade='all, delete, delete-orphan')
    """A list of allowed :py:class:`~processes.models.SchemaType` (optional)."""
    enums = relationship('SchemaEnum', cascade='all, delete, delete-orphan')
    """A list of allowed values :py:class:`~processes.models.SchemaEnum` (optional)."""
    parameters = relationship('Parameter', foreign_keys='Parameter.schema_id', cascade='all, delete, delete-orphan')
    """A list of corresponding :py:class:`~processes.models.Parameter` (optional)."""

    __table_args__: Tuple = (
        CheckConstraint(min_items >= 0, name='check_min_items_positive'),
        CheckConstraint(max_items >= 0, name='check_max_items_positive'),
        {})


class SchemaType(Base):
    """Model of the allowed basic data type(s) for a value."""

    __tablename__ = 'schema_type'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the schema type."""
    schema_id = Column(Integer, ForeignKey('schema.id'))
    """The id of the corresponding schema (ForeignKey)."""
    name = Column(data_type_enum, nullable=False)
    """The name of the schema type - actual value."""


class SchemaEnum(Base):
    """Model storing an exclusive list of allowed values of schema enums."""

    __tablename__ = 'schema_enum'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the schema enum."""
    schema_id = Column(Integer, ForeignKey('schema.id'))
    """The id of the corresponding schema (ForeignKey)."""
    name = Column(TEXT, nullable=False)
    """The name of the schema enum - actual value."""


class ExceptionCode(Base):
    """Model storing exceptions."""

    __tablename__ = 'exception'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the exception."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    description = Column(TEXT, nullable=True)
    """Detailed description to explain the error to client users and back-end developers (optional).

    This should not be shown in the clients directly.
    """
    message = Column(TEXT, nullable=False)
    """Explains the reason the server is rejecting the request.

    This message is intended to be displayed to the client user.
    """
    http = Column(Integer, default=400)
    """HTTP Status Code (400)."""
    error_code = Column(String, nullable=False)
    """Defined error code as descriptive string."""


class Link(Base):
    """Model storing a link."""

    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)  # noqa A003
    """A unique integer identifier of the link."""
    process_graph_id = Column(String, ForeignKey('process_graphs.id'))
    """The id of the corresponding process graph (ForeignKey)."""
    rel = Column(String, nullable=False)
    """Relationship between the current document and the linked document."""
    href = Column(String, nullable=False)  # should be uri!
    """A valid URL."""
    type = Column(String, nullable=True)  # noqa A003
    """A string that hints at the format used to represent data at the provided URI (optional)."""
    title = Column(String, nullable=True)
    """Used as a human-readable label for a link (optional)."""
