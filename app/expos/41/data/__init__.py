# -*- coding: utf-8 -*-

from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty


from os.path import join, isfile, basename, getsize
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
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
from kivy.core.window import Window
from kivy.graphics import Line, Color, Rectangle
from kivy.uix.label import Label
from kivy.clock import Clock
from time import time



TIMER = 10

# TIMER = 15


class QuizzSelector(Scatter):

    english = BooleanProperty(False)

    app = ObjectProperty()
    
    def on_press(self, but, stro):
        if stro == 'but1':
            self.img_active_1.opacity = 1
        elif stro == 'but2':
            self.img_active_2.opacity = 1    
    
    def on_release(self, but, stro):
        if stro == 'but1':
            self.img_active_1.opacity = 0
            if self.app.limite < 4:
                self.app.limite += 1
                question = QuizzMere(app=self.app, deuxJoueurs=False, english = self.english)
                self.parent.add_widget(question)

        elif stro == 'but2':
            if self.app.limite < 4:
                self.app.limite += 1
                question = QuizzMere(app=self.app, deuxJoueurs=True, english = self.english)
                self.parent.add_widget(question)
            self.img_active_2.opacity = 0

class QuizzButton(Button):
    disabled = BooleanProperty(False)

    def on_touch_down(self, touch):
        if not self.disabled:
            ret = super(QuizzButton, self).on_touch_down(touch)
            return ret
        return

class QuizzToggleButton(ToggleButton):
    disabled = BooleanProperty(False)

    def on_touch_down(self, touch):
        if not self.disabled:
            ret = super(QuizzToggleButton, self).on_touch_down(touch)
            return ret
        return
        
class QuizzMere(FloatLayout):
    
    app = ObjectProperty()

    # Indique si le quizz est en anglais
    english = BooleanProperty(False)

    #indique quel bouton a permis de creer le quizz
    originEnglish = BooleanProperty(False)

    # Defini si on a un ou deux joueurs
    deuxJoueurs = BooleanProperty(False)

    # indique que le widget est entrain de se fermer
    closing = BooleanProperty(False)


    Joueur1 = ObjectProperty()
    Joueur2 = ObjectProperty()

    P1 = ObjectProperty((-100,-100))
    P2 = ObjectProperty((-100,-100))
    R1 = NumericProperty(0)
    R2 = NumericProperty(0)

    # Coordonnées pour tracer la ligne blanche
    J1x = NumericProperty(0)
    J1y = NumericProperty(0)
    J2x = NumericProperty(0) 
    J2y = NumericProperty(0)

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

    # Permet de savoir si les 2 joueurs sont pret à commencer
    sync_commencer = BooleanProperty(False)

    # Images de bonne et mauvaise réponse
    medias = ListProperty(None)

    # temps restant pour répondre
    timer = NumericProperty(0)
    timeStart = NumericProperty(0)

    def __init__(self, **kwargs):
        super(QuizzMere, self).__init__(**kwargs)

        # Definition de l'ordre des question
        self.ordreQuestion = sample(range(len(self.app.db.items)), min(5,len(self.app.db.items)))

        self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]

        self.originEnglish = self.english

        if self.item['english'] == []:
            self.english = False

        self.Joueur1 = QuizzItem(app=self.app, mere=self)
        if self.P1 != (-100,-100):
            self.Joueur1.rotation = self.R1
            self.Joueur1.pos = self.P1
            
        self.J1x = self.Joueur1.center_x
        self.J1y = self.Joueur1.y + 200
        self.add_widget(self.Joueur1)

        if self.deuxJoueurs:
            self.Joueur2 = QuizzItem(app=self.app, mere=self)
            if self.P2 != (-100,-100):
                self.Joueur2.rotation = self.R2
                self.Joueur2.pos = self.P2
                
            self.add_widget(self.Joueur2)
            self.J2x = self.Joueur2.center_x
            self.J2y = self.Joueur2.y + 200

        # self.rebuild()

    def rebuild(self):
        if self.item['english'] == []:
            self.english = False

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

        self.timer = TIMER
        self.timeStart = time()
        Clock.schedule_interval(self.update_timer, 1 / 10.)


    def update_pos(self, fils, center_x, y):
        if fils == self.Joueur1:
            self.J1x = center_x
            self.J1y = y + 200
        else:
            self.J2x = center_x
            self.J2y = y + 200

    def check_reponse(self):
        self.correction = True
        finishJ1 = False
        finishJ2 = False

        if not self.deuxJoueurs:
            if self.Joueur1.btnBonneReponse.state == 'down':
                self.Joueur1.bonneReponse = True
                self.Joueur1.correction = True
                self.Joueur1.transform_ui()
                self.Joueur1.score += 1
                self.Joueur1.btnBonneReponse.state = 'normal'
            else:
                self.Joueur1.bonneReponse = False
                self.Joueur1.correction = True
                self.Joueur1.transform_ui()
                self.Joueur1.btnMauvaiseReponse.state = 'normal'

            self.Joueur1.btnBonneReponse.disabled = True
            self.Joueur1.btnMauvaiseReponse.disabled = True
            Clock.unschedule(self.update_timer)
        else:
            if self.timer>0:
                if self.Joueur1.btnBonneReponse.state == 'down' or self.Joueur1.btnMauvaiseReponse.state == "down":
                    finishJ1 = True
                if self.Joueur2.btnBonneReponse.state == 'down' or self.Joueur2.btnMauvaiseReponse.state == "down":
                    finishJ2 = True
                if finishJ1 and finishJ2:
                    Clock.unschedule(self.update_timer)
                else:
                    return
            if self.Joueur1.btnBonneReponse.state == 'down':
                self.Joueur1.bonneReponse = True
                self.Joueur1.correction = True
                self.Joueur1.transform_ui()
                self.Joueur1.score += 1
                self.Joueur1.btnBonneReponse.state = 'normal'
            else:
                self.Joueur1.bonneReponse = False
                self.Joueur1.correction = True
                self.Joueur1.transform_ui()
                self.Joueur1.btnMauvaiseReponse.state = 'normal'

            self.Joueur1.btnBonneReponse.disabled = True
            self.Joueur1.btnMauvaiseReponse.disabled = True
            if self.Joueur2.btnBonneReponse.state =='down':
                self.Joueur2.bonneReponse = True
                self.Joueur2.correction = True
                self.Joueur2.transform_ui()
                self.Joueur2.score += 1
                self.Joueur2.btnBonneReponse.state = 'normal'
            else:
                self.Joueur2.bonneReponse = False
                self.Joueur2.correction = True
                self.Joueur2.transform_ui()
                self.Joueur2.btnMauvaiseReponse.state = 'normal'

            self.Joueur2.btnBonneReponse.disabled = True
            self.Joueur2.btnMauvaiseReponse.disabled = True

            if self.Joueur1.score > self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 0
                self.Joueur2.imageScoreLose.opacity = 1
            elif self.Joueur1.score == self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0
            else:
                self.Joueur1.imageScoreWin.opacity = 0
                self.Joueur1.imageScoreLose.opacity = 1
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0
        
    def bonne_reponse(self, fils):
        if self.correction:
            return

        self.correction = True
        self.Joueur1.btnBonneReponse.disabled = True
        self.Joueur1.btnMauvaiseReponse.disabled = True
        if self.deuxJoueurs:        
            self.Joueur2.btnBonneReponse.disabled = True
            self.Joueur2.btnMauvaiseReponse.disabled = True

        if fils == self.Joueur1:    
            self.Joueur1.bonneReponse = True
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()
            self.Joueur1.score += 2

            if self.deuxJoueurs:
                self.Joueur2.bonneReponse = False
                self.Joueur2.correction = True
                self.Joueur2.transform_ui()

                if self.Joueur1.score > self.Joueur2.score:
                    self.Joueur1.imageScoreWin.opacity = 1
                    self.Joueur1.imageScoreLose.opacity = 0
                    self.Joueur2.imageScoreWin.opacity = 0
                    self.Joueur2.imageScoreLose.opacity = 1
                elif self.Joueur1.score == self.Joueur2.score:
                    self.Joueur1.imageScoreWin.opacity = 1
                    self.Joueur1.imageScoreLose.opacity = 0
                    self.Joueur2.imageScoreWin.opacity = 1
                    self.Joueur2.imageScoreLose.opacity = 0
                else:
                    self.Joueur1.imageScoreWin.opacity = 0
                    self.Joueur1.imageScoreLose.opacity = 1
                    self.Joueur2.imageScoreWin.opacity = 1
                    self.Joueur2.imageScoreLose.opacity = 0
        else: 
            self.Joueur2.bonneReponse = True
            self.Joueur2.correction = True
            self.Joueur2.transform_ui()
            self.Joueur2.score += 2

            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()

            if self.Joueur1.score > self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 0
                self.Joueur2.imageScoreLose.opacity = 1
            elif self.Joueur1.score == self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0
            else:
                self.Joueur1.imageScoreWin.opacity = 0
                self.Joueur1.imageScoreLose.opacity = 1
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0

    def mauvaise_reponse(self, fils):
        if self.correction:
            return

        self.correction = True
        self.Joueur1.btnBonneReponse.disabled = True
        self.Joueur1.btnMauvaiseReponse.disabled = True
        
        if self.deuxJoueurs:
            self.Joueur2.btnBonneReponse.disabled = True      
            self.Joueur2.btnMauvaiseReponse.disabled = True

        if fils == self.Joueur1:        
            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.score -= 1
            self.Joueur1.transform_ui()

            if self.deuxJoueurs:
                self.Joueur2.bonneReponse = False
                self.Joueur2.correction = True
                self.Joueur2.transform_ui()

                if self.Joueur1.score > self.Joueur2.score:
                    self.Joueur1.imageScoreWin.opacity = 1
                    self.Joueur1.imageScoreLose.opacity = 0
                    self.Joueur2.imageScoreWin.opacity = 0
                    self.Joueur2.imageScoreLose.opacity = 1
                elif self.Joueur1.score == self.Joueur2.score:
                    self.Joueur1.imageScoreWin.opacity = 1
                    self.Joueur1.imageScoreLose.opacity = 0
                    self.Joueur2.imageScoreWin.opacity = 1
                    self.Joueur2.imageScoreLose.opacity = 0
                else:
                    self.Joueur1.imageScoreWin.opacity = 0
                    self.Joueur1.imageScoreLose.opacity = 1
                    self.Joueur2.imageScoreWin.opacity = 1
                    self.Joueur2.imageScoreLose.opacity = 0

        else: 
            self.Joueur2.bonneReponse = False
            self.Joueur2.correction = True
            self.Joueur2.score -= 1
            self.Joueur2.transform_ui()

            self.Joueur1.bonneReponse = False
            self.Joueur1.correction = True
            self.Joueur1.transform_ui()

            if self.Joueur1.score > self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 0
                self.Joueur2.imageScoreLose.opacity = 1
            elif self.Joueur1.score == self.Joueur2.score:
                self.Joueur1.imageScoreWin.opacity = 1
                self.Joueur1.imageScoreLose.opacity = 0
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0
            else:
                self.Joueur1.imageScoreWin.opacity = 0
                self.Joueur1.imageScoreLose.opacity = 1
                self.Joueur2.imageScoreWin.opacity = 1
                self.Joueur2.imageScoreLose.opacity = 0




    def commencer(self, fils):
        if not self.deuxJoueurs:
                self.rebuild()
                self.Joueur1.rebuild()
                self.Joueur1.btnContinuez.unbind(on_release = self.Joueur1.do_commencer)
                self.Joueur1.btnContinuez.bind(on_release = self.Joueur1.do_continue)


        elif self.sync_commencer:
            # fils.btnContinuez.unbind(on_release = fils.do_continue)
            if not self.english:
                fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            else:
                fils.btnContinuez.text = 'WAITING FOR PLAYER TWO'

            fils.btnContinuez.disabled = True

            self.rebuild()
            self.Joueur1.rebuild()
            self.Joueur1.btnContinuez.unbind(on_release = self.Joueur1.do_commencer)
            self.Joueur1.btnContinuez.bind(on_release = self.Joueur1.do_continue)
            # self.Joueur1.btnContinuez.disabled = False
            # self.Joueur1.btnContinuez.bind(on_release = self.Joueur1.do_continue)
            self.Joueur2.rebuild()
            self.Joueur2.btnContinuez.unbind(on_release = self.Joueur2.do_commencer)
            self.Joueur2.btnContinuez.bind(on_release = self.Joueur2.do_continue)
            # self.Joueur2.btnContinuez.disabled = False
            # self.Joueur2.btnContinuez.bind(on_release = self.Joueur2.do_continue)
        else:
            # fils.btnContinuez.unbind(on_release = fils.do_continue)
            fils.btnContinuez.disabled = True
            if not self.english:
                fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            else:
                fils.btnContinuez.text = 'WAITING FOR PLAYER TWO'
            self.sync_commencer = True


    def continuer(self, fils):
        if not self.correction:
            return

        if not self.deuxJoueurs:
            self.numeroQuestion += 1

            if self.numeroQuestion >= len(self.ordreQuestion):
                if self.Joueur1.score > 2:
                    self.Joueur1.victoire = True
                else:
                    self.Joueur1.victoire = False

                self.Joueur1.affichage_final()

            else:
                self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]
                self.rebuild()
                self.Joueur1.rebuild()
        elif self.sync_continuer:
            # fils.btnContinuez.unbind(on_release = fils.do_continue)
            if not self.english:
                fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            else:
                fils.btnContinuez.text = 'WAITING FOR PLAYER TWO'

            self.numeroQuestion += 1

            if self.numeroQuestion >= len(self.ordreQuestion):
                if self.Joueur1.score > self.Joueur2.score:
                    self.Joueur1.victoire = True
                    self.Joueur2.victoire = False
                elif self.Joueur1.score == self.Joueur2.score:
                    if self.Joueur1.score > 2:
                        self.Joueur1.victoire = True
                        self.Joueur2.victoire = True
                    else:
                        self.Joueur1.victoire = False
                        self.Joueur2.victoire = False
                
                else:
                    self.Joueur1.victoire = False
                    self.Joueur2.victoire = True
                
                self.Joueur1.affichage_final()
                self.Joueur2.affichage_final()
            else:
                self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]
                self.rebuild()
                self.Joueur1.rebuild()
                # self.Joueur1.btnContinuez.disabled = False
                # self.Joueur1.btnContinuez.bind(on_release = self.Joueur1.do_continue)
                self.Joueur2.rebuild()
                # self.Joueur2.btnContinuez.disabled = False
                # self.Joueur2.btnContinuez.bind(on_release = self.Joueur2.do_continue)
        else:
            # fils.btnContinuez.unbind(on_release = fils.do_continue)
            fils.btnContinuez.disabled = True
            if not self.english:
                fils.btnContinuez.text = 'EN ATTENTE DU DEUXIEME JOUEUR'
            else:
                fils.btnContinuez.text = 'WAITING FOR PLAYER TWO'
            self.sync_continuer = True

    def other_score(self, fils):
        if fils ==  self.Joueur1:
            return self.Joueur2.score
        else:
            return self.Joueur1.score

    def close(self, kwarg):
        if not self.closing:
            self.closing = True
            self.Joueur1.btnClose.unbind(on_release = self.close)
            if self.deuxJoueurs:
                self.Joueur2.btnClose.unbind(on_release = self.close)

            self.app.limite -= 1

            self.parent.remove_widget(self)

    def restart(self, kwarg):
        if not self.closing:
            self.closing = True

            if self.deuxJoueurs:
                question = QuizzMere(app=self.app, deuxJoueurs=True, english = self.english, P1=self.Joueur1.pos, R1= self.Joueur1.rotation, P2=self.Joueur2.pos, R2= self.Joueur2.rotation)
            else:
                question = QuizzMere(app=self.app, deuxJoueurs=False, english = self.english, P1=self.Joueur1.pos, R1= self.Joueur1.rotation)
            self.parent.add_widget(question)

            self.parent.remove_widget(self)

    def update_timer(self, kwarg):
        self.timer = TIMER - time() + self.timeStart

        if self.timer<0:
            Clock.unschedule(self.update_timer)
            self.check_reponse()

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

    # Permet de savoir si on a gagné la partie
    victoire = BooleanProperty(False)

    height_bar = NumericProperty(85)


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

        if self.pos == (-100,-100):
            if self.mere.originEnglish:
                self.center = (randint(200,760), randint(200,880))
                self.rotation = randint(135,225)
            else:
                self.center = (randint(1160,1720), randint(200,880))
                self.rotation = randint(-45,45)


        # self.rebuild()
        self.affichage_debut()


        # self.btnMauvaiseReponse.bind(on_release= self.do_mauvaise_reponse)
        # self.btnBonneReponse.bind(on_release= self.do_bonne_reponse)
        self.btnContinuez.bind(on_release= self.do_commencer)

    def on_center(self, instance, value):
        parent = self.parent
        if not parent:
            return
        # causing problems when the item scale was too important
        x, y = value
        x = max(parent.x, x)
        y = max(parent.y, y)
        x = min(parent.right, x)
        y = min(parent.top, y)
        self.center = x, y

    def on_touch_move(self, touch):
        ret = super(QuizzItem, self).on_touch_move(touch)

        self.mere.update_pos(self, self.center_x, self.y)

        return ret

    def do_bonne_reponse(self, kwargs):
        if self.correction:
            return

        self.mere.bonne_reponse(self)

    def do_mauvaise_reponse(self, kwargs):
        if self.correction:
            return
        self.mere.mauvaise_reponse(self)

    def do_reponse(self):
        self.mere.check_reponse()

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

    def do_commencer(self, kwargs):
        self.mere.commencer(self)

    def affichage_debut(self):
        if self.mere.deuxJoueurs:
            if self.mere.english:
                self.labelTitre.text = "Well done! You are brave enough to enter the arena!\nGet a better score than your opponent and at least three correct answers to honour the emperor !\nOtherwise it’s defeat !"
            else:
                self.labelTitre.text = "Bravo ! Vous avez le courage de descendre dans l'arÈne !\nObtenez un score supÉrieur À votre adversaire et au moins trois bonnes rÉponses pour honorer l'empereur !\nSinon c'est la dÉfaite !"
        else:
            if self.mere.english:
                self.labelTitre.text = "Well done!\nYou are brave enough to enter the arena!\nThree correct answers and you honour the emperor, otherwise it’s defeat !"
            else:
                self.labelTitre.text = "BRAVO !\nVOUS AVEZ LE COURAGE DE DESCENDRE DANS L'ARÈNE!\nTROIS BONNES RÉPONSES ET VOUS HONOREREZ L'EMPEREUR, SINON C'EST LA DÉFAITE !"
        self.labelTitre.text = self.labelTitre.text.upper()
        self.labelTitre.halign = 'center'
        self.labelTitre.y = 220

        self.btnBonneReponse.disabled = True
        self.btnBonneReponse.opacity = 0
        self.btnMauvaiseReponse.disabled = True
        self.btnMauvaiseReponse.opacity = 0
        self.btnContinuez.disabled = False
        self.btnContinuez.opacity = 1
        self.btnContinuez.y = 10

        self.height_bar = 0
        self.photo.source = 'widgets/glaive.png'
        self.photo.size= 100,160
        self.photo.pos = 65,50
        
        #height label titre : 119 ou 153
        self.labelTitre.texture_update()
        if self.labelTitre.height == 153:
            self.height = self.height + 153 - 119

        if self.mere.english:
            self.btnContinuez.text = "START"
        else:
            self.btnContinuez.text = 'COMMENCER'

        self.correction = True







        # self.scat_debut = Scatter(pos = (0,0), size = self.size, do_translation= True)

        # with self.scat_debut.canvas:
        #     Color(1,1,1,1)
        #     Rectangle(pos= (0,0), size= self.size)

        # self.scat_debut.add_widget(Label(text= "BRAVO !\nVOUS AVEZ LE COURAGE DE DESCENDRE DANS L'ARÈNE.\nTROIS BONNES RÉPONSES ET VOUS HONOREREZL'EMPEREUR, SINON C'EST LA DÉFAITE !",
        #                                 pos = (10,self.height - 25), size_hint = (None, None), pos_hint = (None, None),
        #                                 color= (117/255.,113/255.,81/255.,1), text_size=(210, None), font_size= 12))

        # # self.scat_debut.add_widget
        # self.add_widget(self.scat_debut)

        # self.scat_debut.bind(on_touch_move = self.suivi)




    # Affiche la bonne reponse
    def transform_ui(self):
        if self.bonneReponse:
            if self.mere.english:
                self.labelTitre.text = 'GOOD ANSWER !'
                self.labelReponse.text = self.mere.item['english']['description']
            else:
                self.labelTitre.text = u'BONNE RÉPONSE !'
                self.labelReponse.text = self.mere.item['description']

            if len(self.mere.medias) > 0:
                self.photo.source = self.mere.medias[0]
        else:
            if self.mere.english:
                self.labelTitre.text = 'BAD ANSWER...'
                self.labelReponse.text = self.mere.item['english']['description2']
            else:
                self.labelTitre.text = u'MAUVAISE RÉPONSE...'
                self.labelReponse.text = self.mere.item['description2']
            if len(self.mere.medias) > 0:
                self.photo.source = self.mere.medias[1]

        #TODO: dessiner la ligne en haut
        self.labelReponse.texture_update() # nécessaire pour actualiser la variable texture_size du label
        self.labelTitre.texture_update() # nécessaire pour actualiser la variable texture_size du label

        global_height = self.labelReponse.y + self.labelReponse.height + 10 + 210 + self.labelTitre.height + 28 + self.btnBonneReponse.height

        anim = Animation(size=(230, global_height), d=0.2)
        anim.start(self)

        anim2 = Animation(y=global_height - 38 - self.btnBonneReponse.height, d=.2)
        anim2.start(self.btnBonneReponse)

        anim1 = Animation(y= global_height - 25, d=0.2)
        anim1.start(self.labelTitre)

        anim3 = Animation(size= (210,210), y=self.labelReponse.y + self.labelReponse.height + 10, x=10, d=.2)
        anim3.start(self.photo)

        self.btnContinuez.opacity = 1
        self.btnContinuez.y = 10
        self.btnContinuez.disabled = False

        self.height_bar = global_height - 30

        self.btnMauvaiseReponse.opacity = 0

    def affichage_final(self):
        if self.victoire:
            self.labelTitre.text = u'BRAVO\nVOUS HONOREZ L\'EMPEREUR'
            self.photo.source = 'widgets/win-laurier.png'

            if self.mere.deuxJoueurs:
                score_win = Label(text=str(self.score), text_size=(35,20), size=(35,20), font_size=20, pos=(70,50), color=(0,0,0,1), halign='center')
                score_lose = Label(text=str(self.mere.other_score(self)), text_size=(35,20), size=(35,20), font_size=20, pos=(125,50), color=(0,0,0,1), halign='center')
                self.add_widget(score_win)
                self.add_widget(score_lose)

        else:
            self.labelTitre.text = u'L\'EMPEREUR A TRANCHÉ...\nVOUS AVEZ PERDU'
            self.photo.source = 'widgets/lose-casque.png' 
            sang = Scatter(center = (115, 155), scale =0.1, size = (210,210), do_scale = False, do_rotation = False, do_translation = False)
            sang.add_widget(Image( source = 'widgets/lose-blood.png', size = (210,210)))
            self.add_widget(sang, 10)

            anim4 = Animation(scale = 1, d=5, t='out_cubic')
            anim4.start(sang)

            if self.mere.deuxJoueurs:
                score_win = Label(text=str(self.mere.other_score(self)), text_size=(35,20), size=(35,20), font_size=20, pos=(70,50), color=(0,0,0,1), halign='center')
                score_lose = Label(text=str(self.score), text_size=(35,20), size=(35,20), font_size=20, pos=(125,50), color=(0,0,0,1), halign='center')
                self.add_widget(score_win)
                self.add_widget(score_lose)

        if self.mere.english :
            self.btnContinuez.text = 'RESTART' 
        else:
            self.btnContinuez.text = 'RECOMMENCER' 

        self.btnContinuez.disabled = False

        self.btnContinuez.unbind(on_release = self.do_continue)
        self.btnContinuez.bind(on_release = self.mere.restart)

        if self.mere.deuxJoueurs:

            img_win = Image(size=(20, 20), pos = (50,50), source='widgets/score-illust-laurrier.png')
            img_lose = Image(size=(20, 20), pos = (160,50), source='widgets/score-illust-pouce.png')
            ligne = Image(size=(20,20), pos=(105,50), source='widgets/hr-vertical.png')


            self.add_widget(img_win)
            self.add_widget(img_lose)
            self.add_widget(ligne)



        self.photo.y = 150

        self.btnClose.opacity = 1
        self.btnClose.disabled = False
        self.btnClose.bind (on_release = self.mere.close)

        self.labelReponse.text = ''
        self.btnBonneReponse.opacity = 0
        self.btnBonneReponse.disabled = True
        self.btnMauvaiseReponse.opacity = 0
        self.btnMauvaiseReponse.disabled = True

        
        global_height = 10 + 210 + self.labelTitre.height + 60

        anim4 = Animation(height_bar = (global_height - 50), d=0.2)
        anim4.start(self)
        # self.height_bar = global_height - 50
        
        anim = Animation(size=(230, global_height), d=0.2)
        anim.start(self)


        anim1 = Animation(y= global_height - 40, d=0.2)
        anim1.start(self.labelTitre)

        anim3 = Animation(size= (210,210), center_y=165, d=.2)
        anim3.start(self.photo)

        # if not self.victoire:
        #     anim3.start(sang)

    def rebuild(self):

        Animation.stop_all(self)
        Animation.stop_all(self.photo)
        Animation.stop_all(self.btnBonneReponse)
        Animation.stop_all(self.labelTitre)

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
        if self.mere.english:
            self.labelTitre.text = self.mere.item['english']['nom'].upper()
            self.btnMauvaiseReponse.text = self.mere.item['english']['freefield'].upper()
            self.btnBonneReponse.text = self.mere.item['english']['orig_geo_prec'].upper()
        else:
            self.labelTitre.text = self.mere.item['nom'].upper()
            self.btnMauvaiseReponse.text = self.mere.item['freefield'].upper()
            self.btnBonneReponse.text = self.mere.item['orig_geo_prec'].upper()
        
        self.photo.source= self.mere.item.filename
        self.labelReponse.text = ''
        # self.labelMauvaiseReponse.opacity = 0


        self.position = choice([0,1])
        self.bonneReponse = False
        self.correction = False
        
        self.btnContinuez.opacity = 0
        self.btnContinuez.pos = 10,100
        self.btnMauvaiseReponse.opacity = 1
        self.btnBonneReponse.opacity = 1
        self.btnMauvaiseReponse.y = 10
        self.btnBonneReponse.y = 10
        self.btnBonneReponse.disabled = False
        self.btnMauvaiseReponse.disabled = False

        # self.btnContinuez.bind(on_release = self.do_continue)
        if self.mere.english:
            self.btnContinuez.text = 'CONTINUE'
        else:
            self.btnContinuez.text = 'CONTINUER'
        self.btnContinuez.disabled = True

        self.btnBonneReponse.texture_update()
        self.btnMauvaiseReponse.texture_update()

        if self.position:
            self.btnBonneReponse.y = self.btnMauvaiseReponse.y + self.btnMauvaiseReponse.height +5
        else:
            self.btnMauvaiseReponse.y = self.btnBonneReponse.y + self.btnBonneReponse.height + 5

        self.labelTitre.texture_update() 

        self.labelTitre.halign = 'left'

        self.labelTitre.y = 10 + self.btnBonneReponse.height + self.btnMauvaiseReponse.height + 10 + 10
        self.size = (230,354 + (self.labelTitre.height - 32) + self.btnBonneReponse.height -32 + self.btnMauvaiseReponse.height -32+ 10) 

        

        self.photo.size = 230,230
        self.photo.pos = 0, self.labelTitre.y + self.labelTitre.height + 10
        # self.photo.pos = 0,124

        self.height_bar = self.btnMauvaiseReponse.height + self.btnBonneReponse.height + 10 + 10 + 5 #85
        # if self.mere.other_score(self) > self.score:
        #     self.imageScoreWin.opacity = 0
        #     self.imageScoreLose.opacity = 1
        # else:
        #     self.imageScoreWin.opacity = 1
        #     self.imageScoreLose.opacity = 0

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    app.limite = 0

    bgmap = Image(source = 'widgets/map.png', size=(1920,1080))
    root.add_widget(bgmap)

    # question = QuizzMere(app=app, deuxJoueurs=True)

    # question = QuizzItem(app=app)


    # question = QuizzItem(app=app)

    # root.add_widget(question)

    #### BUTTONS TO SWITCH TO EXPO

    def increase_button(but):
        scat = but.parent
        anim = Animation(scale=1.3, d=.05) + Animation(scale=1, d=.05)
        Animation.stop_all(scat)
        anim.start(scat)
    
    def change_expo(but):
        par = but.parent
        if par.center_y < 100: # then its the button at the bottom left of the screen
            anim = Animation(center=(-75,-75), d=.1)
            anim2 = Animation(pos=(0,0), d=.1)
            anim2.start(scat5)
        else:
            anim = Animation(center=(Window.width + 75, Window.height + 75), d=.1)
            anim2 = Animation(pos=(Window.width - scat6.width, Window.height-scat6.height), d=.1)
            anim2.start(scat6)
        anim.start(par)

    def load_expo(but):
        app.change_expo(str(40))

    scat = Scatter( size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    rotation=-90 ,
                    center=(75, 75))    

    but = Button(   size=(85,85),
                    size_hint= (None,None),
                    background_normal='widgets/btn-loupe.png',
                    background_down='widgets/btn-loupe.png',
                    on_press=increase_button,
                    on_release=change_expo)
    scat.add_widget(but)
    root.add_widget(scat)
    scat.center = (75, 75)
    # scat.rotation = -22.5

    scat2 = Scatter( size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    rotation=90 ,
                    center=(75, 75))    

    but2 = Button(  size=(85,85),
                    size_hint= (None,None),
                    background_normal='widgets/btn-loupe.png',
                    background_down='widgets/btn-loupe.png',
                    on_press=increase_button,
                    on_release=change_expo)
    scat2.add_widget(but2)
    root.add_widget(scat2)
    scat2.center = (Window.width- 75, Window.height -75)
    # scat2.rotation = 22.5

    ##### FRENCH POPUP

    scat5 = Scatter(
        size=(222,222),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None),
        center=(-300,-300)
        )
    img = Image(
        source='widgets/popup/pop-up-quizFR.png',
        size_hint=(None,None),
        size=(222,222))
    scat51 = Scatter(
        size=(50,50),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None)
    )
    but5 = Button(  size=(50,50),
                    size_hint= (None,None),
                    background_normal='widgets/popup/btn-oui.png',
                    background_down='widgets/popup/btn-oui-active.png',
                    on_release=load_expo
                )
    scat51.add_widget(but5)
    scat61 = Scatter(
        size=(50,50),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None)
    )

    def show_switch_button_fr(dt):
        anim = Animation(center=(75,75), d=.1)
        anim.start(scat)

    def discard_popup_fr(but):
        anim = Animation(center=(-300,-300), d=.1)
        anim.start(scat5)
        anim.on_complete = show_switch_button_fr

    but6 = Button(  size=(50,50),
                    size_hint= (None,None),
                    background_normal='widgets/popup/btn-non.png',
                    background_down='widgets/popup/btn-non-active.png',
                    on_release=discard_popup_fr
            )
    scat61.add_widget(but6)
    scat5.add_widget(img)
    scat5.add_widget(scat51)
    scat5.add_widget(scat61)
    scat51.rotation = -45
    scat61.rotation = -45
    scat51.center = (65,112)
    scat61.center = (108, 68)

    root.add_widget(scat5)

    ##### ENGLISH POPUP

    scat6 = Scatter(
        size=(222,222),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None),
        center=(Window.width+300,Window.height +300)
        )
    img = Image(
        source='widgets/popup/pop-up-quizEN.png',
        size_hint=(None,None),
        size=(222,222))
    scat52 = Scatter(
        size=(50,50),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None),
        center=(65, 112)
    )
    but5 = Button(  size=(50,50),
                    size_hint= (None,None),
                    background_normal='widgets/popup/btn-yes.png',
                    background_down='widgets/popup/btn-yes-active.png',
                    on_release=load_expo
                )
    scat52.add_widget(but5)
    scat62 = Scatter(
        size=(50,50),
        do_scale=False, do_rotation=False, do_translation=False,
        size_hint=(None,None),
        center=(108, 68)
    )

    def show_switch_button_en(dt):
        anim = Animation(center=(Window.width-75,Window.height-75), d=.1)
        anim.start(scat2)

    def discard_popup_en(but):
        anim = Animation(center=(Window.width+300,Window.height+300), d=.1)
        anim.start(scat6)
        anim.on_complete = show_switch_button_en

    but6 = Button(  size=(50,50),
                    size_hint= (None,None),
                    background_normal='widgets/popup/btn-no.png',
                    background_down='widgets/popup/btn-no-active.png',
                    on_release=discard_popup_en
            )
    scat62.add_widget(but6)
    scat6.add_widget(img)
    scat6.add_widget(scat52)
    scat6.add_widget(scat62)
    scat52.rotation = -45
    scat62.rotation = -45
    scat52.center = (65,112)
    scat62.center = (108, 68)
    scat6.rotation = 180

    root.add_widget(scat6)


    ###### BUTTONS TO SELECT A QUIZZ

    quizzSelector1 = QuizzSelector(english=False, pos=(Window.width - 180, 0), app = app)
    root.add_widget(quizzSelector1)


    quizzSelector2 = QuizzSelector(english=True, rotation= 180, pos=(0, Window.height -180), app= app)
    root.add_widget(quizzSelector2)
    quizzSelector2.pos = pos=(0, Window.height -180)
    root.hide_items = True

    # -------------------------------------------------------------------------
    ##### MODE VEILLE

    helpLayout = FloatLayout()

    helpQuizz1Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=-45)
    helpQuizz1 = Image( source='widgets/help/pop-up-help-exploFR.png',
                        size=(320,90))
    helpQuizz1Scat.add_widget(helpQuizz1)
    helpLayout.add_widget(helpQuizz1Scat)
    helpQuizz1Scat.center=(150,150)
    
    helpQuizz2Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=90+45)
    helpQuizz2 = Image( source='widgets/help/pop-up-help-exploEN.png',
                        size=(320,90))
    helpQuizz2Scat.add_widget(helpQuizz2)
    helpLayout.add_widget(helpQuizz2Scat)
    helpQuizz2Scat.center=(Window.width-150,Window.height-150)
    
    helpExpo1Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=-135)
    helpExpo1 = Image( source='widgets/help/pop-up-help-quizEN.png',
                        size=(320,90))
    helpExpo1Scat.add_widget(helpExpo1)
    helpLayout.add_widget(helpExpo1Scat)
    helpExpo1Scat.center=(200,Window.height-200)
    
    helpExpo2Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=45)
    helpExpo2 = Image( source='widgets/help/pop-up-help-quizFR.png',
                        size=(320,90))
    helpExpo2Scat.add_widget(helpExpo2)
    helpLayout.add_widget(helpExpo2Scat)
    helpExpo2Scat.center=(Window.width-200,200)

    root.add_widget(helpLayout)


    def anim_clues(dt):
        Animation.stop_all(helpExpo1Scat)
        Animation.stop_all(helpExpo2Scat)
        Animation.stop_all(helpQuizz1Scat)
        Animation.stop_all(helpQuizz2Scat)

        delta = 5
        dt = dt /10

        anim = Animation(center_x=helpExpo1Scat.center_x + delta, center_y=helpExpo1Scat.center_y - delta, d=dt/2) + Animation(center=helpExpo1Scat.center, d=dt/2)
        anim.start(helpExpo1Scat)
        anim = Animation(center_x=helpExpo2Scat.center_x - delta, center_y=helpExpo2Scat.center_y + delta, d=dt/2) + Animation(center=helpExpo2Scat.center, d=dt/2)
        anim.start(helpExpo2Scat)
        anim = Animation(center_x=helpQuizz1Scat.center_x + delta, center_y=helpQuizz1Scat.center_y + delta, d=dt/2) + Animation(center_x=helpQuizz1Scat.center_x , center_y=helpQuizz1Scat.center_y , d=dt/2)
        anim.start(helpQuizz1Scat)
        anim = Animation(center_x=helpQuizz2Scat.center_x - delta, center_y=helpQuizz2Scat.center_y - delta, d=dt/2) + Animation(center_x=helpQuizz2Scat.center_x , center_y=helpQuizz2Scat.center_y , d=dt/2)
        anim.start(helpQuizz2Scat)

    # Clock.schedule_interval(anim_clues, 2)

    def toggle_help_layout(show=True):
        Animation.stop_all(helpLayout)
        if show:
            anim = Animation(opacity=1, d=1)
            anim.start(helpLayout)
        else:
            anim = Animation(opacity=0, d=1)
            anim.start(helpLayout)

    def launch_screensaver(dt):
        delay = time() - app.last_touch_time
        if delay > 15:
            Clock.schedule_interval(anim_clues, 2)
            toggle_help_layout(show=True)
            Clock.unschedule(launch_screensaver)

    Clock.schedule_interval(launch_screensaver, 1)

    def stop_screensaver():
        Clock.unschedule(anim_clues)
        Clock.schedule_interval(launch_screensaver, 1)
        toggle_help_layout(show=False)

    app.last_touch_time = 0
    def on_touch_app(touch):
        app.last_touch_time = touch.time_start
        for child in root.children[:]:
            if child.dispatch('on_touch_down', touch):
                stop_screensaver()
                return True

    root.on_touch_down = on_touch_app

    ##### FIN VEILLE


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