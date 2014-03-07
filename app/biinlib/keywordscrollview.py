#:kivy 1.8.0
# -*- coding: utf-8 -*-
__all__ = ('KeywordScrollView', )

from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from museolib.widgets.keywords import Keyword
import unicodedata
from functools import cmp_to_key

from kivy.logger import Logger
from kivy.uix.button import Button
import re

# En paramètre un groupe de mot-clé précis.
# Parcours la liste des mots-clés et les affiche dans la scrollview
# A l'initialisation se connecte à l'input event du clavier
# Lors d'un changement dans le clavier appelle une fonction de tri qui parcours les labels et suppriment 
# ceux qui ne correspondent pas.
# On garde en mémoire un tableau de tous les labels pour les ajouter ou supprimer sans les recréer à chaque fois

# Chaque label est cliquable et appelle une fonction qui met à jour un tableau selected_keywords
# Le widget est préalablement enregistré en tant qu'attribut keywords sur l'app ce qui lui permettra de filtrer
# le contenu dès que selected_keywords variera
class KeywordScrollView(ScrollView):
    keywords = ListProperty([]) # One group only

    local_keywords = ListProperty([])

    alphabetical_sort = BooleanProperty(True)

    selected_keywords = ListProperty([])

    title = StringProperty('')

    buttons = ListProperty([])

    app = ObjectProperty(None)

    keyboard = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(KeywordScrollView, self).__init__(**kwargs)
        self.container.bind(minimum_height=self.container.setter('height'))
    

    def on_selected_keywords(self, instance, value):
        self.keyboard.clear_text()

    def on_keywords(self, instance, value):
        self.container.clear_widgets()
       
        for item in value:
            group = item['group']
            children = item['children']

            if group == self.title:
                self.local_keywords = children
                break

        for key in self.local_keywords:
            but = KeyScrollItem(
                text= key['name'],
                key= key,
                original_text = key['name'],
                # width=self.width - 60,
                active=True,
                controler=self)
            self.buttons.append(but) 
            self.container.add_widget(but)

    def remove_accents(self, input_str):
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

    def clear_self(self):
        self.selected_keywords = []
        for child in self.container.children:
            # child.active = False
            # self.container.remove_widget(child)
            child.state = 'normal'
    
    def on_key(self, widget, value):  

        next_letters = ''      
        for child in self.buttons:
            if child.text != '':
                uname = self.remove_accents(unicode(child.original_text))
                uname = uname.upper()
                child.text = text = child.original_text
                bold = 'fonts/proximanova-bold-webfont.ttf'
                if value in uname:
                    if value != '':
                        splittxt = uname.split(value, 1)
                        index = uname.index(value)
                        lv = len(value)

                        # print text[index:index+lv], text
                        insensitive_text = re.compile(re.escape(value), re.IGNORECASE)
                        ftext = insensitive_text.sub('[font='+ bold +']' + child.original_text[index: index+lv].upper() + '[/font]', text)                        

                        child.text = ftext                  
                        
                        # TODO
                        # value in uname ne prend en compte que la première occurence de value:
                        # Ce n'est pas très grave pour la fonction de recherche qui n'a besoin que d'une seule occurence
                        # Par contre pour la fonction de prédiction des lettres suivantes c'est plus embetant.
                        # Ci-dessous occurs contient toutes les positions des occurences de value dans uname.
                        # Avec len(value) et la position de value, on peut extraire le caractère suivant de chaque occurence de value
                        
                        occurs = [m.start() for m in re.finditer(re.escape(value), uname)]


                        if len(splittxt) > 1:
                            if len(splittxt[1]) > 0:
                                letter = splittxt[1][0]
                                letter = letter.encode('utf-8')
                                if letter not in next_letters:
                                    next_letters += letter

                    if not child in self.container.children:
                        self.container.add_widget(child)
                        child.active = True
                else:
                    if child in self.container.children:
                        self.container.remove_widget(child)
                        # child.state = 'normal'
                        child.active = False
                        # When a keyword disappear it deactivate itself
                        # for key in self.selected_keywords: 
                        #     if key[1] == child.key['id']:
                        #         self.selected_keywords.remove(key)
            # print 'NEXT : ', next_letters
        
        self.keyboard.next_input(next_letters)


class AttributeScrollView(KeywordScrollView):

    def on_keywords(self, instance, value):
        self.container.clear_widgets()
        # self.local_keywords = sorted(self.keywords)
        self.local_keywords = self.keywords

        for param in self.local_keywords:
            if param != '':
                but = AttributeScrollItem(
                    text= param,
                    active=True,
                    original_text= param,
                    # width=self.width ,
                    controler=self)
                self.buttons.append(but) 
                self.container.add_widget(but)

class KeyScrollItem(ToggleButtonBehavior, Label):
    active = BooleanProperty(True)   

    controler = ObjectProperty(None)             

    key = ObjectProperty(None)

    original_text = StringProperty('')

    def on_release(self):
        key = (self.original_text, self.key['id'])
        if self.state == 'down':
            if key not in self.controler.selected_keywords:
                self.controler.selected_keywords.append(key)
        else:
            if key in self.controler.selected_keywords:
                self.controler.selected_keywords.remove(key)
        

class AttributeScrollItem(KeyScrollItem):

    def on_release(self):
        if self.state == 'down':
            # for child in self.controler.buttons:
            #     if child is not self and child.state == 'down':
            #         child.state = 'normal'
            # del self.controler.selected_keywords[:]
            if self.original_text not in self.controler.selected_keywords:
                self.controler.selected_keywords.append(self.original_text)
        else:
            if self.original_text in self.controler.selected_keywords:
                self.controler.selected_keywords.remove(self.original_text)





