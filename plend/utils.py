from typing import List, Dict, Any


def clean_name(name, replacement: str = '_') -> str:
    cleaned_name = ''
    for char in name:
        if char == name[0] and not char.isidentifier():
            cleaned_name += '_' + char
        elif not char.isalnum():
            cleaned_name += '_'
        else:
            cleaned_name += char
    cleaned_name = cleaned_name.lower() \
                               .replace('__', '_') \
                               .replace('__', '_') \
                               .strip('_')
    if not cleaned_name.isidentifier():
        raise ValueError()
    return cleaned_name
