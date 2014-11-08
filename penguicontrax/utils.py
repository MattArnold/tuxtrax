import functools
import xml.etree.ElementTree as ET

from flask import make_response


# decorator to add uncaching headers
UNCACHE_HEADERS = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache', 'Expires': '0'
}


def uncacheable_response(fun):
    @functools.wraps(fun)
    def wrapped(*args, **kwargs):
        ret = fun(*args, **kwargs)
        # figure out what type of response it was
        if hasattr(ret, 'headers'):   # is a response object
            response = ret
        else:
            # create real response
            if hasattr(ret, 'strip') or \
               not hasattr(ret, '__getitem__'):
                response = make_response(ret)    # handle string
            else:
                response = make_response(*ret)   # handle tuple
        # adds uncacheable headers to response
        for key, val in UNCACHE_HEADERS.items():
            response.headers[key] = val
        return response
    return wrapped


def dump_table_xml(elements, table, parent_node, collection_name,
                   element_name):
    collection = ET.SubElement(parent_node, collection_name)
    for element in elements:
        element_node = ET.SubElement(collection, element_name)
        element_dict = dict((col, getattr(element, col))
                            for col in table.columns.keys())
        for key, value in element_dict.iteritems():
            ET.SubElement(element_node, str(key)).text = unicode(value)
    return collection


def dump_table(elements, table):
    """
    @elements is a result set from sqlalchemy
    @table is the table name used for the result set
    returns a list of dicts
    """
    all = [dict((col, getattr(element, col))
                for col in table.columns.keys())
           for element in elements]
    return all


def dump_table_json(elements, table):
    """
    @elements is a result set from sqlalchemy
    @table is the table name used for the result set
    @returns a string of serialized list of dicts
    """
    return json.dumps(dump_table(elements, table))


