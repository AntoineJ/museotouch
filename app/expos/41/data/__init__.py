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
from kivy.core.window import Window
from kivy.graphics import Line, Color
from kivy.uix.label import Label

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
        



class QuizzMere(FloatLayout):
    
    app = ObjectProperty()

    # Indique si le quizz est en anglais
    english = BooleanProperty(False)

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

    # Images de bonne et mauvaise réponse
    medias = ListProperty(None)

    def __init__(self, **kwargs):
        super(QuizzMere, self).__init__(**kwargs)

        # Definition de l'ordre des question
        self.ordreQuestion = sample(range(len(self.app.db.items)), min(5,len(self.app.db.items)))

        self.item = self.app.db.items[self.ordreQuestion[self.numeroQuestion]]

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

        self.rebuild()

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

    def update_pos(self, fils, center_x, y):
        if fils == self.Joueur1:
            self.J1x = center_x
            self.J1y = y + 200
        else:
            self.J2x = center_x
            self.J2y = y + 200

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



    def continuer(self, fils):
        if not self.correction:
            return

        if not self.deuxJoueurs:
            self.numeroQuestion += 1

            if self.numeroQuestion >= len(self.app.db.items):
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

            if self.numeroQuestion >= len(self.app.db.items):
                if self.Joueur1.score > self.Joueur2.score:
                    self.Joueur1.victoire = True
                    self.Joueur2.victoire = False
                elif self.Joueur1.score == self.Joueur2.score:
                    self.Joueur1.victoire = True
                    self.Joueur2.victoire = True
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
            self.center = (randint(200,1720), randint(200,880))
            self.rotation = randint(0,360)




        self.rebuild()


        self.btnMauvaiseReponse.bind(on_release= self.do_mauvaise_reponse)
        self.btnBonneReponse.bind(on_release= self.do_bonne_reponse)
        self.btnContinuez.bind(on_release= self.do_continue)

    def on_touch_move(self, touch):
        ret = super(QuizzItem, self).on_touch_move(touch)

        self.mere.update_pos(self, self.center_x, self.y)

        return ret

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
                self.labelReponse.text = str(self.mere.item['description2'])
            if len(self.mere.medias) > 0:
                self.photo.source = self.mere.medias[1]

        #TODO: dessiner la ligne en haut
        self.labelReponse.texture_update() # nécessaire pour actualiser la variable texture_size du label
        self.labelTitre.texture_update() # nécessaire pour actualiser la variable texture_size du label

        global_height = self.labelReponse.y + self.labelReponse.height + 10 + 210 + self.labelTitre.height + 60

        anim = Animation(size=(230, global_height), d=0.2)
        anim.start(self)

        anim2 = Animation(y=global_height - 85, d=.2)
        anim2.start(self.btnBonneReponse)

        anim1 = Animation(y= global_height - 40, d=0.2)
        anim1.start(self.labelTitre)

        anim3 = Animation(size= (210,210), y=self.labelReponse.y + self.labelReponse.height + 10, x=10, d=.2)
        anim3.start(self.photo)

        self.btnContinuez.opacity = 1
        self.btnContinuez.y = 10
        self.btnContinuez.disabled = False

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
        self.size = 230,354
        self.btnContinuez.opacity = 0
        self.btnContinuez.pos = 10,100
        self.btnMauvaiseReponse.opacity = 1
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


        if self.position:
            self.btnBonneReponse.y = 47
        else:
            self.btnMauvaiseReponse.y = 47

        self.photo.size = 230,230
        self.photo.pos = 0,124

        self.labelTitre.y = 90

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

    bgmap = Image(source = 'widgets/background.jpg', size=(1920,1080))
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
        app.change_expo(str(40))



    scat = Scatter( size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    rotation=180 ,
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

    scat2 = Scatter( size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    rotation=180 ,
                    center=(75, 75))    

    but2 = Button(   size=(85,85),
                    size_hint= (None,None),
                    background_normal='widgets/btn-loupe.png',
                    background_down='widgets/btn-loupe.png',
                    on_press=increase_button,
                    on_release=change_expo)
    scat2.add_widget(but2)
    root.add_widget(scat2)
    scat2.center = (Window.width- 75, Window.height -75)


    ###### BUTTONS TO SELECT A QUIZZ

    quizzSelector1 = QuizzSelector(english=False, pos=(Window.width - 180, 0), app = app)
    root.add_widget(quizzSelector1)


    quizzSelector2 = QuizzSelector(english=True, rotation= 180, pos=(0, Window.height -180), app= app)
    root.add_widget(quizzSelector2)
    quizzSelector2.pos = pos=(0, Window.height -180)
    root.hide_items = True

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