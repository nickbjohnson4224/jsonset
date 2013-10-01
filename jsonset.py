import json

class JSONSet(object):

    def __init__(self, test):
        self.test = test

    def __contains__(self, value):
        try:
            return self.test(value)
        except (KeyError, ValueError, TypeError, AttributeError):
            return False

def _build_range(r):
    
    if isinstance(r, (int, long, float)):
        return JSONSet(lambda v: v == r)
    if isinstance(r, list):
        if len(r) == 2 and \
            (isinstance(r[0], (int, long, float)) or r[0] == None) and \
            (isinstance(r[1], (int, long, float)) or r[1] == None):
            
            if r[0] == None:
                if r[1] == None:
                    return JSONSet(lambda v: isinstance(v, (int, long, float)))
                else:
                    return JSONSet(lambda v: v <= r[1])
            else:
                if r[1] == None:
                    return JSONSet(lambda v: v >= r[0])
                else:
                    return JSONSet(lambda v: v >= r[0] and v <= r[1])

    raise ValueError('invalid range specifier %s' % repr(r))

def _build_string(s):

    if len(s) > 0 and s[0] == '$':
        if len(s) > 1 and s[1] == '$':
            return lambda e: e == s[1:]
        if s == '$string':
            return lambda e: isinstance(e, basestring)
        if s == '$number':
            return lambda e: isinstance(e, (int, long, float))
        if s == '$integer':
            return lambda e: isinstance(e, (int, long))
        if s == '$boolean':
            return lambda e: isinstance(e, bool)
        if s == '$any':
            return True
    else:
        return lambda e: e == s

def _build_array(a):
    
    a = [ JSONSet(_build(x)) for x in a ]

    def test_array(value):
        if not isinstance(value, list):
            return False
        if len(a) != len(value):
            return False
        for i in range(len(a)):
            if value[i] not in a[i]:
                return False
        return True

    return test_array

def _build_object(obj):

    if len(obj) == 1:
        key = obj.keys()[0]
        if len(key) > 0 and key[0] == '$':
            if len(key) > 1 and key[1] == '$':
                obj = { k[1:] : JSONSet(_build(v)) for k, v in obj.entries() }
                return lambda e: e.keys() == obj.keys() and all(e[x] in obj[x] for x in e)

            if key == '$union':
                t = [ JSONSet(_build(x)) for x in obj[key] ]
                return lambda e: any(e in x for x in t)
            if key == '$and':
                t = [ JSONSet(_build(x)) for x in obj[key] ]
                return lambda e: all(e in x for x in t)
            if key == '$array':
                t = JSONSet(_build(obj[key]))
                return lambda e: isinstance(e, list) and all(x in t for x in e)
            if key == '$length':
                r = _build_range(obj[key])
                return lambda e: len(e) in r
            if key == '$range':
                r = _build_range(obj[key])
                return lambda v: v in r

            raise ValueError('invalid directive %s' % key)
 
    obj = { k : JSONSet(_build(v)) for k, v in obj.iteritems() }
    return lambda e: e.keys() == obj.keys() and all(e[x] in obj[x] for x in e)

def _build(obj):
    if isinstance(obj, basestring):
        return _build_string(obj)
    if isinstance(obj, (int, long, float, bool)) or obj == None:
        return lambda x: x == obj
    if isinstance(obj, list):
        return _build_array(obj)
    return _build_object(obj)

def loads(s):
    obj = json.loads(s)
    return JSONSet(_build(obj))
