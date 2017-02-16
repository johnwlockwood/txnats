import attr

@attr.s(slots=True)
class SendPing(object):
    outstanding_pings = attr.ib(
        validator=attr.validators.instance_of(int),
        metadata={
            "json":"outStandingPings",
            "json_out": lambda x: x*3,
            "json_in": lambda x: int(x)/3,
            })


@attr.s(str=True)
class NatsError(Exception):
    "Nats Error"
    fault_count = attr.ib(validator=attr.validators.instance_of(int),
        metadata={
            "json":"faultCount"
            })


def asjsondict(entity):
    entity_dict = attr.asdict(entity)
    for field in attr.fields(entity.__class__):
        if field.metadata.get('json') is not None:
            field_value = getattr(entity, field.name)
            if field.metadata.get('json_out') is not None:
                field_value = field.metadata.get('json_out')(field_value)
            entity_dict[field.metadata.get('json')] = field_value
            del entity_dict[field.name]
    return entity_dict


def fromjsondict(expected_class, entity_dict):
    entity_params = {}
    for field in attr.fields(expected_class):
        key_name = field.name
        if field.metadata.get('json') is not None:
            key_name = field.metadata.get('json')
        
        if key_name in entity_dict:
            value = entity_dict[key_name]
            if field.metadata.get('json_in'):
                value = field.metadata.get('json_in')(value)
            entity_params[field.name] = value

    return expected_class(**entity_params)

