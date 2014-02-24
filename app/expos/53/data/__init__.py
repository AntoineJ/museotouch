#:kivy 1.8.0
# -*- coding: utf-8 -*-
from os.path import join
from glob import glob

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

from museolib.widgets.keywords import Keywords
from museolib.widgets.imageitem import ImageItem
from museolib.widgets.basket import Basket

from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty

from kivy.uix.vkeyboard import VKeyboard
from kivy.core.window import Window
from kivy.uix.widget import Widget 
from kivy.config import Config 

from museolib.widgets.keyboard import Keyboard
from os.path import dirname,abspath, join

# class MyKeyboardListener(Widget):

#     def __init__(self, **kwargs):
#         print('Init keyboard listener')
#         super(MyKeyboardListener, self).__init__(**kwargs)
#         self._keyboard = Window.request_keyboard(
#             self._keyboard_closed, self, 'text')
#         if self._keyboard.widget:
#             print 'in'
#             vkeyboard = self._keyboard.widget
#             vkeyboard.layout = 'layout.json'
#             vkeyboard.size = self.size
#             vkeyboard.key_margin = [0,0,0,0]
#             vkeyboard.margin_hint = [0,0,0,0]
#         self._keyboard.bind(on_key_down=self._on_keyboard_down)


#     def _keyboard_closed(self):
#         print('My keyboard have been closed!')
#         self._keyboard.unbind(on_key_down=self._on_keyboard_down)
#         self._keyboard = None

#     def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#         print('The key', keycode, 'have been pressed')
#         print(' - text is %r' % text)
#         print(' - modifiers are %r' % modifiers)

#         # Keycode is composed of an integer + a string
#         # If we hit escape, release the keyboard
#         if keycode[1] == 'escape':
#             keyboard.release()

#         # Return True to accept the key. Otherwise, it will be used by
#         # the system.
#         return True

# Popup qui contient tout le contenu de l'item (en surimpression)
# Même comportement que pour MGR donc la classe devrait peut-être hériter de Popup plutôt.
class ContentPopup(Scatter):
    item = ObjectProperty(None)
    imgitem = ObjectProperty(None)

ImageItem.popup = ObjectProperty(None)
        
def on_btn_moreinfo(self, *largs):
    # Instanciation de la classe ContentPopup 
    # On passe en paramètre self.item qui contient toutes les infos à afficher
    self.popup = ContentPopup(item=self.item, imgitem=self, size_hint=(None,None), size=(800,800))
    self.parent.add_widget(self.popup)

ImageItem.on_btn_moreinfo = on_btn_moreinfo



def on_start(self):
    pass

ImageItem.on_start = on_start


def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    root.hide_items = False # Désactive l'affichage des items au démarrage

    # keyboard_layout = FloatLayout(size=(300,300), size_hint=(None, None))

    # kbListener = MyKeyboardListener(size=(100,150), size_hint=(None, None))
    # print kbListener._keyboard.widget.font_size
    # print kbListener.size_hint

    # keyboard_layout.add_widget(kbListener)

    # root.add_widget(kbListener)
    curdir = dirname(__file__)
    json_filename = join(curdir, 'layout.json')

    kb = (Keyboard(size=(240,500), size_hint=(None,None), pos =(100,100), layout_filename = json_filename))

    root.add_widget(kb)

    # app.trigger_objects_filtering()

    # layout = GridLayout(cols=7, padding=10, spacing=10,
    #     size_hint=(None, None), width=1920)
    # layout.bind(minimum_height=layout.setter('height'))
    # # add button into that grid
    # for i in range(300):
    #     btn = Button(text=str(i), size=(250, 250),
    #                  size_hint=(None, None))
    #     layout.add_widget(btn)

    # scroll = ScrollView(size_hint=(None, None), size=(1920, 1080),
    #             pos_hint={'center_x': .5, 'center_y': .5}
    #             , do_scroll_x=False)

    # scroll.add_widget(layout)
    # root.add_widget(scroll)

    # widgetlayout = FloatLayout(size=(1920,540), size_hint=(None,None), pos=(0,0))
    # with widgetlayout.canvas:
    #     Color(1,0,1,.2)
    #     Rectangle(
    #         pos=widgetlayout.pos, 
    #         size=widgetlayout.size)
        
    # import random
    # def change_grid(but):
    #     rd = random.randint(1, 100)

    #     layout.clear_widgets()
    #     for i in range(rd):
    #         btn = Button(text=str(i), size=(250, 250),
    #              size_hint=(None, None))
    #         layout.add_widget(btn)

    # but = Button(
    #     text='relayout', 
    #     size=(150,150), 
    #     size_hint=(None, None),
    #     pos= (150,150),
    #     on_release=change_grid
    #     )
    # widgetlayout.add_widget(but)
    # root.add_widget(widgetlayout)




    #### LAISSER CETTE PARTIE SINON CRASH -> variable app.basket appellée dans imageitem
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

