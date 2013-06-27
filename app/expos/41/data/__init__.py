# -*- coding: utf-8 -*-

from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty


from os.path import join, isfile, basename, getsize
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
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


class QuizzMere(FloatLayout):
    
    app = ObjectProperty()

    # Defini si on a un ou deux joueurs
    deuxJoueurs = BooleanProperty(False)


    Joueur1 = ObjectProperty()
    Joueur2 = ObjectProperty()

    # Item associé à la question
    item = ObjectProperty()

    # Permet de savoir si on est en phase de correction
    correction = BooleanProperty(False)

    # Liste d'id de question
    ordreQuestion = ListProperty([])

    # numero de la question en cours
    numeroQuestion = NumericProperty(0)

    # Permet de savoir si les 2 joueurs sont pret à continuer (peut etre mettre une variable par personne)
    sync_continuer = BooleanProperty(False)

    # Images de bonne et mauvaise réponse
    medias = ListProperty(None)

    def __init__(self, **kwargs):
        super(QuizzMere, self).__init__(**kwargs)

        # Definition de l'ordre des question
        self.ordreQuestion = sample(range(len(self.app.db.items)), min(5,len(self.app.db.items)))

        self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]

        self.Joueur1 = QuizzItem(app=self.app, mere=self)
        self.add_widget(self.Joueur1)

        if self.deuxJoueurs:
            self.Joueur2 = QuizzItem(app=self.app, mere=self)
            self.add_widget(self.Joueur2)


        self.rebuild()


    def rebuild(self):
        self.medias = []
        self.correction = False
        self.sync_continuer = False

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

    
    def bonne_reponse(self, fils):
        if self.correction:
            return

        self.correction = True

        if fils == self.Joueur1:    
            self.Joueur1.bonneReponse = True
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()
            self.Joueur1.score += 2

            self.Joueur2.bonneReponse = False
            self.Joueur2.correction = True
            self.Joueur2.transform_ui()
        else: 
            self.Joueur2.bonneReponse = True
            self.Joueur2.correction = True
            self.Joueur2.transform_ui()
            self.Joueur2.score += 2

            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()




    def mauvaise_reponse(self, fils):
        if self.correction:
            return

        self.correction = True

        if fils == self.Joueur1:        
            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.score -= 1
            self.Joueur1.transform_ui()

            self.Joueur2.bonneReponse = False
            self.Joueur2.correction = True
            self.Joueur2.transform_ui()
        else: 
            self.Joueur2.bonneReponse = False
            self.Joueur2.correction = True
            self.Joueur2.score -= 1
            self.Joueur2.transform_ui()

            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()



    def continuer(self, fils):
        if not self.correction:
            return

        print self.parent, fils

        if not self.deuxJoueurs:
            self.numeroQuestion += 1

            if self.numeroQuestion >= len(self.app.db.items):
                self.parent.remove_widget(self)
            else:
                self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]
                self.rebuild()
                self.Joueur1.rebuild()
        elif self.sync_continuer:
            fils.btnContinuez.unbind(on_release = fils.do_continue)
            fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            self.numeroQuestion += 1

            if self.numeroQuestion >= len(self.app.db.items):
                self.parent.remove_widget(self)
            else:
                self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]
                self.rebuild()
                self.Joueur1.rebuild()
                self.Joueur1.btnContinuez.bind(on_release = self.Joueur1.do_continue)
                self.Joueur2.rebuild()
                self.Joueur2.btnContinuez.bind(on_release = self.Joueur2.do_continue)
        else:
            fils.btnContinuez.unbind(on_release = fils.do_continue)
            fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            self.sync_continuer = True





class QuizzItem(Scatter):

    app = ObjectProperty()

    # Classe Mere
    mere = ObjectProperty()

    #- Item associé à la question 
    item = ObjectProperty()

    # Permet d'avoir une position aléatoire entre les deux réponses
    position = NumericProperty(0)

    # Permet de savoir si on a bien répondu
    bonneReponse = BooleanProperty(False)

    # Permet de savoir si on est en phase de correction
    correction = BooleanProperty(False)

    #- Liste d'id de question
    ordreQuestion = ListProperty([])

    #- numero de la question en cours
    numeroQuestion = NumericProperty(0)

    #- Images de bonne et mauvaise réponse
    medias = ListProperty(None)

    # Score du joueur
    score = NumericProperty(0)

    # image = StringProperty('')
    # question = StringProperty('')
    # bonneReponse = StringProperty('')
    # mauvaiseReponse = StringProperty('')

    def __init__(self, **kwargs):
        
        super(QuizzItem, self).__init__(**kwargs)

        # Definition de l'ordre des question. A revoir pour le mode 2 joueurs
        # self.ordreQuestion = sample(range(len(self.app.db.items)), min(5,len(self.app.db.items)))

        self.item = self.mere.item

        # Position aléatoire des réponses
        self.position = choice([0,1])   
        if self.position:
            self.btnBonneReponse.y = 47
        else:
            self.btnMauvaiseReponse.y = 47


        self.rebuild()


        self.btnMauvaiseReponse.bind(on_release= self.do_mauvaise_reponse)
        self.btnBonneReponse.bind(on_release= self.do_bonne_reponse)
        self.btnContinuez.bind(on_release= self.do_continue)

    def do_bonne_reponse(self, kwargs):
        if self.correction:
            return

        self.mere.bonne_reponse(self)

        # self.bonneReponse = True
        # self.correction = True
        # self.transform_ui()

        # self.score += 2


    def do_mauvaise_reponse(self, kwargs):
        if self.correction:
            return

        self.mere.mauvaise_reponse(self)

        # self.bonneReponse = False
        # self.correction = True
        # self.transform_ui()

    def do_continue(self, kwargs):
        if not self.correction:
            return

        self.mere.continuer(self)

        # self.mere.numeroQuestion += 1

        # if self.numeroQuestion >= len(self.mere.app.db.items):
        #     self.parent.remove_widget(self)
        # else:
        #     self.mere.item = self.mere.app.db.items[self.mere.ordreQuestion[self.mere.numeroQuestion]]
        #     self.rebuild()

    # Affiche la bonne reponse
    def transform_ui(self):

        anim = Animation(size=(230,400), d=0.2)
        anim.start(self)

        anim1 = Animation(y=370, d=0.2)
        anim1.start(self.labelTitre)
        # self.labelTitre.pos = (10,370)
        if self.bonneReponse:
            self.labelTitre.text = 'BONNE REPONSE !'
            self.labelReponse.text = self.mere.item['description']
            if len(self.mere.medias) > 0:
                self.photo.source = self.mere.medias[0]
        else:
            self.labelTitre.text = 'MAUVAISE REPONSE ...'
            self.labelReponse.text = self.mere.item['description2']
            if len(self.mere.medias) > 0:
                self.photo.source = self.mere.medias[1]

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

        # self.medias = []

        # # Ajout des images de bonne/mauvaise reponse
        # for filedata in self.item.data:
        #     if self.item.data.index(filedata) == 0:
        #         continue
        #     else:
        #         fileurl = filedata['fichier']
        #         filename = basename(fileurl)
        #         filepath = join(self.app.expo_dir, 'otherfiles', filename)
        #         if isfile(filepath) and getsize(filepath) > 0:
        #             self.medias.append(filepath)

        self.labelTitre.text = self.mere.item['nom']
        self.btnMauvaiseReponse.text = self.mere.item['freefield']
        self.btnBonneReponse.text = self.mere.item['orig_geo_prec']
        self.photo.source= self.mere.item.filename
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


        # self.btnContinuez.bind(on_release = self.do_continue)
        self.btnContinuez.text = 'CONTINUEZ'


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

    bgmap = Image(source = 'widgets/background.jpg', size=(1920,1080))
    root.add_widget(bgmap)

    question = QuizzMere(app=app, deuxJoueurs=True)

    # question = QuizzItem(app=app)

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