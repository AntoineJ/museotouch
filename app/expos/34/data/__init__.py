from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.slider import SizeSlider
from museolib.widgets.basket import Basket
from kivy.utils import platform

from twisted.internet import reactor
from twisted.internet import protocol

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ListProperty, StringProperty, BooleanProperty 
from museolib.widgets.imagebuttons import ImageButtons 
from kivy.core.window import Window
from museolib.widgets.imageitem import ImageItem
from kivy.animation import Animation
from museolib.utils import no_url
from os.path import join, isfile, basename


clientList = []

class EchoProtocol(protocol.Protocol):
    
    def connectionMade(self):
        clientList.append(self)
        print 'client list : ', clientList

    def connectionLost(self, reason):
        clientList.remove(self)
        print 'client list removed : ', reason

    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        print response
        if response:
            print 'response self : ', self
            print 'transport : ', self.transport
            self.transport.write(response)

    def sendData(self, data):
        if data:
            self.transport.write(data)

class EchoFactory(protocol.Factory):
    protocol = EchoProtocol
    def __init__(self, app):
        self.app = app



#### IMAGE ITEM

greenColor = (0.22, 0.66, 0.2, 1)
greenWater = (0, 0.63, 0.6, 1)
blueColor = (0.11, 0.44, 0.72, 1)
orangeColor = (0.91, 0.30, 0.1, 1)

ImageItem.my_color = (1,0,1,1)
ImageItem.projection = StringProperty(None)

def my_on_start(self):
    # set the item color
    critere = self.item.keywords[0]

    if critere == '264':
        self.my_color = orangeColor
    elif critere == '265':
        self.my_color = greenWater
    elif critere == '267':
        self.my_color  = greenColor
    elif critere == '266':
        self.my_color = blueColor
    else:
        self.my_color = (0.29803921568627,0.69019607843137,0.9921568627451,1)

    #self.bg_img.color = self.my_color
    #self.btn_triangle1.color = self.my_color
    self.img_square.color = self.my_color

    #look for a video file :
    for elem in self.item['data']:
        if len(basename(elem['fichier'])) > 30:
            if elem['fichier'].endswith('jpg') or elem['fichier'].endswith('png'): 
                # self.projection = join(self.app.expo_dir, 'otherfiles', no_url(elem['fichier']))
                self.projection = basename(elem['fichier']).encode('utf-8')
                # if not isfile(self.projection):
                #     self.projection = None
                # else:
                #     break

ImageItem.on_start = my_on_start

def send_message(string):      
    if len(clientList) > 0:
        clientList[0].transport.write(string)
        print 'send_message ok, msg : ', string
    else:
        print 'no client, msg : ', string


def my_on_btn_more(self, *largs):
    if self.flip_front == True:
        new_rotation = 45
    else:
        new_rotation = 0

    anim = Animation(d=.3, rotation=new_rotation, t='out_quad')    
    Animation.stop_all(self.btn_more_cross, 'rotation')
    anim.start(self.btn_more_cross)
    
    # self.img_square.scale = 0.4
    print 'btn more', self.projection, self.flip_front
    if self.projection and self.flip_front == True: 
        print 'launching message'
        send_message(self.projection)
        send_message(',add')
    elif self.projection and self.flip_front == False:
        send_message(self.projection)
        send_message(',remove')
    self.flip()


ImageItem.on_btn_more = my_on_btn_more  

ImageItem.light = BooleanProperty(False)
def display_item(self):
    order=''
    # msg1 ='3f136432a5c1276654ed60779424cc3d.png'
    # msg2 = '7a8ac45322022038982ae07f3106961f.png'
    # msg = msg1
    if self.light:
        self.light = False
        order = ',remove'
    else:
        self.light = True
        order = ',add'

    print 'dislpay', self.light

    if self.projection:
        send_message(self.projection)
        # send_message(msg)
        send_message(order)

ImageItem.display_item = display_item
def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    # -------------------------------------------------------------------------
    # BACKGROUND
    # ------------------------------------------ 
    background = Image(source ='widgets/background.png', pos_hint={'center_x':.5, 'center_y':.5})
    root.add_widget(background)

    # -------------------------------------------------------------------------
    # SERVER CONNECTION
    # ------------------------------------------------------------------------- 
    factory = EchoFactory(app)
    server = reactor.listenTCP(8001, factory)
    # label = Label(text="server started\n", pos=(100,100))
    # root.add_widget(label)

    # button = Button(text='broadcast msg', width = 100, height = 30, size_hint= (None,None), pos = (300, 100))
    # button.bind(on_release=send_message)
    # root.add_widget(button)

    # -------------------------------------------------------------------------
    # Create a button to display help
    help_img = Button(background_normal="widgets/help_screen.png", background_down="widgets/help_screen.png", size=(1920,1080), size_hint=(1,1))
    app.help = BooleanProperty(False)

    def show_help(self, *largs):
        # print 'show help'
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
        size=(50,50),#(99,101),
        border=(0,0,0,0),
        #pos_hint={'x':25, 'y':25}
        x=25,
        y=15)
    helpButton.bind(on_release=show_help)
    root.add_widget(helpButton)
    help_img.bind(on_release=show_help)

    futur_img = Button(background_normal="widgets/background_temps.png", background_down="widgets/background_temps.png", size=(1920,1080), size_hint=(1,1))
    app.futur = BooleanProperty(False)

    def show_futur(self, *largs):
        if app.futur == False:
            app.root_images.parent.add_widget(futur_img)
            app.futur = True
        else:
            app.root_images.parent.remove_widget(futur_img)
            app.futur = False

    futurButton = Button(
        background_normal='widgets/btn_idee.png',
        background_down='widgets/btn_idee.png',
        size_hint=(None,None),
        size=(50,50),#(99,101),
        border=(0,0,0,0),
        #pos_hint={'x':25, 'y':25}
        x=1920 - 25 - 50,
        y=15)
    futurButton.bind(on_release=show_futur)
    root.add_widget(futurButton)
    futur_img.bind(on_release=show_futur)


    # -------------------------------------------------------------------------
    # Create an image map widget
    # Widget Mobile
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imageButtons = imageButtons = ImageButtons(
            size_hint=(None, None),
            size=(420, 420),
            sources=sources,
            suffix='_active',
            show_one_cat_only=True)
    scatter = scatter_imageButtons = Scatter(
            auto_bring_to_front=True,
            size=imageButtons.size,
            size_hint=(None, None), rotation=0, scale=1, do_scale=False,
            # pos_hint = {'center_x': .5, 'center_y':.5}
            x = Window.width/2 - imageButtons.width/2,
            y = Window.height/2 - imageButtons.height/2
            )
    img = Image(source = 'widgets/background_menu.png', size=(420,420))
    scatter.add_widget(img)
    scatter.add_widget(app.imageButtons)
    root.add_widget(scatter)

    def on_menu_change(self, active_ids):
        if len(active_ids) > 0:
            send_message('clear')
    app.imageButtons.bind(active_ids=on_menu_change)

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
    # if basket.active :
        #do not offer a basket on tablets, only on tables
        # if platform() not in ('android'):  
        #     root.add_widget(basket)

    # -------------------------------------------------------------------------

    return root

