from typing import Any, Union


def deep_typeof(obj: Any) -> Union[type, str]:
    if isinstance(obj, list):
        # Analyze each element in the list
        element_types = {deep_typeof(item) for item in obj}
        return f"list[{', '.join(map(str, element_types))}]"
    elif isinstance(obj, dict):
        key_types = {deep_typeof(key) for key in obj.keys()}
        value_types = {deep_typeof(value) for value in obj.values()}
        return f"dict[{', '.join(map(str, key_types))}, {', '.join(map(str, value_types))}]"
    elif isinstance(obj, tuple):
        element_types = tuple(deep_typeof(item) for item in obj)
        return f"tuple[{', '.join(map(str, element_types))}]"
    elif isinstance(obj, set):
        element_types = {deep_typeof(item) for item in obj}
        return f"set[{', '.join(map(str, element_types))}]"
    else:
        # Return the type name for basic types
        return type(obj).__name__


def flatten_list(nested_list):
    if not isinstance(nested_list, list):
        return [nested_list]

    flattened = []
    for item in nested_list:
        flattened.extend(flatten_list(item))

    return flattened


def chunk_split(text, group):
    return [text[i : i + group] for i in range(0, len(text), group)]
