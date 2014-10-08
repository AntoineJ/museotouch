from museolib.utils import convert_to_key
from os.path import basename

class BackendItem(dict):
    @property
    def date(self):
        if 'date_crea' in self:
            # return int(self['date_crea'])
            if self['fields']['date_crea']:
                tmp = int(self['fields']['date_crea'])
            else:
                tmp=0
            return tmp

    @property
    def id(self):
        return int(self['id'])

    @property
    def origin(self):
        if 'orig_geo' in self['fields']:
            return self['fields']['orig_geo']

    @property
    def origin_ex(self):
        if 'orig_geo_prec' in self['fields']:
            return self['fields']['orig_geo_prec']

    @property
    def title(self):
        return self['title']
    
    @property
    def description(self):
        if 'description' in self['fields']:
            return self['fields']['description']
        elif 'cartel' in self['fields']:
            return self['fields']['cartel']
        else:
            return ''

    @property
    def origin_key(self):
        return convert_to_key(self.origin)

    @property
    def freefield(self):
        if 'freefield' in self.fields:
            return self.fields['freefield']
        else:
            return ''

    @property
    def medias(self):
        ret = []
        for x in self['fields']['data']:
            name = x.rsplit('/')[-1].rsplit('.')[0]
            if name == str(self.id):
                continue

            ret.append(basename(x))
        return ret

    @property
    def taille(self):
        try:
            return int(self['fields']['taille'])
        except:
            return 0

    def __getattr__(self, nom):
        """ Si l'attribut n'est pas dans ceux ci dessus, c'est un item du JSON : """
        if nom in self:
            return self[nom]
        elif nom in self['fields']:  # renvoie None sinon
            return self['fields'][nom]
        if nom in self:
            return self[nom]
        else:
            if nom == 'description':
                import pdb; pdb.set_trace()
            raise AttributeError(nom)

    def __setattr__(self, nom, val):
        self[nom] = val

class Backend(object):
    def __init__(self, **options):
        self.items = []
        self.options = options

        for item in self.load_items():
            self.add_item(item)
        self.items = sorted(self.items, key=lambda x: x.date)

    def add_item(self, item):
        assert(isinstance(item, BackendItem))
        self.items.append(item)

    @property
    def length(self):
        return len(self.items)

    # database request
    def get_expos(self, on_success=None, on_error=None):
        pass
