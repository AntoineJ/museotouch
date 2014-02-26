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
from biinlib.keyboard.keyboard import Keyboard

from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty

from kivy.uix.vkeyboard import VKeyboard
from kivy.core.window import Window
from kivy.uix.widget import Widget 
from kivy.uix.image import Image 
from kivy.config import Config 
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation

from biinlib.keywordscrollview import KeywordScrollView
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

class WidgetsPanel(FloatLayout):
    active = BooleanProperty(False)

    app = ObjectProperty(None)

    keys = ListProperty([])

    title = StringProperty('')

    def __init__(self, **kwargs):
        super(WidgetsPanel, self).__init__(**kwargs)



        self.app.keywords = keywords = KeywordScrollView(
            pos=(self.x + 240, self.y),
            title=u'Thématique',
            app=self.app)
        self.container.add_widget(keywords)
        
        def on_pos(widget, value):
            keywords.pos = value[0] + 240 + 15, value[1]
        self.bind(pos=on_pos)
        
        self.keyboard.bind(on_input = keywords.on_key)

    def toggle_panel(self, but):
        Animation.stop_all(self, 'y')
        if self.active:
            anim = Animation(y=-self.height, t='in_quad', d=.1)
            anim.start(self)
            self.active = False
        else:
            anim = Animation(y=0, t='in_quad', d=.1)
            anim.start(self)
            self.active = True

# En paramètre l'attribut db.items de app et un slug de champ à trouver
# A l'init parcours tous ces champs et les stocke et les affichent dans la liste
# Meme fonction que keywordScrollView pour l'input du clavier le filtre dans la scrollView (Faire une classe mère ?)
# Lorsqu'un label est sélectionné on recherche tous les items qui possèdent ce label et on les rajoutent à la fonction
# de filtre du main (A vérifier)
class FieldScrollView(ScrollView):
    pass

class ContentPopup(Scatter):
    item = ObjectProperty(None)
    imgitem = ObjectProperty(None)
    color = ListProperty([0,0,0,1])

    def __init__(self, **kwargs):
        super(ContentPopup, self).__init__(**kwargs)
        colors = []

        # Find main color in the image
        if self.img is not None:
            cimg = CoreImage(self.img.source, keep_data=True)
            r, g, b = 0, 0, 0
            count = 0
            for i in range(0, cimg.width, 5):
                for j in range(0, cimg.height, 5):
                    try:
                        color = cimg.read_pixel(i,j)
                        if len(color) > 2:
                            r += color[0]
                            g += color[1]
                            b += color[2]
                            count += 1
                            
                    except IndexError as e:
                        print "Can't find color : ", e
                        r , g , b = 0
                        count = 1

            r = r/ count
            g = g/ count
            b = b/ count
            self.color = r,g,b,1


    def close(self, but):
        self.parent.remove_widget(self)


ImageItem.popup = ObjectProperty(None)
        
def on_btn_moreinfo(self, *largs):
    # Instanciation de la classe ContentPopup 
    # On passe en paramètre self.item qui contient toutes les infos à afficher
    self.popup = ContentPopup(item=self.item, imgitem=self, size_hint=(None,None), size=(800,800))
    self.app.root_images.add_widget(self.popup)

ImageItem.on_btn_moreinfo = on_btn_moreinfo



def on_start(self):
    pass

ImageItem.on_start = on_start



def feed_scroll(defs):
    item = ImageItem(**defs)
    app = defs.pop('app')
    app.root.scroller.layout.add_widget(item)



def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    # root.hide_items = False # Désactive l'affichage des items au démarrage
    
    app.should_display_images_by_default = True

    root.scroller = scroller = ScrollView( 
        size_hint=(None, None), 
        size=(1920, 1080),
        pos_hint={'center_x': .5, 'center_y': .5}, 
        do_scroll_x=False)

    root.add_widget(scroller)

    scroller.layout = layout = GridLayout(
        cols=8, 
        col_force_default = True,
        row_force_default = True,
        col_default_width = 223,
        row_default_height = 252,
        padding=15, 
        spacing=15,
        size_hint=(None, None), 
        width=1920)

    scroller.add_widget(layout)


    panel = WidgetsPanel(app=app)
    root.add_widget(panel)

    def my_show_objects(objects):
        self = app
        root = self.root
        if isinstance(self.root_images.x, (int, long)):
            if root.type_expo == 'normal':
                images = [x.source for x in self.root.scroller.layout.children]

                images_to_add = []
                images_displayed = []
                for item in objects:
                    # is the current filename is already showed ?
                    filename = item.filename
                    if filename in images:
                        images.remove(filename)
                        continue

                    # x = randint(self.scroller.layout.x + 200, self.scroller.layout.right - 200)
                    # y = randint(root.y + 300, root.top - 100)
                    # angle = randint(0, 360)

                    image = dict(source=filename, size_hint=(1,1), item=item, app=self)
                    images_to_add.append(image)
                    images_displayed.append(filename)

                self.images_displayed = images_displayed
                self.delayed_work(feed_scroll, images_to_add)

                # remove all the previous images
                for child in self.root.scroller.layout.children[:]:
                    for filename in images:
                        if filename == child.source:
                            self.images_pos[filename] = {
                                'center': child.center,
                                'rotation': child.rotation }
                            self.root.scroller.layout.remove_widget(child)

    app.show_objects = my_show_objects

    # keyboard_layout = FloatLayout(size=(300,300), size_hint=(None, None))

    # kbListener = MyKeyboardListener(size=(100,150), size_hint=(None, None))
    # print kbListener._keyboard.widget.font_size
    # print kbListener.size_hint

    # keyboard_layout.add_widget(kbListener)

    # root.add_widget(kbListener)
    # curdir = dirname(__file__)
    # json_filename = join(curdir, 'layout.json')

    # kb = (Keyboard(size=(240,500), size_hint=(None,None), pos =(100,100), layout_filename = json_filename))

    # root.add_widget(kb)

    app.trigger_objects_filtering()


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

