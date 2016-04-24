# Deductive entity-attribute-value database
import functools as f
import pickle

AND = 0
OR = 1
NOT = 2

# EAV
class Entity(object):
    def __init__(self, name, path, tags=None):
        self.name = name
        self.path = path
        self.tags = tags or set()

    def __repr__(self):
        return str((self.name, self.path, self.tags))

    def __str__(self):
        return self.name + ': ' + ', '.join(str(tag) for tag in self.tags)

    def addtag(self, newtag):
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

class Bucket(set):
    """ Set of entities """
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name + ' <{\n' + ';\n'.join(str(ent) for ent in self) + '\n}>'

    def freeze(self):
        return FrozenBucket(self.name, self)

    def add(self, newent):
        if not isinstance(newent, Entity):
            raise ValueError('Cannot add %s to Bucket' % newent)
        if newent in self:
            raise BucketAddException(newent)
        super().add(newent)

    def querytag(self, tag):
        """ Search for all Entities: tag in self """
        for ent in self:
            for x in ent.tags:
                if tag.match(x):
                    yield ent
                    break

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
            return f.reduce(operator, map(prefunc, result))

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
            frozen = self.freeze()
            pickle.dump(frozen, outfile)

class FrozenBucket(object):
    """ A storage only Bucket() """
    def __init__(self, name, ents):
        self.name = name
        self.ents = frozenset(ents)

    def thaw(self):
        b = Bucket(self.name)
        b.update(self.ents)
        return b

def loadbucket(path):
    with open(path, 'rb') as infile:
        frozenbucket = pickle.load(infile)
    return frozenbucket.thaw()

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

class BucketAddException(Exception):
    def __init__(self, ent):
        self.ent = ent

    def __str__(self):
        return "Duplicate entity " + self.ent.name + '; Cannot add!' 

def main():
    b = loadbucket('shapes')

    query = (AND, [
                    (NOT, [Tag('red'), Tag('blue')]),
                    (OR, [Tag('square'), Tag('star')])
                ]
            )

    c = Bucket('Result of query')
    c.update(b.query(query))
    print(c)

if __name__ == '__main__':
    main()
