from os.path import join
from kivy.uix.floatlayout import FloatLayout
from museolib.widgets.basket import Basket

# from twisted.internet import reactor
# from twisted.internet import protocol

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, BooleanProperty 
from kivy.core.window import Window
from museolib.widgets.imageitem import ImageItem
from kivy.uix.scatter import Scatter
from os.path import join, isfile, basename, split
from museolib.widgets.cicularkeywordpicker import CircularKeywordPicker
from kivy.uix.video import Video

from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS


#### IMAGE ITEM
def my_on_start(self):

    keyword =  self.item['keywords'][0]
    # Keyword 269 = Texte
    # Keyword 270 = Photo
    # Keyword 271 = Video

    if '269' in self.item['keywords']:
        self.container.remove_widget(self.img_square)
        self.scale=1

        self.container.remove_widget(self.scatter_date_photo)
        self.container.remove_widget(self.scatter_legende_photo)
        self.height = self.text_content_label.height*2

        self.text_content_label.texture_update()
        self.text_content_label.text = self.item['description'].replace('\r', '')
        self.height = self.text_content_label.height *0.6
        self.container.remove_widget(self.scatter_background_texte)
        self.container.remove_widget(self.video_buttons_layout)
        self.container.remove_widget(self.preview_button)
    elif '270' in self.item['keywords']:
        #adapt the item size to the image size
        self.size = self.img_square.texture_size
        self.container.remove_widget(self.text_content)   
        self.container.remove_widget(self.scatter_background_texte)
        self.container.remove_widget(self.video_buttons_layout)
        self.container.remove_widget(self.preview_button)
    elif '271' in self.item['keywords']:
        self.color = (1,1,1,.5)
        self.container.remove_widget(self.text_content)   
        self.container.remove_widget(self.scatter_background_texte)
        self.container.remove_widget(self.scatter_background_texte)
        self.container.remove_widget(self.scatter_date_photo)
        self.container.remove_widget(self.scatter_legende_photo)

        #look for a video file :
        for elem in self.item['data']:
                if elem['fichier'].endswith('mp4'):
                    video_filename = join(self.app.expo_dir, 'otherfiles', split(elem['fichier'])[1])
                    if not isfile(video_filename):
                        video_filename = None
                    else:
                        # self.color = (0,0,0,1)
                        self.size = (1280,720)
                        self.img_square.keep_ratio = False
                        self.img_square.allow_stretch = True
                        self.img_square.size = self.size
                        self.scale = 0.5
                        self.player = Video(source = video_filename, state='stop', options={'allow_stretch': True})
                        # , allow_fullscreen = False, image_stop= '', image_pause='')
                        self.container.add_widget(self.player, 1)
                        self.player.opacity = 0
                        
                        def mask_video_buttons():
                            self.video_buttons_layout.opacity = 0
                            self.video_buttons_layout.y = -100
                        mask_video_buttons()
                        def display_video_buttons():
                            self.video_buttons_layout.opacity = 1
                            self.video_buttons_layout.y = self.height/2-self.video_buttons_layout.height/2
                        def mask_preview_button():
                            self.preview_button.opacity = 0
                            self.preview_button.y = -100
                        def display_preview_button():
                            self.preview_button.opacity =1
                            self.preview_button.y =  self.height/2 - self.preview_button.height/2
                        def my_video_on_touch_down(touch):
                            if self.player.opacity == 1:
                                # if not self.collide_point(*touch.pos):
                                #     print 'no collide point'
                                #     return False
                                if touch.is_double_tap:
                                    # set_video_to_fullscreen()
                                    if self.player.state == 'play':
                                        self.player.state = 'pause'
                                        # self.video_buttons_layout.opacity = 1
                                    return True
                                # return super(Video, self).on_touch_down(touch)

                        self.player.on_touch_down = my_video_on_touch_down

                        def on_state(instance, value):
                            print 'on state ', value, self.player.eos
                            if value == 'play':
                                self.player.opacity = 1
                                mask_video_buttons()
                                mask_preview_button()
                            elif value == 'pause':
                                display_video_buttons()
                                self.video_buttons_layout.opacity = 1
                            elif value == 'stop':
                                self.player.seek(0)
                                self.player.opacity = 0 
                                mask_video_buttons()     
                                display_preview_button()           
                            else:
                                print 'whatever'

                        self.player.bind(state=on_state)

ImageItem.on_start = my_on_start

def on_play_button(self, *largs):
    if hasattr(self, 'player'):
        # self.player.opacity = 1
        self.player.state = 'play'
        # self.video_buttons_layout.opacity = 0

def on_stop_button(self, *largs):
    if hasattr(self, 'player'):
        self.player.state = 'stop'
        # on_play_button(self, None)

ImageItem.on_stop_button =  on_stop_button
ImageItem.on_play_button = on_play_button

class EchoServerProtocol(WebSocketServerProtocol):
 
   def onMessage(self, msg, binary):
      self.sendMessage(msg, binary)
      print 'message received'

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    # -------------------------------------------------------------------------
    # BACKGROUND
    # ------------------------------------------ 
    Window.clearcolor=(0.79607843137255,0.79607843137255,0.79607843137255,1)

    # # -------------------------------------------------------------------------
    # # Create an image map widget
    # # Widget Mobile
    # sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    # sources = [x for x in sources if '_active' not in x]
    # app.imageButtons = imageButtons = ImageButtons(
    #         size_hint=(None, None),
    #         size=(420, 420),
    #         sources=sources,
    #         suffix='_active',
    #         show_one_cat_only=True)
    # scatter = scatter_imageButtons = Scatter(
    #         auto_bring_to_front=True,
    #         size=imageButtons.size,
    #         size_hint=(None, None), rotation=0, scale=1, do_scale=False,
    #         # pos_hint = {'center_x': .5, 'center_y':.5}
    #         x = Window.width/2 - imageButtons.width/2,
    #         y = Window.height/2 - imageButtons.height/2
    #         )
    # img = Image(source = 'widgets/background_menu.png', size=(420,420))
    # scatter.add_widget(img)
    # scatter.add_widget(app.imageButtons)
    # root.add_widget(scatter)

    # def on_menu_change(self, active_ids):
    #     if len(active_ids) > 0:
    #         send_message('clear')
    # app.imageButtons.bind(active_ids=on_menu_change)

    def trigger_objects_filtering(self, ids):
        # start from all items
        items = app.db.items
        key = ids
        items_result = []
        
        if key:
            for item in items:
                if key in item.keywords:
                    items_result.append(item) 

        items = items_result

        app.show_objects(items)


    keywordPicker = CircularKeywordPicker(  
        size_hint=(None,None),
        size=(300,300), 
        outer_radius=300,
        inner_radius=220,
        # pos_hint= ({'x':-200, 'y':-200})
        )
    scatter = scatter_keywordpicker = Scatter (
        auto_bring_to_front= True ,
        size=keywordPicker.size,
        size_hint=(None,None),
        rotation = 0,
        scale = 1,
        do_rotation=False,
        do_scale=False,
        do_translation = False,
        pos_hint= {'center_y':.5},
        x= Window.width - keywordPicker.width/1.5
        # center_x = Window.width/2
        )
    scatter.add_widget(keywordPicker)
    root.add_widget(scatter)
    
    keywordPicker.bind(active_ids=trigger_objects_filtering)

    keywordPicker.keywords = [app.db.keywords[1]] # Just the date group

    keywordPicker.go_to_angle(6, 1)
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
    # -------------------------------------------------------------------------

    factory = WebSocketServerFactory("ws://localhost:9000") 
    factory.protocol = EchoServerProtocol
    listenWS(factory)

    return root

