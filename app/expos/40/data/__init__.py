from os.path import join
from glob import glob

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, NumericProperty, ListProperty
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.vector import Vector
from kivy.clock import Clock

from kivy.core.image import Image as CoreImage

from museolib.widgets.imagemap import ImageMap
from museolib.widgets.basket import Basket
from museolib.widgets.imageitem import ImageItem

import random

from kivy.utils import platform

ImageItem.description = StringProperty('')
ImageItem.name = StringProperty('')
ImageItem.copyright = StringProperty('')
ImageItem.subtitle = StringProperty('')
ImageItem.text = StringProperty('')

ImageItem.english = BooleanProperty(False)

def my_on_start(self):     
    if self.app.expo_id == '40':
        self.size = self.img_square.size

        if self.english:
            endict = self.item['english']
            if 'nom' in endict:
                self.name = endict['nom']
            if 'freefield' in endict:
                self.subtitle = endict['freefield']
            if 'orig_geo_prec' in endict:
                self.copyright = endict['orig_geo_prec']
            if 'description' in endict:
                self.description = endict['description'].replace('\r', '')
        else:
            self.description = self.item.description.replace('\r', '')
            self.name = self.item['nom']
            self.subtitle = self.item['freefield']
            self.copyright = self.item['orig_geo_prec']
        self.text = self.description + self.name + self.subtitle + self.copyright

        self.height += self.text_content_label.height
        self.y -= self.text_content_label.height

ImageItem.on_start = my_on_start  

def my_on_close(self):
    def do_remove(dt):
        if self in self.glass.image_items:
            self.glass.image_items.remove(self)
        if self.parent:
            self.parent.remove_widget(self)

    anim = Animation(scale=.01, d=.1, t='out_cubic')
    anim.on_complete = do_remove
    anim.start(self)

ImageItem.on_close = my_on_close

class GlassButton(Button):
    color = ObjectProperty((1,1,1,1))
    item = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GlassButton, self).__init__(**kwargs)

    def on_state(self, button, state ):
        if state == 'down':
            self.background_color = self.color
        else:
            self.background_color = (1,1,1,1)

class Glass(Scatter):
    background_img = StringProperty('')
    glass_img = StringProperty('')
    disabled = BooleanProperty(False)
    app = ObjectProperty(None)

    content = BooleanProperty(False)
    english = BooleanProperty(False)
    item = ObjectProperty(None)
    
    color = ObjectProperty((0,0,0,0))
    width_orig = NumericProperty(300)

    image_items = ListProperty([])
    children_items = ListProperty([])
    child_thumbs = ListProperty([])

    def __init__(self, **kwargs):
        super(Glass, self).__init__(**kwargs)
        self.color = (random.random(), random.random(), random.random(), 1)
        self.orig_width = self.width
        self.keywords = self.app.db.keywords[0]["children"]

    def remove(self):
        if not self.disabled:
            self.disabled = True
            self.parent.remove_widget(self)
            self.app.glass_count -= 1

    def match_filename_keyword(self, name):
        for key in self.keywords:
            if key["name"] == name:
                return key['id']

    def get_item_from_filename(self, filename_id):
        key_id = self.match_filename_keyword(filename_id)
        its = []
        for item in self.app.db.items:
            if key_id in item.keywords:
                it = {}
                it["item"] = item
                its.append(it)

        if len(its) > 0:
            it = random.choice(its)
            self.item = it["item"]
            self.content = True
            self.get_children()

    def get_children(self):
        children_ids = self.item.children
        children_items = []
        if len(children_ids) > 0:
            for child_id in children_ids:
                for item in self.app.db.items:
                    if item.id == int(child_id):
                        children_items.append(item)
        
        if len(children_items) > 0:
            i = 0
            for child in children_items:
                if i == 0: 
                    margin=0
                else: 
                    margin = 5
                but = GlassButton(
                    background_normal=child.filename, 
                    background_down=child.filename, 
                    color= self.color,
                    size= (58,58),
                    pos= (255 + margin + 58*i , 60),
                    item=child)
                but.bind(on_release = self.open_child_content)
                self.add_widget(but)
                self.child_thumbs.append(but)
                i += 1

    def remove_content(self):
        self.content = False
        for child in self.image_items[:]:
            if child != None:
                child.on_close()
        del self.image_items[:]
        
        for child in self.child_thumbs[:]:
            if child:
                self.remove_widget(child)
            self.child_thumbs.remove(child)

    # def pixel(self, x,y):
    #     x -= self.x
    #     y -= self.y
    #     x = int(x)
    #     y = int(y)
    #     y = self.height - y 
    #     coreimage = self.img._coreimage
    #     # coreimage = self.coreimage
    #     try:
    #         color = coreimage.read_pixel(x,y)
    #     except IndexError:
    #         print IndexError
    #         return False
    #     if color[-1] <= 0.1:
    #         return False

    #     return True

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.do_collide_after_children:
            if not self.collide_point(x, y):
                return False
        #limit the touch in the glass
        a = touch.pos
        b = self.center
        d = Vector(a).distance(b)
        if d > 100:

            # let the child widgets handle the event if they want
            touch.push()
            touch.apply_transform_2d(self.to_local)
            if super(Scatter, self).on_touch_down(touch):
                touch.pop()
                self._bring_to_front()
                return True
            touch.pop()

            # if our child didn't do anything, and if we don't have any active
            # interaction control, then don't accept the touch.
            if not self.do_translation_x and \
                not self.do_translation_y and \
                not self.do_rotation and \
                not self.do_scale:
                return False

            if self.do_collide_after_children:
                if not self.collide_point(x, y):
                    return False
            return        

        # grab the touch so we get all it later move events for sure
        self._bring_to_front()
        touch.grab(self)
        self._touches.append(touch)
        self._last_touch_pos[touch] = touch.pos

        return True

    def on_touch_move(self, touch):
        ret = super(Glass, self).on_touch_move(touch)
        if self.scale < .3:
            self.remove()

        mmap = self.app.map
        fn_id = mmap.find_glass_item(self.center)
        if fn_id:
            if self.content == False:
                self.get_item_from_filename(fn_id)
        else:
            self.content = False
            self.remove_content()
        return ret

    def launch_image_item(self, item):
        ii = ImageItem(app=self.app, item=item, source=item.filename)
        self.app.root_images.add_widget(ii)
        ii.pos = self.center
        ii.rotation = self.rotation
        return ii 

    def open_content(self, item_p):
        for item in self.image_items:
            if item.source == item_p.filename:
                return
        ii = ImageItem(app=self.app, item=item_p, source=item_p.filename, color=self.color, english= self.english)
        self.app.root.add_widget(ii)
        ii.center = self.center
        ii.glass = self
        ii.rotation = self.rotation
        ii.scale = .1
        anim = Animation(scale= .5, d=.2, t='out_cubic')
        anim.start(ii)
        self.image_items.append(ii)

    def open_child_content(self, but):
        self.open_content(but.item)

    def open_main_item(self):
        self.open_content(self.item)

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    bgmap = Image(source = 'widgets/map.jpg', size=(1920,1080))
    root.add_widget(bgmap)
    # -------------------------------------------------------------------------
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    # app.imagemap = imagemap = ImageMap(
    
    app.map = imagemap = ImageMap(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(1920, 1080),
            sources=sources,
            suffix='',
            glass=True)
    root.add_widget(imagemap)

    app.glass_count = 0
    def add_glass(but):
        if app.glass_count < 5:
            # x = random.randint(app.root_images.x + 200, app.root_images.right - 200)
            # y = random.randint(root.y + 300, root.top - 100)
            center_x = but.parent.center_x
            center_y = but.parent.center_y
            if but.english:
                x = center_x + 150
                y = center_y - 150 
                center_x -= 150
                center_y += 150
            else:                
                x = center_x - 150
                y = center_y + 150 
                center_x += 150
                center_y -= 150
            glass = Glass(  center=(x,y),
                            size=(300,300),
                            app= app,
                            english=but.english)
            root.add_widget(glass)
            app.glass_count += 1
            

            anim = Animation(center_x=center_x , center_y=center_y, d=.1, t='out_cubic')
            anim.start(glass)

    def increase_button(but):
        scat = but.parent
        # but.parent.scale = 1.5
        anim = Animation(scale=1.3, d=.05) + Animation(scale=1, d=.05)
        Animation.stop_all(scat)
        anim.start(scat)

    scat = Scatter( size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    rotation=180 ,
                    center=(75, Window.height-75))    

    but = Button(   size=(85,85),
                    size_hint= (None,None),
                    background_normal='widgets/btn-loupe.png',
                    background_down='widgets/btn-loupe.png',
                    on_press=increase_button,
                    on_release=add_glass)
                    # center=(75, Window.height-75))
    scat.add_widget(but)
    root.add_widget(scat)
    scat.center = (75, Window.height-75)
    but.english = False

    def change_expo(but):
        app.change_expo(str(41))
        # app.show_expo(str(41))

    scat2 = Scatter(size=(85,85), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    center=(Window.width - 75, 75))    

    but2 = Button(  size=(85,85),
                    size_hint= (None,None),
                    background_normal='widgets/btn-loupe.png',
                    background_down='widgets/btn-loupe.png',
                    on_press=increase_button,
                    on_release=add_glass)
    scat2.add_widget(but2)
    root.add_widget(scat2)
    scat2.center = (Window.width - 75, 75)
    but2.english = True

    scat3 = Scatter(size=(130,130), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    rotation=180,
                    size_hint=(None,None),
                    center=(75, 75))    

    but3 = Button(  size=(130,130),
                    size_hint= (None,None),
                    background_normal='widgets/btn-switch-mode.png',
                    background_down='widgets/btn-switch-mode.png',
                    on_press=increase_button,
                    on_release=change_expo)
    scat3.add_widget(but3)
    root.add_widget(scat3)
    scat3.center = (75,75)

    scat4 = Scatter(size=(130,130), 
                    do_scale=False, 
                    do_rotation=False,
                    do_translation=False,
                    scale=1,
                    size_hint=(None,None),
                    center=(Window.width -75, Window.height - 75))    

    but4 = Button(  size=(130,130),
                    size_hint= (None,None),
                    background_normal='widgets/btn-switch-mode.png',
                    background_down='widgets/btn-switch-mode.png',
                    on_press=increase_button,
                    on_release=change_expo)
    scat4.add_widget(but4)
    root.add_widget(scat4)
    scat4.center = (Window.width -75, Window.height - 75)

    def anim_buttons(dt):
        key = random.random()
        if key > .7:
            butint = random.random()
            if butint > .7:
                increase_button(but2)
            else:
                increase_button(but)

    # Clock.schedule_interval(anim_buttons, 2)


    root.hide_items = True
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

    return root

