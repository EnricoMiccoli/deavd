# Deductive entity-attribute-value database

# EAV
class Entity(object):
    def __init__(self, name, path, tags=[]):
        self.tags = tags
        self.name = name
        self.path = path

    def __repr__(self):
        return str((self.name, self.path, self.tags))

    def __str__(self):
        return self.name + ': ' + ', '.join(str(tag) for tag in self.tags)

    def addtag(self, newtag):
        self.tags.append(newtag)

class Tag(object):
    def __init__(self, name, attributes=[]):
        self.name = name
        self.attributes = attributes

    def __repr__(self):
        return str((self.name, self.attributes))

    def __str__(self):
        return self.name + '{' * bool(self.attributes) + ', '.join(str(att) for att in self.attributes) + '}' * bool(self.attributes)

    def addatt(self, newatt):
        self.tags.append(newatt)

class Attribute(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str((self.name, self.value))

    def __str__(self):
        return self.name + ':' + self.value

    def addval(self, newval):
        self.value = newval # needs check against overwriting

class Bucket(set):
    """ Set of entities """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + ' <{ ' + '; '.join(str(ent) for ent in self) + ' }>'

    def query(self, tag):
        if tag.attributes == []:
            return [ent for ent in self if tag.name in (tag.name for tag in  ent.tags)]
#        else:
#            return [ent for ent in self if
#                    tag.name in (tag.name for tag in  ent.tags) and
#                    set(tag.attributes) < set(ent.attributes)]

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

def main():
    pippo = Entity('Pippo', './pippo', tags=[
        Tag('animale', attributes=[Attribute('specie', 'supercane')]),
        Tag('parla'),
    ])
    pluto = Entity('Pluto', './pluto', tags=[
        Tag('animale', attributes=[Attribute('specie', 'cane')]),
        Tag('muto'),
        Tag('personaggio', attributes=[Attribute('esistente', 'no')])
    ])
    animali = Bucket('Animali')
    animali.update(x for x in [pluto, pippo])
    for animale in animali:
        print(animale)

    print(animali.query(Tag('parla',)))
#   print(animali.query(Tag('personaggio', attributes=[Attribute('esistente', 'no')])))

if __name__ == '__main__':
    main()
