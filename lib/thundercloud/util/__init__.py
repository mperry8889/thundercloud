def mergeDict(lhs, rhs, merge=lambda l, r: l):
    if type(lhs) != type(rhs) != dict:
        raise AttributeError

    if lhs == {}:
        return dict(rhs)
    
    if rhs == {}:
        return dict(lhs)
    
    result = dict(lhs)
    for k, v in rhs.iteritems():
        if lhs.has_key(k):
            result[k] = merge(lhs[k], rhs[k])
        else:
            result[k] = v
    
    return result
