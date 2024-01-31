def convert_value(v):
    if isinstance(v, dict):
        return v
    elif isinstance(v, list):
        new_list = []
        for vv in v:
            new_value = convert_value(vv)
            if isinstance(new_value, list):
                new_list.extend(new_value)
            else:
                new_list.append(new_value)
        return new_list
    elif isinstance(v, str):
        return [{"str": v}]
    elif isinstance(v, int):
        return [{"int": v}]
    elif isinstance(v, float):
        return [{"float": v}]
    elif isinstance(v, bool):
        return [{"bool": v}]
    elif v is None:
        return [{}]
    else:
        return [{"str": str(v)}]
