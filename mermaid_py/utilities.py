def get_dict_by_keyval(key, val, list):
    """
    Utility function for accessing nested data in JSON object (dict). Iterates list of dictionaries for matching
    key value pair.
    :param key: key eg. 'name', 'id'.
    :param val: value.
    :param list: eg. list of dict objects to enumerate.
    :return: item where item[key] == val in list.
    """

    for item in list:
        if key in item and item[key] == val:
            return item
    return None
