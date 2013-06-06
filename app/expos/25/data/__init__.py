from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label 
from kivy.uix.image import Image
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.imagebuttons import ImageButtons 
from museolib.widgets.basket import Basket
from museolib.widgets.circularslider import CircularSlider

from museolib.widgets.imageitem import ImageItem
from kivy.uix.videoplayer import VideoPlayer
from museolib.utils import no_url
from os.path import join, isfile
from kivy.core.window import Window
from kivy.clock import Clock
from museolib.widgets.calendar import CalendarSlider
from datetime import datetime, timedelta
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from museolib.widgets.gridkeywords import GridKeywords, GridKeywordsGroup

from kivy.utils import platform
from kivy.animation import Animation


#### IMAGE ITEM

redColor = (0.929411765, 0.109803922, 0.141176471, 1)
greenColor = (0, 0.650980392, 0.31372549, 1)
blueColor = (0, 0.654901961, 0.619607843, 1)
orangeColor = (0.945098039, 0.352941176, 0.160784314, 1)
purpleColor = (0.619607843, 0.145098039, 0.388235294, 1)

# print ImageItem.item['orig_geo']

ImageItem.my_color = (1,0,1,1)

def my_on_start(self):
    # set the item color
    critere = self.item['orig_geo']

    if critere == 'star':
        self.my_color = redColor
    elif critere == 'techniques':
        self.my_color = blueColor
    elif critere == 'chiffres':
        self.my_color = greenColor
    elif critere == 'secrets':
        self.my_color  = orangeColor
    elif critere == 'dates':
        self.my_color = purpleColor
    else:
        self.my_color = (0.29803921568627,0.69019607843137,0.9921568627451,1)

    self.bg_img.color = self.my_color
    self.btn_triangle1.color = self.my_color
    self.btn_triangle2.color = self.my_color

    #look for a video file :
    for elem in self.item['data']:
            if elem['fichier'].endswith('wmv'):
                self.video = join(self.app.expo_dir, 'otherfiles', no_url(elem['fichier']))
                if not isfile(self.video):
                    self.video = None
                else:
                    break

ImageItem.on_start = my_on_start

def my_on_btn_more(self, *largs):
    if not self.isPlayingVideo:
        if self.isLoupe:
            self.on_zoom()
        #new_rotation = -45 if self.btn_more_cross.rotation == 0 else 0
        if self.flip_front == True:
            new_rotation = 45
        else:
            new_rotation = 0

        anim = Animation(d=.3, rotation=new_rotation, t='out_quad')    
        Animation.stop_all(self.btn_more_cross, 'rotation')
        anim.start(self.btn_more_cross)
        
        # self.img_square.scale = 0.4
        self.flip()

ImageItem.on_btn_more = my_on_btn_more                  
    
ImageItem.isLoupe = BooleanProperty(False)

def my_on_btn_zoom(self, *largs):
    if not self.isPlayingVideo:
        if not self.flip_front:
            self.on_btn_more(None)
        if self.scale < 1:
            Animation(t='out_quad', d=0.3, scale = 1.).start(self)
        if self.isLoupe == True:
            my_ceil = lambda n: 0 if n < 0 else n
            L,H = self.img_square.texture.size
            x = my_ceil(L-H)/2
            y = my_ceil(H-L)/2
            w = min(L,H)
            h = min(L,H)
            self.img_square.texture = self.img_square.texture.get_region(x, y, w, h)
            self.isLoupe = False
        else:
            self.img_square.reload()    
            self.isLoupe = True

ImageItem.on_zoom = my_on_btn_zoom

ImageItem.isPlayingVideo = BooleanProperty(False)
def on_btn_play(self, *largs):
    if hasattr(self, 'video') and self.video: 
        self.player = VideoPlayer(source=self.video, play = True, allow_fullscreen=False, options={'allow_stretch': True})
        self.player.size = 512,512
        self.container.add_widget(self.player) 
        self.flip()
        self.btn_more_cross.rotation = 0
        self.isPlayingVideo = True

ImageItem.on_btn_play = on_btn_play


def on_stop_video(self, *largs):
    
    if self.isPlayingVideo == True:
        self.player.play = False
        # self.video = None
        self.flip()
        self.container.remove_widget(self.player)
        self.player = None
        self.isPlayingVideo = False

ImageItem.on_stop_video = on_stop_video

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    root.square_items = True
    app.gameMode = False
    # Window.clearcolor = (0.556862745, 0.780392157, 0.243137255,1)

    app.db_game = [] # custom dababase for game items
    # Look for game items, remove them from expo, keep them for game mode
    def separate_game_items(*largs):
        for item in app.db.items:
            if 'orig_geo_prec' in item:
                if item['orig_geo_prec'] != 'non':
                    app.db_game.append(item)
                    app.db.items.remove(item)
    Clock.schedule_once(separate_game_items, -1)

    # -------------------------------------------------------------------------
    # Image 
    background = Image(source ='widgets/background_global.jpg', pos_hint={'center_x':.5, 'center_y':.5})
    root.add_widget(background)

    background_game = Image(source ='widgets/background-jeu.jpg', pos_hint={'x':-1})
    root.add_widget(background_game)
    # -------------------------------------------------------------------------
    # Create calendar slider

    mul = CalendarSlider(pos_hint={'y':0, 'center_x':0.5}, display=['days'])
    mul.days_begin = datetime(1890, 8, 15, 20, 0, 0)  # year can't be < 1
    mul.days_end = datetime(2010, 8, 19, 4, 0, 0)
    mul.adjust_slider('days', 135, 20) # rognage de 196 pixels, decalage vers la droite de 8
    root.add_widget(mul, index=0)
    app.calendar = mul

    # -------------------------------------------------------------------------
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            size_hint=(None, None),
            size=(540, 153),
            sources=sources,
            suffix='_active',
            show_one_cat_only=True)
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=False,
            size=imagemap.size,
            size_hint=(None, None), rotation=0, scale=1,
            pos_hint={'center_x': 0.5, 'center_y': 0.11},
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)
    
    def on_menu_change(self, active_ids):
        if len(active_ids) > 0:
            def move_root_images_and_items(*largs):
                if app.items_to_add == 0:
                    app.do_ordering_datation()
                    Clock.unschedule(move_root_images_and_items)
            Clock.schedule_interval(move_root_images_and_items, 0.5)
    app.imagemap.bind(active_ids=on_menu_change)

    # -------------------------------------------------------------------------
    # Create a widget for keywords in the game interface
    # Here we are using a scatter between to be able to rotate the widget
    img = Image(source='widgets/titre_jeu.png', 
        size=(442, 124),
        pos_hint={'center_x':-0.185, 'center_y':0.88},
        auto_bring_to_front=True )
    root.add_widget(img)

    app.gridkeywords = gridkeywords = GridKeywords(
            size=(600, 700),
            size_hint=(None, None),
            orientation='vertical',
            title_template='KeywordItemTitle')
    scatter = scatter_keywords = Scatter(size=gridkeywords.size,
            auto_bring_to_front=True,
            pos_hint={'center_x': -0.185, 'center_y': 0.45},
            size_hint=(None, None), rotation=0,
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(gridkeywords)
    root.add_widget(scatter)
    
    def update_objects_from_game_filter(self, *largs):
        if app.gridkeywords and app.gridkeywords.selected_keywords:
            selected_keywords = app.gridkeywords.selected_keywords
            groups = list(set([x[0] for x in selected_keywords]))
            result = []
            removeItems = []
            for item in app.db_game:
                result.append(item)

            for group in groups:
                keywords = [x[1] for x in selected_keywords if x[0] == group]
                for item in result:
                    key = keywords[0]
                    remove = True
                    if key in item.keywords:
                        remove = False

                    if remove == True:
                        removeItems.append(item)

            for item in removeItems:
                if item in result:
                    result.remove(item)
        if isinstance(app.root_images.x, (int, long)):
            if len(app.gridkeywords.selected_keywords) == 0:
                result = app.db_game          
	    app.show_objects(result)    

            def move_root_images_and_items(*largs):
                if app.items_to_add == 0:
                    app.root_images.x = 0
                    do_ordering_datation()
                    Clock.unschedule(move_root_images_and_items)
            Clock.schedule_interval(move_root_images_and_items, 0.5)

    # create trigger for updating objects
    trigger_game_filtering = Clock.create_trigger(
            update_objects_from_game_filter, 0)

    gridkeywords.keywords = app.db.keywords
    gridkeywords.bind(selected_keywords = trigger_game_filtering)

    # -------------------------------------------------------------------------
    # Create a button to order all the items by datation
    def order_items(*largs):
        if app.gameMode:
            do_ordering_datation()
        else:
            app.do_ordering_datation()
    kwargs = {'size_hint': (None, None), 'size': (41, 41),
            'border': (0, 0, 0, 0), 'x':0, 'y':(Window.height-41)}
    ordering_datation = Button(
            background_normal='widgets/btn_ranger.png',
            background_down='widgets/btn_ranger.png',
            **kwargs)
    ordering_datation.bind(on_release=order_items)
    root.add_widget(ordering_datation)


    # -------------------------------------------------------------------------
    # Create a button to display help
    #help_img = Image(source="widgets/help_screen.png", size=(1920,1080))
    help_img = Button(background_normal="widgets/help_screen.png", background_down="widgets/help_screen.png", size=(1920,1080))
    
    app.help = BooleanProperty(False)

    def show_help(self, *largs):
        if not app.gameMode:
            if app.help == False:
                app.root_images.parent.add_widget(help_img)
                app.help = True
            else:
                app.root_images.parent.remove_widget(help_img)
                app.help = False

    help_img.bind(on_release=show_help)
        
    helpButton = Button(
        background_normal='widgets/btn_help.png',
        background_down='widgets/btn_help.png',
        size_hint=(None,None),
        size=(41,41),
        border=(0,0,0,0),
        pos_hint={'x':0, 'y':0})
    # helpButton.bind(on_release=app.do_reset_item_position)
    helpButton.bind(on_release=show_help)
    root.add_widget(helpButton)


    # -------------------------------------------------------------------------
    ########### RESET ALL THE WIDGETS AND CLEAR ITEMS
    # -------------------------------------------------------------------------
    def reset_widgets(*largs):
        if app.gameMode == False:
            while len(app.imagemap.active_ids) != 0:
                app.imagemap.active_ids.pop()
            for child in app.imagemap.children:
                child.source = child.source_original
                child.active = False
            app.calendar.slider_d.value_min = 0
            app.calendar.slider_d.value_max = 1
        else:
            while len(app.gridkeywords.selected_keywords) != 0:
                for group in app.gridkeywords.selected_keywords:
                    for child in group[0].children[0].children:
                        child.state = 'normal'
                        child.selected = not child.selected

        
        
    resetButton = Button(
        background_normal='widgets/btn_init.jpg',
        background_down='widgets/btn_init.jpg',
        size_hint=(None,None),
        size=(41,41),
        border=(0,0,0,0),
        pos=(Window.width - 41, Window.height - 41))
    resetButton.bind(on_release=reset_widgets)
    root.add_widget(resetButton)

    # -------------------------------------------------------------------------
    # Create ticket button to switch expo/game mode

    root.ticketContact = False
    #First contact
    def on_ticket_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        root.ticketContact = True
        return True

    #on contact movement
    def on_ticket_move(self, touch):
        if touch.grab_current is self:
            root.x = root.x + touch.dx
            app.root_images.x = app.root_images.x + touch.dx
            for i, item in enumerate(reversed(app.root_images.children)):
                item.x = item.x + touch.dx
        return True

    def do_ordering_datation():
        children = app.root_images.children[:]
        children.sort(key=lambda x: x.item.date)
        display_ordering_as_table(children)

    def display_ordering_as_table(children):
        # remove and readd all children
        app.root_images.clear_widgets()
        for item in reversed(children):
            app.root_images.add_widget(item)

        cx, cy = app.root_images.center

        # size of image
        imgs = int(512 * .5) - 5

        # size of area for work
        width = app.root_images.width - 800
        height = app.root_images.height - 200

        # images per size
        mx = 1 + width // imgs
        my = 1 + height // imgs

        xoffset = 310
        yoffset = 90
        # initial position
        x = app.root_images.center_x - xoffset - (mx * imgs) / 2 
        y = app.root_images.center_y - yoffset + (my * imgs) / 2 - imgs

        # XXX make it configurable, this is to prevent overlap with map widget
        y += 80

        # direction
        dx = 1
        dy = -1

        for i, item in enumerate(children):
            mi = i % (mx * my)
            ix = x + (mi % mx) * imgs * dx
            iy = y + (mi // mx) * imgs * dy
            item.flip_front=True
            (Animation(d=0.1 + i / 30.) + Animation(scale=item.scale_min, pos=(ix, iy),
                    rotation=0., t='out_quad',
                    d=.25)).start(item)

    # on release
    def on_ticket_up(self, touch):
       
        def move_items_to_game_mode( *largs):
            reset_widgets(None)
            app.root_images.x = 0
            items = app.db_game
	    if isinstance(app.root_images.x, (int, long)):
                app.show_objects(items)
            # for i, item in enumerate(reversed(app.root_images.children)):
            def move_root_images_and_items(*largs):
                if app.items_to_add == 0:
                    do_ordering_datation()
                    Clock.unschedule(move_root_images_and_items)
            Clock.schedule_interval(move_root_images_and_items, 0.5)

        def move_items_to_expo_mode(*largs):
            app.root_images.x = 0
            app.update_objects_from_filter()
            app.do_reset_item_position()
            def move_root_images_and_items(*largs):
                if app.items_to_add == 0:
                    app.do_ordering_datation()
                    Clock.unschedule(move_root_images_and_items)
            Clock.schedule_interval(move_root_images_and_items, 0.5)

        def open_game_mode(duration = 0.5):
            separate_game_items()
            anim = Animation(x=1920, duration = 0.5)
            anim.start(root)
            anim2 = Animation(x=1920, duration=0.5)
            anim2.start(app.root_images)
            anim2.on_complete = move_items_to_game_mode
            if app.help:
                show_help(None)
            for i, item in enumerate(reversed(app.root_images.children)):
                anim3 = Animation(x=item.x + (1920-root.x), duration=0.5)
                anim3.start(item)
                if item.isPlayingVideo == True:
                    item.on_stop_video()
                if not item.flip_front:
                    item.on_btn_more()

        def open_expo_mode(duration = 0.5):
            anim = Animation(x=0, duration = 0.5)
            anim.start(root)
            anim2 = Animation(x=-1920, duration=0.5)
            anim2.start(app.root_images)
            anim2.on_complete = move_items_to_expo_mode
            for i, item in enumerate(reversed(app.root_images.children)):
                anim3 = Animation(x=item.x - (1920 - app.root_images.x) , duration=0.5)
                anim3.start(item)

        def return_to_expo_mode(duration = 0.2):
            anim = Animation(x=0, duration=0.2)
            anim.start(root)
            anim2 = Animation(x=0, duration=0.2)
            anim2.start(app.root_images)
            for i, item in enumerate(reversed(app.root_images.children)):
                anim3 = Animation(x=item.x-root.x, duration=0.2)
                anim3.start(item)

        def return_to_game_mode(duration = 0.2):
            anim = Animation(x=1920, duration = 0.2)
            anim.start(root)
            anim2 = Animation(x=0, duration=0.2)
            anim2.start(app.root_images)
            for i, item in enumerate(reversed(app.root_images.children)):
                # anim3 = Animation(x=item.x + (1920-root.x), duration=0.2)
                anim3 = Animation(x=(item.x - app.root_images.x), duration=0.2)
                anim3.start(item)

        if touch.grab_current is self and root.ticketContact == True:
            if app.gameMode == False:
                if touch.dx > 0:
                    open_game_mode()
                    app.gameMode = True
                else:
                    return_to_expo_mode()
            else:
                #GAME MODE
                if touch.dx < 0:
                    open_expo_mode()
                    app.gameMode = False
                else:
                    return_to_game_mode()
            touch.ungrab(self)
            root.ticketContact = False

        return True

    #create a button to switch in game mode
    gameButton = Image(
        source='widgets/ticket.png',
        size_hint=(None,None),
        size=(141, 49))
    scatter_ticket = Scatter(size=(141,49),
        auto_bring_to_front=False,
        pos_hint={'x':-0.031, 'center_y':0.5},
        size_hint=(None,None), rotation=0,
        do_translation=False, do_rotation=False, do_scale=False)
    scatter_ticket.add_widget(gameButton)
    root.add_widget(scatter_ticket, 0)

    scatter_ticket.bind(on_touch_move=on_ticket_move)
    scatter_ticket.bind(on_touch_down=on_ticket_down)
    scatter_ticket.bind(on_touch_up=on_ticket_up)   

    original_ticket_x = gameButton.x
    #ticket animation
    anim = Animation(x= original_ticket_x + 5, duration=.2, transition= 'in_out_cubic') + Animation(x= original_ticket_x - 5, duration=.2, transition='in_out_cubic' )
    def anim_ticket(dt):
        anim.start(gameButton)

    # call anim_ticket every 0.5 seconds
    # Clock.schedule_interval(anim_ticket, 2)

    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1, 'top': 1},'size_hint': (None, None), 'size': (100, 100),
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
    # -------------------------------------------------------------------------
    return root

