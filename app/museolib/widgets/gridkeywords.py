__all__ = ('GridKeywords', )

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, \
        NumericProperty, StringProperty


class GridKeyword(ToggleButton):

    selected = BooleanProperty(False)
    controler = ObjectProperty(None)
    group = ObjectProperty(None)
    text_id = StringProperty(None)
    all_keys = ObjectProperty(None)
    isInverted = BooleanProperty(True)

    def on_touch_down(self, touch):
        ret = super(GridKeyword, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self.selected = not self.selected
            print self.center
        return ret

    def on_selected(self, instance, value):
        keywords = self.controler.selected_keywords
        key = (self.group, self.text_id)

        if self.isInverted:
            for keyw in keywords:
                if self.group in keyw:
                    keywords.remove(keyw)                
            if key in keywords:
                keywords.remove(key)
            if self.state == 'down':
                if not key in keywords:
                    keywords.append(key)
        else:
            if value:
                if not key in keywords:
                    keywords.append(key)
                    self.group.count_selected += 1
            else:
                if key in keywords:
                    keywords.remove(key)
                    self.group.count_selected -= 1


class GridKeywordsGroup(GridLayout):
    title = StringProperty('')
    accitem = ObjectProperty(None)
    count_selected = NumericProperty(0)

class GridKeywords(GridLayout):

    keywords = ListProperty([])

    alphabetical_sort = BooleanProperty(True)

    selected_keywords = ListProperty([])

    title_template = StringProperty(None)

    isInverted = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(GridKeywords, self).__init__(**kwargs)

    def on_keywords(self, instance, value):
        self.clear_widgets()

        accitem = None
        accgroup = None
        for item in value:
            if item['group'].find('filtre') == -1 : # We don't use groups with "filtre" in the name, -> only for imagebuttons
                # create new group
                accgroup = GridKeywordsGroup(title=item['group'])#, accitem=accitem)
                self.add_widget(accgroup)

                children = item['children']
                keys = []
                for child in children:
                    keys.append(child['id']) # we store all keyword keys of each group 

                if self.alphabetical_sort:
                    children.sort(key=lambda x: x['name'])
                for child in children:
                    keyword = GridKeyword(text=child['name'].upper(), text_id=child['id'],
                            controler=self, group=accgroup, all_keys=keys, isInverted=self.isInverted)
                    accgroup.buttons_layout.add_widget(keyword)

    def clear_all(self):
        for group in self.children:
            for keyword in group.buttons_layout.children:
                keyword.selected = False
