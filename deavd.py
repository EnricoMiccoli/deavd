# Deductive entity-attribute-value database
import functools as f
OR = 1
AND = 0

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
        """ Takes standard polish-venetian query """
        # polish-venetian query: (OR, [a,b,c])
        # (AND, [OR, [a,b,c]), (AND, [n,k,d]])
        print('---- call ----')

        u = lambda x,y: x | y
        n = lambda x,y: x & y

        def queryop(operator):
            result = []
            for request in query[1]:
                if isinstance(request, Tag):
                    print('tag')
                    result.append(set(self.querytag(request)))
                else:
                    print('operator')
                    return self.query(request)

            return (f.reduce(operator, result))

        if query[0] == OR:
            return queryop(u)
        elif query[0] == AND:
            return queryop(n)
        else:
            raise ValueError('Logic operator not recognized: %s' % query[0])

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
    pippo = Entity('Pippo', './pippo')
    pippo.tags.update([
        Tag('animale', attributes={'specie': 'supercane'}),
        Tag('parla'),
    ])
    pluto = Entity('Pluto', './pluto')
    pluto.tags.update([
        Tag('animale', attributes={'specie': 'cane'}),
        Tag('muto'),
        Tag('personaggio', attributes={'esistente': 'no'})
    ])
    canary = Entity('canary', 'canary')
    animali = Bucket('Animali')
    animali.update(x for x in [pluto, pippo, canary])

    query = (OR, [Tag('parla'), Tag('muto'), (OR, [Tag('animale'), Tag('personaggio')])])
    print(animali.query(query))

if __name__ == '__main__':
    main()
