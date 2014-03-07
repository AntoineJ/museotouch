#:kivy 1.8.0
# -*- coding: utf-8 -*-

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image

from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty

from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle

from museolib.widgets.imageitem import ImageItem
from museolib.widgets.basket import Basket
from museolib.widgets.slider import SizeSlider

from biinlib.keyboard.keyboard import Keyboard
from biinlib.keywordscrollview import KeywordScrollView, AttributeScrollView

from os.path import dirname,abspath, join

from kivy.clock import Clock

blue = '00a5a2'
bluergb = (0,.647,.635,1)

class WidgetsPanel(FloatLayout):
    active = BooleanProperty(False)

    app = ObjectProperty(None)

    keys = ListProperty([])

    title = StringProperty('')

    def __init__(self, **kwargs):
        super(WidgetsPanel, self).__init__(**kwargs)

        # -------------------------------------------------------------------------
        # Widget Scroll View on one group of Keywords
        self.app.keywords = keywords = KeywordScrollView(
            pos=(self.x + 240 * 4, self.y),
            title=u'Thématique',
            size=(240,420),
            app=self.app,
            keyboard=self.keyboard)
        self.container.add_widget(keywords)
        # Binding widget with keyboard
        self.keyboard.bind(on_input = keywords.on_key)
        keywords.bind(selected_keywords=self.build_sentence)
        # -------------------------------------------------------------------------
        # Date Slider
        self.app.date_slider = slider = SizeSlider(
            size=(448, 240), size_hint=(None, None))
        scatter = Scatter(size=slider.size,
                auto_bring_to_front=False,
                pos=(self.x, self.y - 240),
                size_hint=(None, None), rotation=-90,
                do_translate=False, do_rotate=False, do_scale=False)
        scatter.add_widget(slider)
        slider.reset()
        self.container.add_widget(scatter)
        slider.bind(value_range=self.build_sentence)

        # Find all the titles and authors from item database
        item_names = []
        item_authors = []
        for item in self.app.db.items:
            if item.nom not in item_names:
                item_names.append(item.nom)
            if item.freefield not in item_authors:
                item_authors.append(item.freefield)

        # -------------------------------------------------------------------------
        # Title Scroll View
        title_scroll = AttributeScrollView(
            pos=(self.x + 240, self.y),
            size=(480, 420),
            app = self.app,
            keyboard=self.keyboard)
        self.container.add_widget(title_scroll)
        title_scroll.keywords = item_names
        self.app.title_widget = title_scroll
        # Binding widget with keyboard
        self.keyboard.bind(on_input = title_scroll.on_key)
        # Binding widget with main filtering
        title_scroll.bind(selected_keywords=self.app.trigger_objects_filtering)
        title_scroll.bind(selected_keywords=self.build_sentence)
        # -------------------------------------------------------------------------
        # Author Scroll View
        author_scroll = AttributeScrollView(
            pos=(self.x + 240 * 3, self.y),
            size=(240,420),
            app= self.app,
            keyboard=self.keyboard)
        self.container.add_widget(author_scroll)
        author_scroll.keywords = item_authors
        self.app.author_widget = author_scroll
        # Binding widget with keyboard
        self.keyboard.bind(on_input = author_scroll.on_key)
        # Binding widget with main filtering
        author_scroll.bind(selected_keywords=self.app.trigger_objects_filtering)
        author_scroll.bind(selected_keywords=self.build_sentence)
        # -------------------------------------------------------------------------
        # Moving children widgets with panel
        def on_pos(widget, value):
            title_scroll.pos = self.x + 240 + 2, value[1]
            author_scroll.pos = self.x + 240 * 3 + 4, value[1]
            keywords.pos = value[0] + 240 *4 + 6, value[1]
            scatter.pos = self.x + 240 * 5 + 8, value[1]
        self.bind(pos=on_pos)

    def clear_panel(self):
        self.keyboard.clear_text()
        self.app.keywords.clear_self()
        self.app.title_widget.clear_self()
        self.app.author_widget.clear_self()
        self.app.date_slider.reset()

    def build_sentence(self, instance, value):

        prefix_text = "Trouve moi les livres "
        # TITLE TEXT
        titles = self.app.title_widget.selected_keywords
        if len(titles) > 0:
            if len(titles) == 1:
                self.dynamic_sentence.text = 'Trouve moi le livre [color='+blue+']' + titles[0].encode('utf-8') + '[/color]'
            elif len(titles) > 1:
                title_text = ''
                for title in titles:
                    ttl = title.encode('utf-8')
                    if titles.index(title) == len(titles) - 1:
                        title_text = title_text + ' et [color='+blue+']' + ttl + '[/color]'
                    elif title_text != '':
                        title_text = title_text + ', [color='+blue+']' + ttl + '[/color]'
                    else:
                        title_text = '[color='+blue+']' + ttl + '[/color]'
                self.dynamic_sentence.text = prefix_text + title_text
            
        else:
            # DATE TEXT
            date_min = str(self.app.date_slider.text_min)
            date_max = str(self.app.date_slider.text_max)
            date_text = "parus de [color="+blue+"]" + date_min + "[/color] à [color="+blue+"]" + date_max + "[/color]"

            #AUTHORS TEXT
            authors = self.app.author_widget.selected_keywords
            authors_text = ''
            if len(authors) > 0:
                if len(authors) == 1:
                    authors_text += "de l'auteur [color="+blue+"]" + authors[0].encode('utf-8') + "[/color]"
                elif len(authors) > 1:
                    authors_text = "des auteurs " 
                    for author in authors:
                        auth = author.encode('utf-8')
                        if authors.index(author) == len(authors) - 1:
                            authors_text = authors_text + ' et [color='+blue+']' + auth + '[/color]'
                        elif authors_text != "des auteurs ":
                            authors_text = authors_text + ', [color='+blue+']' + auth + '[/color]'
                        else:
                            authors_text = authors_text + '[color='+blue+']' + auth + '[/color]'
                authors_text = authors_text + ' '

            # THEMES TEXT
            themes = self.app.keywords.selected_keywords
            themes_text = ''
            if len(themes) > 0:
                if len(themes) == 1:
                    themes_text = 'du thème [color='+blue+']' + themes[0][0].encode('utf-8') + '[/color]'
                elif len(themes) > 1:
                    themes_text = 'des thèmes ' 
                    for theme in themes:
                        th = theme[0]
                        th = th.encode('utf-8')

                        if themes.index(theme) == len(themes) -1:
                            themes_text += ' et [color='+blue+']' + th + '[/color]'
                        elif themes_text !=  'des thèmes ':
                            themes_text += ', [color='+blue+']' + th + '[/color]'
                        else:
                            themes_text += '[color='+blue+']' + th + '[/color]'
                themes_text += ' '
                self.dynamic_sentence.text = self.dynamic_sentence2.text = prefix_text + authors_text + themes_text + date_text
        
        self.dynamic_sentence.x = 30
        duration = 15

        def init_anims(dt):
            Animation.stop_all(self.dynamic_sentence)
            if self.dynamic_sentence.width > 1400:
                anim = Animation(x= -self.dynamic_sentence.width -30, d=duration) 
                anim.start(self.dynamic_sentence)
                def callback(dt):
                    self.dynamic_sentence.x = 30

                anim.on_complete = callback

        Clock.unschedule(init_anims)
        def check_width(dt):
            if self.dynamic_sentence.width > 1400:
                init_anims(None)
                Clock.schedule_interval(init_anims, duration)
            else:
                Animation.stop_all(self.dynamic_sentence)
                self.dynamic_sentence.x = 30
                Clock.unschedule(init_anims)

        Clock.unschedule(check_width)
        Clock.schedule_once(check_width, .2) 

    def toggle_panel(self, but):
        Animation.stop_all(self, 'y')
        if self.active:
            anim = Animation(y=-self.height + 60, t='in_quad', d=.1)
            anim.start(self)
            self.active = False
        else:
            anim = Animation(y=0, t='in_quad', d=.1)
            anim.start(self)
            self.active = True

    def close_panel(self):
        if self.active == True:
            self.toggle_panel(None)


class ContentPopup(Scatter):
    item = ObjectProperty(None)
    controler = ObjectProperty(None)
    color = ListProperty([0,0,0,1])
    controler = ObjectProperty(None)
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ContentPopup, self).__init__(**kwargs)

        # Find theme and espace keywords 
        themes = []
        espaces = []
        theme = ''
        espace = ''
        for group in self.app.db.keywords:
            
            if group['group'] == u'Thématique':
                for key in group['children']:
                    if key['id'] in self.item.keywords:
                        themes.append(key)
                        theme = key['name']
            elif group['group'] == u'Espace de la bibliothèque':
                for key in group['children']:
                    if key['id'] in self.item.keywords:
                        espaces.append(key)
                        espace = key['name']

        self.ids['theme'].text = theme.upper()
        self.ids['espace'].text = espace.upper()

        # Find main color in the image
        if self.item.filename is not None:
            cimg = CoreImage(self.item.filename, keep_data=True)
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
            self.color = (r,g,b,1)

    def change_text(self, but):
        buttons = [self.ids['resume'], self.ids['struct']]
        
        for button in buttons: 
            if button != but and button.state == 'normal' and but.state == 'normal':
                but.state = 'down'
                return
            if button != but:
                if but.state == 'normal':
                    button.state = 'down'
                else:
                    button.state = 'normal'

        maintext = self.ids['maintext']
        if maintext.text == self.item.description:
            maintext.text = self.item.description2
        else:
            maintext.text = self.item.description

    def close(self, but):
        self.parent.remove_widget(self)

class ScrollItem(Button):
    item = ObjectProperty(None)
    source = StringProperty('')
    app = ObjectProperty(None)
    popup = ObjectProperty(None)

    def open(self, *largs):
        if self.popup == None:
            self.popup = ContentPopup(
                item=self.item, 
                app=self.app,
                controler=self, 
                size_hint=(None,None))
            self.app.root_images.add_widget(self.popup)
        elif self.popup.parent is None:
            self.app.root_images.add_widget(self.popup)

        self.popup.center = (self.center_x, Window.center[1])
        self.app.panel.close_panel()
        
def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    
    app.should_display_images_by_default = True

    root.scroller = scroller = ScrollView( 
        size_hint=(None, None), 
        size=(1920, 1080),
        pos_hint={'center_x': .5, 'center_y': .5}, 
        do_scroll_x=False)
    root.add_widget(scroller)


    def rotate_window(but):
        but.background_color = bluergb
        but.children[0].color = (1,1,1,1)
        if Window.rotation == 180:
            Window.rotation = 0
        else:
            Window.rotation = 180

    def on_press_button(but):
        but.background_color = (1,1,1,1) 
        but.children[0].color = bluergb

    but = Button(
        size=               (72,71),
        size_hint=          (None,None),
        pos=                (Window.width - 72 + 10, Window.height/2 - 71/2),
        background_color=   bluergb,
        background_normal=  'widgets/picto-background.png',
        background_down=    'widgets/picto-background.png')
    
    img = Image(
        source='widgets/picto-reverse.png',
        size=(40,40),
        pos=(but.x + (but.width - 40)/2, but.y + (but.height -40)/2),
        color=(1,1,1,1)
        )
    but.add_widget(img)
    but.bind(on_press=on_press_button)
    but.bind(on_release=rotate_window)
   

    but2 = Button(
        size=               (72,71),
        size_hint=          (None,None),
        pos=                (0-10, Window.height/2 - 71/2),
        background_color=   bluergb,
        background_normal=  'widgets/picto-background.png',
        background_down=    'widgets/picto-background.png')
       
    img = Image(
        source='widgets/picto-reset.png',
        size=(40,40),
        pos=(but2.x + (but2.width - 40)/2, but2.y + (but2.height -40)/2),
        color=(1,1,1,1)
        )
    but2.add_widget(img)

    def add_buttons(dt):
        root.add_widget(but)
        root.add_widget(but2)
    Clock.schedule_once(add_buttons, .5)

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
    layout.bind(minimum_height=layout.setter('height'))

    scroller.add_widget(layout)


    panel = WidgetsPanel(app=app)
    app.panel = panel
    root.add_widget(panel)

    def clear_panel(but):        
        but.background_color = bluergb
        but.children[0].color = (1,1,1,1)
        panel.clear_panel() 
        app.root_images.clear_widgets() 
        panel.close_panel()  
    but2.bind(on_press=on_press_button)
    but2.bind(on_release=clear_panel)

    def feed_scroll(defs):
        source = defs['source']
        if source not in app.images_displayed:
            return
        current_images = [x.source for x in app.root.scroller.layout.children]
        if source in current_images:
            return

        item = ScrollItem(**defs)
        app.root.scroller.layout.add_widget(item)

    def my_show_objects(objects):
        self = app
        root = self.root
        selected_authors = self.author_widget.selected_keywords
        selected_titles = self.title_widget.selected_keywords
        # selected_titles = [x.upper() for x in selected_titles]

        for item in objects[:]:
            # Filtering authors and titles
            if item.nom not in selected_titles and len(selected_titles) > 0:
                objects.remove(item)
                continue

            if item.freefield not in selected_authors and len(selected_authors) > 0:
                objects.remove(item)
                continue

        panel.result_sentence.text = "J'ai trouvé [font=fonts/proximanova-bold-webfont.ttf][size=28]" + str(len(objects)) + " [/size][/font]livres!"
        
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

                    image = dict(source=filename, size_hint=(1,1), item=item, app=self)
                    images_to_add.append(image)
                    images_displayed.append(filename)
                self.images_displayed = images_displayed
                self.delayed_work(feed_scroll, images_to_add)

                # remove all the previous images
                for child in self.root.scroller.layout.children[:]:
                    for filename in images:
                        if filename == child.source:
                            self.root.scroller.layout.remove_widget(child)

    app.show_objects = my_show_objects

    app.trigger_objects_filtering()

    def on_touch_window(touch):
        return True

    # Window.on_touch_down = on_touch_window

    # def on_value(widget, value):
    #     print 'relou' , value
    # app.bind(items_to_add=on_value)

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

