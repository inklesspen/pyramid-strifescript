import colander

from colander import (
    Sequence,
    MappingSchema,
    SequenceSchema,
    SchemaNode,
    String,
    Boolean,
    Date,
    Integer,
    All,
    Length,
    Email,
    Invalid,
    Function,
    OneOf
)

from webob.multidict import MultiDict

class Registration(MappingSchema):
    username = SchemaNode(String(), validator=Length(max=50))
    email = SchemaNode(String(), validator=All(Email(), Length(min=3, max=254)), missing=None)
    password = SchemaNode(String(), validator=Length(min=5))


def _add_messages(md, key, error_node):
    for msg in error_node.messages():
        if hasattr(msg, 'interpolate'):
            msg = msg.interpolate()
        md.add(key, msg)

def collect_errors(error_exc):
    collected = MultiDict()
    # Any root-level errors?
    _add_messages(collected, '__form__', error_exc)
    for child in error_exc.children:
        key = child.node.name
        _add_messages(collected, key, child)
    return collected.dict_of_lists()
