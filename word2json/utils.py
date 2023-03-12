from datetime import datetime, date


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()[:-6] + "Z"
    raise TypeError("Type %s not serializable" % type(obj))
