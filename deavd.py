# Deductive entity-attribute-value database

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

class Attribute(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str((self.name, self.value))

    def __str__(self):
        return self.name + ':' + self.value

class Bucket(set):
    """ Set of entities """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

def main():
    pippo = Entity('Pippo', './pippo', tags=[
        Tag('animale', attributes=[Attribute('specie', 'supercane')]),
        Tag('parla'),
    ])
    pluto = Entity('Pluto', './pluto', tags=[
        Tag('animale', attributes=[Attribute('specie', 'cane')]),
        Tag('muto', []),
        Tag('personaggio', attributes=[Attribute('esistente', 'no')])
    ])
    animali = Bucket('Animali')
    animali.update(x for x in [pluto, pippo])
    print(animali)
    for animale in animali:
        print(animale)

if __name__ == '__main__':
    main()
