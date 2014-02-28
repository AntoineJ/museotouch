#:kivy 1.8.0
# -*- coding: utf-8 -*-

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty

from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation

from museolib.widgets.imageitem import ImageItem
from museolib.widgets.basket import Basket
from museolib.widgets.slider import SizeSlider

from biinlib.keyboard.keyboard import Keyboard
from biinlib.keywordscrollview import KeywordScrollView, AttributeScrollView

from os.path import dirname,abspath, join


blue = '00a5a2'

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
            size=(450, 240), size_hint=(None, None))
        scatter = Scatter(size=slider.size,
                auto_bring_to_front=False,
                pos=(self.x, self.y - 240),
                size_hint=(None, None), rotation=-90,
                do_translate=False, do_rotate=False, do_scale=False)
        scatter.add_widget(slider)
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
            return

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

        self.dynamic_sentence.text = prefix_text + authors_text + themes_text + date_text
        

        self.dynamic_sentence.x = 30

        print self.dynamic_sentence.width
        if self.dynamic_sentence.width > 1200:
            Animation.stop_all(self.dynamic_sentence)
            anim = Animation(x=-self.dynamic_sentence.width - 30, d=5) + Animation(opacity=0, d=.1) + Animation(x=1300, d=0.1) + Animation(opacity=1, d=.1) + Animation(x=30, d=5)
            anim.repeat = True
            anim.start(self.dynamic_sentence)
            
            def anim_restart(dt):
                print 'restart'
                if self.dynamic_sentence.x < -1500:
                    self.dynamic_sentence.x = 1920
                Animation.stop_all(self.dynamic_sentence)
                anim = Animation(x=-self.dynamic_sentence.width, d=15)
                anim.on_complete=anim_restart
                anim.start(self.dynamic_sentence) 
            # anim_restart(None)


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

# En paramètre l'attribut db.items de app et un slug de champ à trouver
# A l'init parcours tous ces champs et les stocke et les affichent dans la liste
# Meme fonction que keywordScrollView pour l'input du clavier le filtre dans la scrollView (Faire une classe mère ?)
# Lorsqu'un label est sélectionné on recherche tous les items qui possèdent ce label et on les rajoutent à la fonction
# de filtre du main (A vérifier)
class FieldScrollView(ScrollView):
    pass

class ContentPopup(Scatter):
    item = ObjectProperty(None)
    controler = ObjectProperty(None)
    color = ListProperty([0,0,0,1])
    controler = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ContentPopup, self).__init__(**kwargs)

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

class ScrollItem(Button):
    item = ObjectProperty(None)
    source = StringProperty('')
    app = ObjectProperty(None)
    popup = ObjectProperty(None)

    def open(self, *largs):
        if self.popup == None:
            self.popup = ContentPopup(
                item=self.item, 
                controler=self, 
                size_hint=(None,None), 
                size=(800,800))
            self.app.root_images.add_widget(self.popup)
        elif self.popup.parent is None:
            self.app.root_images.add_widget(self.popup)

def feed_scroll(defs):
    # items = []
    # for i in range(30):
    #     item = ScrollItem(**defs)
    #     items.append(item)

    app = defs.pop('app')
    # for item in items:
    #     app.root.scroller.layout.add_widget(item)

    item = ScrollItem(**defs)
    app.root.scroller.layout.add_widget(item)

    # for i in range(30):
    #     btn = Button(text=str(i), 
    #                  size_hint=(None, None))
    #     app.root.scroller.layout.add_widget(btn)



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
    layout.bind(minimum_height=layout.setter('height'))

    scroller.add_widget(layout)


    panel = WidgetsPanel(app=app)
    root.add_widget(panel)

    def my_show_objects(objects):
        self = app
        root = self.root
        selected_authors = self.author_widget.selected_keywords
        selected_titles = self.title_widget.selected_keywords

        for item in objects[:]:
            # Filtering authors and titles
            if item.nom not in selected_titles and len(selected_titles) > 0:
                objects.remove(item)
                continue

            if item.freefield not in selected_authors and len(selected_authors) > 0:
                objects.remove(item)
                continue

        # for item in objects[:]:
        #     for i in range(30):
        #         objects.append(item)

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
                            # self.images_pos[filename] = {
                            #     'center': child.center,
                            #     'rotation': child.rotation }
                            self.root.scroller.layout.remove_widget(child)

    app.show_objects = my_show_objects

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

