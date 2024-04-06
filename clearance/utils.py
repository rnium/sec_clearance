def get_ordinal_suffix(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    if value % 100 in {11, 12, 13}:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    return suffix

def get_ordinal_number(value):
    return f'{value}{get_ordinal_suffix(value)}'