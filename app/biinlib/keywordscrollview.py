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

from kivy.uix.button import Button

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

    def __init__(self, **kwargs):
        super(KeywordScrollView, self).__init__(**kwargs)
        self.container.bind(minimum_height=self.container.setter('height'))
    

    def on_selected_keywords(self, instance, value):
        pass
        # if len(value) == 0:
        #     self.selected_keywords = []


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
                # width= 230,
                active=True,
                controler=self)
            self.buttons.append(but) 
            self.container.add_widget(but)

    def remove_accents(self, input_str):
        nkfd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    
    def on_key(self, widget, value):        
        for child in self.buttons:
            uname = self.remove_accents(child.text)
            uname = uname.upper()

            if value in uname:
                if not child in self.container.children:
                    self.container.add_widget(child)
                    child.active = True
            else:
                if child in self.container.children:
                    self.container.remove_widget(child)
                    child.state = 'normal'
                    child.active = False


class KeyScrollItem(ToggleButtonBehavior, Label):
    active = BooleanProperty(True)   

    controler = ObjectProperty(None)             

    key = ObjectProperty(None)

    def on_release(self):
        if self.state == 'down':
            for child in self.controler.container.children:
                if child is not self and child.state == 'down':
                    child.state = 'normal'
            del self.controler.selected_keywords[:]
            self.controler.selected_keywords.append((None, self.key['id']))


