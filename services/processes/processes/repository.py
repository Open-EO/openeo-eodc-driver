from collections import Callable

from .models import ProcessGraph, Parameter, Return, Category, Base, Schema, SchemaType, SchemaEnum, ExceptionCode, \
    Link, ProcessDefinitionEnum


def construct_process_graph(user_id: str, process_graph_json: dict, process_definition: ProcessDefinitionEnum) -> ProcessGraph:

    db_process_graph = ProcessGraph(
        openeo_id=process_graph_json.get('id'),
        user_id=user_id,
        process_definition=process_definition,
        summary=process_graph_json.get('summary'),
        description=process_graph_json.get('description'),
        deprecated=process_graph_json.get('deprecated', False),
        experimental=process_graph_json.get('experimental', False),
        process_graph=process_graph_json.get('process_graph'),
        examples=process_graph_json.get('examples', None),
    )

    if 'parameters' in process_graph_json:
        for param in process_graph_json['parameters']:
            db_process_graph = add_parameter(db_process_graph, param)

    if 'categories' in process_graph_json:
        for category in process_graph_json['categories']:
            db_process_graph = add_category(db_process_graph, category)

    if 'returns' in process_graph_json:
        db_process_graph = add_return(db_process_graph, process_graph_json['returns'])

    if 'exceptions' in process_graph_json:
        for error_code, exception in process_graph_json['exceptions'].items():
            exception['error_code'] = error_code
            db_process_graph = add_exception(db_process_graph, exception)

    if 'links' in process_graph_json:
        for link in process_graph_json['links']:
            db_process_graph = add_link(db_process_graph, link)

    return db_process_graph


def add_single_or_multiple(item_name: str, dict_: dict, add_func: Callable, parent: Base):
    if item_name in dict_:
        item = dict_[item_name]
        if isinstance(item, list):
            for sub in item:
                parent = add_func(parent, sub)
        else:
            parent = add_func(parent, dict_[item_name])
    return parent


def add_category(parent: Base, category: str):
    parent.categories.append(Category(
        name=category,
    ))
    return parent


def add_schema_type(parent: Base, schema_type: str):
    parent.types.append(SchemaType(
        name=schema_type,
    ))
    return parent


def add_enum(parent: Base, enum: str):
    parent.enums.append(SchemaEnum(
        name=enum,
    ))
    return parent


def add_schema(parent: Base, schema: dict):
    db_schema = Schema(
        subtype=schema.get('subtype', None),
        pattern=schema.get('pattern', None),
        minimum=schema.get('minimum', None),
        maximum=schema.get('maximum', None),
        min_items=schema.get('min_items', 0),
        max_items=schema.get('max_items', None)
    )
    if 'enum' in schema:
        for enum in schema['enum']:
            db_schema = add_enum(db_schema, enum)
    if 'parameters' in schema:
        for param in schema['parameters']:
            db_schema = add_parameter(db_schema, param)
    if 'type' in schema:
        db_schema = add_single_or_multiple('type', schema, add_schema_type, db_schema)
    if 'items' in schema:
        db_schema = add_single_or_multiple('items', schema, add_schema, db_schema)

    parent.schemas.append(db_schema)
    return parent


def add_parameter(parent: Base, param: dict):
    db_param = Parameter(
        name=param.get('name'),
        description=param.get('description'),
        optional=param.get('optional', False),
        deprecated=param.get('deprecated', False),
        experimental=param.get('experimental', False),
        default=str(param['default']) if 'default' in param else None,
    )
    db_param = add_single_or_multiple('schema', param['schema'], add_schema, db_param)
    parent.parameters.append(db_param)
    return parent


def add_return(parent: Base, returns: dict):
    db_return = Return(
        description=returns.get('description', None),
    )
    db_return = add_single_or_multiple('schema', returns, add_schema, db_return)
    parent.returns = db_return
    return parent


def add_exception(parent: Base, exception: dict):
    parent.exceptions.append(ExceptionCode(
        description=exception.get('description', None),
        message=exception.get('message'),
        http=exception.get('http', 400),
        error_code=exception.get('error_code')
    ))
    return parent


def add_link(parent: Base, link: dict):
    parent.links.append(Link(
        rel=link.get('rel'),
        href=link.get('href'),
        type=link.get('type', None),
        title=link.get('title', None),
    ))
    return parent
