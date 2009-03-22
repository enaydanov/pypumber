#! /usr/bin/env python

def compact_spans(spans):
    starts, ends, count = [], [], 0
    for s, e in spans:
        if s > e:
            raise ValueError('Wrong span: (%d, %d). Start must be less or equal to end.' % (s, e))
        for i in range(count):
            if s >= starts[i] and e <= ends[i]: 
                break # (...[...]...) => (... ... ...)
            elif s <= starts[i] and e >= ends[i]:
                starts[i], ends[i] = None, None # [...(...)...] => [... ... ...]
        else:
            i, j = -1, -1
            if s in ends: 
                i = ends.index(s)
                ends[i] = e # (...)[...]... => (... ...)...
            if e in starts: 
                j = starts.index(e)
                if i != -1: 
                    ends[i], starts[j], ends[j] = ends[j], None, None # (...)[...]<...> => (... ... ...) 
                else:
                    starts[j] = s # ...[...]<...> => ...<... ...>
            if i == -1 and j == -1:
                starts.append(s)
                ends.append(e)
                count += 1
    
    return sorted([x for x in starts if x != None] + [x for x in ends if x != None])


def highlight_groups(matchobj, regular, highlight):
    if matchobj is None:
        return None
    color, chunks, str = [regular, highlight, False], [], matchobj.string
    def reducer(start, end):
        chunks.append(color[color[2]](str[start:end]))
        color[2] = not color[2]
        return end
    reducer(
        reduce(
            reducer, 
            compact_spans(
                matchobj.span(g) 
                for g in xrange(1, len(matchobj.groups())+1) 
                if matchobj.group(g) != None), 
            0), 
        len(str)
    )
    
    return ''.join(chunks)
