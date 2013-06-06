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
from museolib.widgets.keywords import Keywords
from museolib.widgets.basket import Basket
from museolib.widgets.circularslider import CircularSlider

from museolib.widgets.imageitem import ImageItem
from kivy.properties import BooleanProperty
from kivy.uix.videoplayer import VideoPlayer
from museolib.utils import no_url
from os.path import join, isfile
from kivy.core.window import Window
from kivy.clock import Clock
from museolib.widgets.calendar import CalendarSlider
from datetime import datetime, timedelta
from museolib.utils import send_mail
import re
import csv
from kivy.properties import ObjectProperty
from kivy.graphics import RenderContext, Color, Rectangle, BindTexture

from kivy.utils import platform
from kivy.animation import Animation

########## EXPO SAINT ETIENNE


#### UTIL

ORANGE = (0.93333333333333, 0.49803921568627, 0, 1)
YELLOW = (1, 0.92941176470588, 0, 1)
BLUE = (0, 0.67450980392157, 0.71372549019608, 1)
GREEN = (0.04705882352941, 0.49019607843137, 0.24313725490196, 1)
GREENLIGHT = (0.5921568627451, 0.74901960784314, 0.05098039215686, 1)
PINK = (0.91372549019608, 0.37647058823529, 0.50980392156863, 1)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

FNAME = "expos/29/mails.csv"

def squarize_img(img):
    # Rognage => maximum square :
    my_ceil = lambda n: 0 if n < 0 else n
    L,H = img.texture.size
    x = my_ceil(L-H)/2
    y = my_ceil(H-L)/2
    w = min(L,H)
    h = min(L,H)
    #import pdb; pdb.set_trace()
    img.texture = img.texture.get_region(x, y, w, h)

#### IMAGE ITEM

ImageItem.my_color = (1,0,1,1)
ImageItem.emailMode = False
ImageItem.images = ObjectProperty()

def my_on_start(self):
    # set the item color
    critere = self.item['orig_geo']

    if critere == 'decouvre':
        self.my_color = PINK
    elif critere == 'deplace':
        self.my_color = GREENLIGHT
    elif critere == 'habite':
        self.my_color = BLUE
    elif critere == 'sors':
        self.my_color  = ORANGE
    elif critere == 'sport':
        self.my_color = GREEN
    elif critere == 'travaille':
        self.my_color = YELLOW
    else:
        self.my_color = (1,1,1,1)

    self.bg_img.color = self.my_color
    self.btn_triangle1.color = self.my_color
    #self.btn_triangle2.color = self.my_color

    #look for a secondary files (only images) to navigate between images in a gallery
    i = 1
    self.images = []
    self.images.append(self.source) # append the main image
    for elem in self.item['data']:
        filename = join(self.app.expo_dir, 'otherfiles', no_url(elem['fichier']))
        if isfile(filename):
            # img = Image(source = filename, pos=(512*i, 0))
            # squarize_img(img)
            self.images.append(filename)
            # self.gallery.add_widget(img)
            i = i+1
            # print img.x
    if i == 1:
        self.galleryLeft.x = self.galleryLeft.x - 50
        self.galleryRight.x = self.galleryRight.x + 50

ImageItem.on_start = my_on_start

def my_on_btn_more(self, *largs):
    if not self.isPlayingVideo:
        if self.isLoupe:
            self.on_zoom()
        if self.emailMode:
            self.share_item()
        #new_rotation = -45 if self.btn_more_cross.rotation == 0 else 0
        if self.flip_front == True:
            new_rotation = 45
        else:
            new_rotation = 0

        anim = Animation(d=.3, rotation=new_rotation, t='out_quad')    
        Animation.stop_all(self.btn_more_cross, 'rotation')
        anim.start(self.btn_more_cross)

        self.flip()

ImageItem.on_btn_more = my_on_btn_more                  
    
ImageItem.isLoupe = BooleanProperty(False)

def my_on_btn_zoom(self, *largs):
    if not self.isPlayingVideo:
        if not self.flip_front:
            self.on_btn_more(None)
        if self.emailMode:
            self.share_item()
        if self.scale < 1:
            Animation(t='out_quad', d=0.3, scale = 1.).start(self)
        if self.isLoupe == True:
            self.isLoupe = False
        else:
            self.isLoupe = True

ImageItem.on_zoom = my_on_btn_zoom

ImageItem.isPlayingVideo = BooleanProperty(False)
def on_btn_play(self, *largs):
    if hasattr(self, 'video') and self.video: 
        print 'video found'
        self.player = VideoPlayer(source=self.video, play = True, allow_fullscreen=False, options={'allow_stretch': True})
        self.player.size = 512,512
        self.container.add_widget(self.player) 
        self.flip()
        self.btn_more_cross.rotation = 0
        self.isPlayingVideo = True

ImageItem.on_btn_play = on_btn_play


def on_stop_video(self, *largs):
    
    if self.isPlayingVideo == True:
        print 'stop video'
        self.player.play = False
        self.flip()
        self.container.remove_widget(self.player)
        self.player = None
        self.isPlayingVideo = False

ImageItem.on_stop_video = on_stop_video

def on_share_item(self, *largs):
    animUp = Animation(y=10, duration=0.2)
    animDown = Animation(y=-303, duration=0.2)

    if not self.emailMode:
        animUp.start(self.email_form)
        animDown.start(self.share_button)
        self.emailMode = True
    else:
        animUp.start(self.share_button)
        animDown.start(self.email_form)
        self.email1.text = 'Email emetteur'
        self.email2.text = 'Email destinataire'
        self.emailMode = False
        self.email1.focus= False
        self.email2.focus= False

ImageItem.share_item = on_share_item

def shake_email_form(self):
    anim = Animation(x=self.email_form.x + 5, duration=.05) + Animation(x = self.email_form.x -5, duration=.1) + Animation(x= self.email_form.x, duration=.05)
    anim.start(self.email_form)

def on_check_email_form(self, *largs):
    if not EMAIL_REGEX.match(self.email1.text):
        shake_email_form(self)
        return
    elif not EMAIL_REGEX.match(self.email2.text):
        shake_email_form(self)
        return
    else: # both email valid
        send_mail(items=[self.item], email_to=self.email2.text, email_from=self.email1.text)
        try:
            mail_file = open(FNAME, "a")
            writer = csv.writer(mail_file, quoting=csv.QUOTE_MINIMAL)
            content =  self.email1.text
            writer.writerow([content])
        finally:
            mail_file.close()

        on_share_item(self, None)

ImageItem.check_email_form = on_check_email_form

def on_leave_focus_1(self, *largs):
    if self.email1.focus:
        self.email2.focus = False
        self.email1.text = ''

ImageItem.leave_focus_1 = on_leave_focus_1

def on_leave_focus_2(self, *largs):
    if self.email2.focus:
        self.email1.focus = False
        self.email2.text = ''

ImageItem.leave_focus_2 = on_leave_focus_2

def on_next_img(self, *largs):
    currentIndex = self.images.index(self.img_square.source)
    if currentIndex != len(self.images) - 1:
        nextSource = self.images[currentIndex+1]
        nextIndex = currentIndex+1
    else:
        nextSource = self.images[0]
        nextIndex = 0
    
    self.img_square.source = nextSource
    self.img_square.reload()
    squarize_img(self.img_square)


ImageItem.display_next_img = on_next_img

def on_prev_img(self, *largs):
    currentIndex = self.images.index(self.img_square.source)
    if currentIndex != 0:
        prevIndex = currentIndex-1
        nextSource = self.images[prevIndex]
    else:
        prevIndex = len(self.images)-1
        nextSource = self.images[prevIndex]

    print 'nextSource : ', nextSource
    self.img_square.source = nextSource
    self.img_square.reload()
    squarize_img(self.img_square)

ImageItem.display_prev_img = on_prev_img
def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    root.square_items = True
    app.gameMode = False

    # FNAME = join(self.app.expo_dir, "mails.csv")
    mail_file = open(FNAME, "a")
    try:
        writer = csv.writer(mail_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["antoine@biin.fr"])
    finally:
        mail_file.close()

    # Window.clearcolor = (0.556862745, 0.780392157, 0.243137255,1)

    # -------------------------------------------------------------------------
    # Image 
    background = Image(source ='widgets/background.jpg', pos_hint={'center_x':.5, 'center_y':.5})
    root.add_widget(background)

    # -------------------------------------------------------------------------
    # Create an image map widget
    # Widget Mobile
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            size_hint=(None, None),
            size=(350, 350),
            sources=sources,
            suffix='_active')
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=True,
            size=imagemap.size,
            size_hint=(None, None), rotation=0, scale=1, do_scale=False,
            y= Window.height-350
            )
    img = Image(source = 'widgets/background_map.png', size=(350,350))
    scatter.add_widget(img)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)


    # Create an image Button
    # Carte de Saint Etienne
    sources = glob(join(app.expo_data_dir, 'widgets', 'carte', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imageButtons = imageButtons = ImageButtons(
                                                   size_hint=(None, None),
                                                   size=(616, 1080),
                                                   sources=sources,
                                                   suffix='_active',
                                                   show_objects_when_empty=True)

    scatter = scatter_imageButtons = Scatter(
                                             auto_bring_to_front=False,
                                             size=imageButtons.size,
                                             size_hint=(None, None), rotation=0, scale=1,
                                             pos_hint={'center_x':.84, 'center_y': .5},
                                             do_translation=False, do_rotation=False, do_scale=False)
    
    scatter.add_widget(app.imageButtons)
    root.add_widget(scatter, index=0)

    # -------------------------------------------------------------------------
    # Create a button to order all the items by datation
    kwargs = {'size_hint': (None, None), 'size': (41, 41),
            'border': (0, 0, 0, 0)}
    ordering_datation = Button(
            background_normal='widgets/btn_ranger.png',
            background_down='widgets/btn_ranger.png',
            x=41 +2, y=0,
            **kwargs)
    def order_datation(*largs):
        for item in app.root_images.children:
            if item.emailMode == True:
                item.share_item()
        app.do_ordering_datation()
    ordering_datation.bind(on_release=order_datation)
    root.add_widget(ordering_datation)

    ordering_datation2 = Button(
            background_normal='widgets/btn_ranger.png',
            background_down='widgets/btn_ranger.png',
            x=Window.width-41*2 - 2,
            y=Window.height-41,
            **kwargs)
    ordering_datation2.bind(on_release=app.do_ordering_datation)
    root.add_widget(ordering_datation2)

    # -------------------------------------------------------------------------
    # Create a button to display help
    help_img = Image(source="widgets/help_screen.png", size=(1920,1080))
    app.help = BooleanProperty(False)

    def show_help(self, *largs):
        if app.help == False:
            app.root_images.parent.add_widget(help_img)
            app.help = True
        else:
            app.root_images.parent.remove_widget(help_img)
            app.help = False
        
    helpButton = Button(
        background_normal='widgets/btn_help.png',
        background_down='widgets/btn_help.png',
        size_hint=(None,None),
        size=(41,41),
        border=(0,0,0,0))
    helpButton.bind(on_release=show_help)
    root.add_widget(helpButton)

    helpButton2 = Button(
        background_normal='widgets/btn_help_revers.png',
        background_down='widgets/btn_help_revers.png',
        size_hint=(None,None),
        size=(41,41),
        border=(0,0,0,0),
        x=Window.width-41, 
        y=Window.height-41)
    helpButton2.bind(on_release=show_help)
    root.add_widget(helpButton2)

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

