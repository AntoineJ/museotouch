# -*- coding: utf-8 -*-

from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty


from os.path import join, isfile, basename, getsize
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.slider import SizeSlider
from museolib.widgets.basket import Basket
from kivy.utils import platform
from random import choice, randint, sample, shuffle
from kivy.animation import Animation


class QuizzItem(Scatter):

    app = ObjectProperty()

    # Item associé à la question
    item = ObjectProperty()

    # Permet d'avoir une position aléatoire entre les deux réponses
    position = NumericProperty(0)

    # Permet de savoir si on a bien répondu
    bonneReponse = BooleanProperty(False)

    # Permet de savoir si on est en phase de correction
    correction = BooleanProperty(False)

    # Liste d'id de question
    ordreQuestion = ListProperty([])

    numeroQuestion = NumericProperty(0)

    medias = ListProperty(None)

    # image = StringProperty('')
    # question = StringProperty('')
    # bonneReponse = StringProperty('')
    # mauvaiseReponse = StringProperty('')

    def __init__(self, **kwargs):
        
        super(QuizzItem, self).__init__(**kwargs)

        # Definition de l'ordre des question. A revoir pour le mode 2 joueurs
        self.ordreQuestion = sample(range(len(self.app.db.items)), min(5,len(self.app.db.items)))

        self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]

        # Position aléatoire des réponses
        self.position = choice([0,1])   
        if self.position:
            self.btnBonneReponse.y = 47
        else:
            self.btnMauvaiseReponse.y = 47


        # Ajout des images de bonne/mauvaise reponse
        for filedata in self.item.data:
            if self.item.data.index(filedata) == 0:
                continue
            else:
                fileurl = filedata['fichier']
                filename = basename(fileurl)
                filepath = join(self.app.expo_dir, 'otherfiles', filename)
                if isfile(filepath) and getsize(filepath) > 0:
                    self.medias.append(filepath)


        self.rebuild()


        self.btnMauvaiseReponse.bind(on_release= self.do_mauvaise_reponse)
        self.btnBonneReponse.bind(on_release= self.do_bonne_reponse)
        self.btnContinuez.bind(on_release= self.do_continue)

    def do_bonne_reponse(self, kwargs):
        if self.correction:
            return

        self.bonneReponse = True
        self.correction = True
        self.transform_ui()


    def do_mauvaise_reponse(self, kwargs):
        if self.correction:
            return

        self.bonneReponse = False
        self.correction = True
        self.transform_ui()

    def do_continue(self, kwargs):
        if not self.correction:
            return

        self.numeroQuestion += 1

        if self.numeroQuestion >= len(self.app.db.items):
            pass 
        else:
            self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]
            self.rebuild()

    def transform_ui(self):

        anim = Animation(size=(230,400), d=0.2)
        anim.start(self)


        self.labelTitre.pos = (10,370)
        if self.bonneReponse:
            self.labelTitre.text = 'BONNE REPONSE !'
            self.labelReponse.text = self.item['description']
            if len(self.item['data']) > 1:
                pass
        else:
            self.labelTitre.text = 'MAUVAISE REPONSE ...'
            self.labelReponse.text = self.item['description2']
            if len(self.item['data']) > 1:
                pass

        anim2 = Animation(y=340, d=.2)
        anim2.start(self.btnBonneReponse)

        #TODO: dessiner la ligne en haut

        anim3 = Animation(size= (210,210), y=120, x=10, d=.2)
        anim3.start(self.photo)

        self.btnContinuez.opacity = 1
        self.btnContinuez.y = 10

        # self.btnBonneReponse.opacity = 0
        self.btnMauvaiseReponse.opacity = 0



    def rebuild(self):


        self.labelTitre.text = self.item['nom']
        self.btnMauvaiseReponse.text = self.item['freefield']
        self.btnBonneReponse.text = self.item['orig_geo_prec']
        self.photo.source= self.item.filename
        self.labelReponse.text = ''
        # self.labelMauvaiseReponse.opacity = 0

        self.position = choice([0,1])
        self.bonneReponse = False
        self.correction = False
        self.size = 230,354
        self.btnContinuez.opacity = 0
        self.btnContinuez.pos = 10,100
        self.btnMauvaiseReponse.opacity = 1
        self.btnMauvaiseReponse.y = 10
        self.btnBonneReponse.y = 10

        if self.position:
            self.btnBonneReponse.y = 47
        else:
            self.btnMauvaiseReponse.y = 47

        self.photo.size = 230,230
        self.photo.pos = 0,124

        self.labelTitre.y = 90





def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    question = QuizzItem(app=app)

    root.add_widget(question)




    # -------------------------------------------------------------------------
    # Add a date slider to our root widget.


    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1, 'top': 1},'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0), 'color' : (0,0,0,1), 'bold' : True}
    #active to False disables the basket
    #email_send to True activates sending the url of the basket by email
    #url_send to True activates sending the url of the basket to a specific url 
    app.basket = basket = Basket(
        active = False,
        background_normal='widgets/corner_topright.png',
        background_down='widgets/corner_topright_down.png',
        email_send = True,
        url_send = False,
        url_send_url = 'http://urltest.lapin.be?url=',
        app = app, 
        **kwargs)
    if basket.active :
        #do not offer a basket on tablets, only on tables
        if platform() not in ('android'):  
            root.add_widget(basket)

    # -------------------------------------------------------------------------

    return root