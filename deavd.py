# Deductive entity-attribute-value database
import functools as f
import pickle
import yaml

AND = 0
OR = 1
NOT = 2

# EAV
class Entity(object):
    def __init__(self, name, path, tags=None):
        self.name = name
        self.path = path
        self.tags = tags or set()
        self.coherence = {'blacklist':[], 'paradoxes':[]}
        self.inference = None

    def __repr__(self):
        return str((self.name, self.path, self.tags))

    def __str__(self):
        return self.name + ': ' + ', '.join(str(tag) for tag in self.tags)

    def addtag(self, newtag):
        if newtag in self.coherence['blacklist']:
            raise TagBlacklistedException(newtag)
        else:
            self.tags.add(newtag)

class Tag(object):
    def __init__(self, name, attributes=None):
        self.name = name
        self.attributes = attributes or {}

    def __repr__(self):
        return str((self.name, self.attributes))

    def __str__(self):
        return self.name + \
            '{' * bool(self.attributes) + \
            ', '.join(':'.join([att,self.attributes[att]]) for att in self.attributes) + \
            '}' * bool(self.attributes)

    def addatt(self, newatt, val):
        self.tags[newatt] = val # check against overwriting

    def match(self, other):
        return self.name == other.name and set(self.attributes.items()) <= set(other.attributes.items())

class Bucket(dict):
    """ Set of entities """
    def __init__(self, name, coherence=None, inference=None):
        super().__init__()
        self.name = name
        self.coherence = coherence
        self.inference = inference

    def __str__(self):
        return self.name + ' <{\n' + ';\n'.join(str(ent) for ent in self) + '\n}>'
    
    def querytag(self, tag):
        """ Search for all Entities: tag in self """
        for entkey in self:
            for x in self[entkey].tags:
                assert isinstance(x, Tag)
                if tag.match(x):
                    assert isinstance(entkey, str)
                    yield entkey
                    break

    def difference(self, other):
        return set(self).difference(set(other))

    def query(self, query):
        """ Takes standard polish query """
        # polish query: (OR, [a,b,c])  (AND, [OR, [a,b,c]), (AND, [n,k,d]])

        u = (lambda x: x, lambda x,y: x | y)
        n = (lambda x: x, lambda x,y: x & y)
        without = (lambda x: self.difference(x), lambda x,y: x & y)

        def queryop(arg):
            prefunc, operator = arg
            result = []
            for request in query[1]:
                if isinstance(request, Tag):
                    result.append(set(self.querytag(request)))
                else:
                    result.append(self.query(request))
            output =  f.reduce(operator, map(prefunc, result))
            assert isinstance(output, set)
            return output # returns set of keys that satisfy query

        if query[0] == OR:
            return queryop(u)
        elif query[0] == AND:
            return queryop(n)
        elif query[0] == NOT:
            return queryop(without)
        else:
            raise ValueError('Logic operator not recognized: %s' % query[0])

    def dump(self, path):
        with open(path, 'wb') as outfile:
            pickle.dump(self, outfile)

def loadbucket(path):
    with open(path, 'rb') as infile:
        bucket =  pickle.load(infile)
        assert isinstance(bucket, Bucket)
        return bucket

def parsequery(querystring):
    words = querystring.split()
    ands = []
    for word in words:
        if word[0] == '-':
            ands.append((NOT, [Tag(word[1:])]))
        elif '/' in word:
            ors = word.split('/')
            ands.append((OR, [Tag(x) for x in ors]))
        else:
            ands.append(Tag(word))
    return (AND, ands)


# EXCEPTIONS
class TagAddError(Exception):
    def __init__(self, ent, tag):
        assert isinstance(ent, Entity)
        assert isinstance(tag, Tag)
        self.tag = tag
        self.ent = ent

    def __str__(self):
        return "Can't add " + self.tag.name + ' to ' + self.ent.name

class AttAddError(Exception):
    def __init__(self, tag, att):
        assert isinstance(tag, Tag)
        assert isinstance(att, Attribute)
        self.att = att
        self.tag = tag

    def __str__(self):
        return "Can't add " + self.att.name + ' to ' + self.tag.name

class ValAddError(Exception):
    def __init__(self, att, val):
        assert isinstance(att, Attribute)
        self.val = val
        self.att = att

    def __str__(self):
        return "Can't add " + self.val + ' to ' + self.att.name

class BucketDuplicateException(Exception):
    def __init__(self, ent):
        self.ent = ent

    def __str__(self):
        return "Duplicate binary " + self.ent.name + '; Cannot add!' 

class TagBlacklistedException(Exception):
    def __init__(self, tag):
        self.ent = ent

    def __str__(self):
        return 'Tag "' + tag.name + '" is blacklisted!'

class CoherenceCheckFail(Exception):
    def __init__(self, fails):
        self.fails = fails

    def __str__(self):
        return 'Coherence fail:' + \
            '\nBlacklisted:' * bool(self.fails[0]) + \
            '\n'.join(self.fails[0]) + \
            '\nParadoxes:' * bool(self.fails[1]) + \
            '\n'.joind(self.fails[1])

def main():
    b = loadbucket('shapes')
    query = (AND, [
                    (NOT, [Tag('red'), Tag('blue')]),
                    (OR, [Tag('square'), Tag('star')])
                ]
            )

    goodkeys = b.query(query)
    c = Bucket('results')
    c.update((key, b[key]) for key in goodkeys)
    print(c)

if __name__ == '__main__':
    main()













