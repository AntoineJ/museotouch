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

import random, time

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
    source = StringProperty(None)
    img = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GlassButton, self).__init__(**kwargs)
        if self.source != None:
            self.img = img = Image(
                source=self.source,
                pos=self.pos,
                size_hint=(None, None),
                allow_stretch=True,
                keep_ratio=False,
                size=self.size)
            self.add_widget(img)

    def on_state(self, button, state ):
        if state == 'down':
            # self.background_color = self.color
            self.img.color = self.color
        else:
            self.img.color = (1,1,1,1)
            # self.background_color = (1,1,1,1)

class Glass(Scatter):
    background_img = StringProperty('')
    glass_img = StringProperty('')
    disabled = BooleanProperty(False)
    app = ObjectProperty(None)

    content = BooleanProperty(False)
    content2 = BooleanProperty(False)
    english = BooleanProperty(False)
    item = ObjectProperty(None)
    item2 = ObjectProperty(None)
    
    color = ObjectProperty((0,0,0,0))
    width_orig = NumericProperty(300)

    image_items = ListProperty([])
    children_items = ListProperty([])
    child_thumbs = ListProperty([])

    fn_id = StringProperty(None)

    def __init__(self, **kwargs):
        super(Glass, self).__init__(**kwargs)
        self.color = (random.random(), random.random(), random.random(), 1)
        self.orig_width = self.width
        self.keywords = self.app.db.keywords[0]["children"]

    def remove(self):
        if not self.disabled:
            self.remove_content()
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
            if key_id in item.keywords and "361" in item.keywords:
                it = {}
                it["item"] = item
                its.append(it)
        if len(its) > 0:
            self.item = its[0]["item"]
            self.content = True
            if len(its) > 1:
                self.item2 = its[1]["item"]
                self.content2 = True
            self.get_children()

    def look_for_children(self, ids):
        children_items = []
        if len(ids) > 0:
            for child_id in ids:
                for item in self.app.db.items:
                    if item.id == int(child_id):
                        children_items.append(item)
        return children_items

    def create_glass_button(self, parent, fn, pos, item):
        but = GlassButton(
            # background_normal=fn, 
            # background_down=fn, 
            source= fn,
            background_color=(1,1,1,0),
            color= self.color,
            size= (58,58),
            pos= pos,
            item=item)
        but.bind(on_release = self.open_child_content)
        parent.add_widget(but)
        self.child_thumbs.append(but)

    def get_children(self):
        if self.content == True:
            children_ids = self.item.children
            children_items = self.look_for_children(children_ids)
            
            if len(children_items) > 0:
                i = 0
                for child in children_items:
                    if i == 0: 
                        margin=0
                    else: 
                        margin = 5
                    self.create_glass_button(fn=child.filename, parent=self, pos=(255 + margin + 58*i , 58), item=child)
                    i += 1
        if self.content2 == True:
            children_ids = self.item2.children
            children_items = children_items = self.look_for_children(children_ids)
            if len(children_items) > 0:
                i = 0
                for child in children_items:
                    if i == 0: 
                        margin=0
                    else: 
                        margin = 5
                    self.create_glass_button(fn=child.filename, parent=self.scatContent, pos=(0 + margin + 58*i , -2), item=child)
                    i += 1
            

    def remove_content(self):
        self.content = False
        self.content2 = False
        self.fn_id = ''
        for child in self.image_items[:]:
            if child != None:
                child.on_close()
        del self.image_items[:]
        
        for child in self.child_thumbs[:]:
            if child:
                child.parent.remove_widget(child)
            self.child_thumbs.remove(child)

    def on_center(self, instance, value):
        parent = self.parent
        if not parent:
            return
        # causing problems when the item scale was too important
        x, y = value
        x = max(parent.x, x)
        y = max(parent.y, y)
        x = min(parent.right, x)
        y = min(parent.top, y)
        self.center = x, y

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
            if self.content == False or self.fn_id != fn_id:
                self.get_item_from_filename(fn_id)
                self.fn_id = fn_id
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

    def open_main_item(self, ido):
        if ido == "1":
            self.open_content(self.item)
        elif ido == "2":
            self.open_content(self.item2)

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
                x = center_x - 150
                y = center_y + 150 
                center_x += 150
                center_y -= 150                
            else:                
                x = center_x + 150
                y = center_y - 150 
                center_x -= 150
                center_y += 150
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
    but.english = True

    def change_expo(but):
        app.change_expo(str(41))

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
    but2.english = False

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

    ##### MODE VEILLE

    helpLayout = FloatLayout()

    helpQuizz1Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=-45)
    helpQuizz1 = Image( source='widgets/pop-up-help-quiz.png',
                        size=(320,90))
    helpQuizz1Scat.add_widget(helpQuizz1)
    helpLayout.add_widget(helpQuizz1Scat)
    helpQuizz1Scat.center=(150,150)
    
    helpQuizz2Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=90+45)
    helpQuizz2 = Image( source='widgets/pop-up-help-quiz.png',
                        size=(320,90))
    helpQuizz2Scat.add_widget(helpQuizz2)
    helpLayout.add_widget(helpQuizz2Scat)
    helpQuizz2Scat.center=(Window.width-150,Window.height-150)
    
    helpExpo1Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=-135)
    helpExpo1 = Image( source='widgets/pop-up-help-loupe.png',
                        size=(320,90))
    helpExpo1Scat.add_widget(helpExpo1)
    helpLayout.add_widget(helpExpo1Scat)
    helpExpo1Scat.center=(150,Window.height-150)
    
    helpExpo2Scat = Scatter(size=(320,90),
                                do_scale=False,
                                do_rotation=False,
                                do_translation=False,
                                scale=1,
                                rotation=45)
    helpExpo2 = Image( source='widgets/pop-up-help-loupe.png',
                        size=(320,90))
    helpExpo2Scat.add_widget(helpExpo2)
    helpLayout.add_widget(helpExpo2Scat)
    helpExpo2Scat.center=(Window.width-150,150)

    root.add_widget(helpLayout)


    def anim_clues(dt):
        Animation.stop_all(helpExpo1Scat)
        Animation.stop_all(helpExpo2Scat)
        Animation.stop_all(helpQuizz1Scat)
        Animation.stop_all(helpQuizz2Scat)

        delta = 5
        dt = dt /10

        anim = Animation(center_x=helpExpo1Scat.center_x + delta, center_y=helpExpo1Scat.center_y - delta, d=dt/2) + Animation(center=helpExpo1Scat.center, d=dt/2)
        anim.start(helpExpo1Scat)
        anim = Animation(center_x=helpExpo2Scat.center_x - delta, center_y=helpExpo2Scat.center_y + delta, d=dt/2) + Animation(center=helpExpo2Scat.center, d=dt/2)
        anim.start(helpExpo2Scat)
        anim = Animation(center_x=helpQuizz1Scat.center_x + delta, center_y=helpQuizz1Scat.center_y + delta, d=dt/2) + Animation(center_x=helpQuizz1Scat.center_x , center_y=helpQuizz1Scat.center_y , d=dt/2)
        anim.start(helpQuizz1Scat)
        anim = Animation(center_x=helpQuizz2Scat.center_x - delta, center_y=helpQuizz2Scat.center_y - delta, d=dt/2) + Animation(center_x=helpQuizz2Scat.center_x , center_y=helpQuizz2Scat.center_y , d=dt/2)
        anim.start(helpQuizz2Scat)

    # Clock.schedule_interval(anim_clues, 2)

    def toggle_help_layout(show=True):
        Animation.stop_all(helpLayout)
        if show:
            anim = Animation(opacity=1, d=1)
            anim.start(helpLayout)
        else:
            anim = Animation(opacity=0, d=1)
            anim.start(helpLayout)

    def launch_screensaver(dt):
        delay = time.time() - app.last_touch_time
        if delay > 15:
            Clock.schedule_interval(anim_clues, 2)
            toggle_help_layout(show=True)
            Clock.unschedule(launch_screensaver)

    Clock.schedule_interval(launch_screensaver, 1)

    def stop_screensaver():
        Clock.unschedule(anim_clues)
        Clock.schedule_interval(launch_screensaver, 1)
        toggle_help_layout(show=False)

    app.last_touch_time = 0
    def on_touch_app(touch):
        app.last_touch_time = touch.time_start
        for child in root.children[:]:
            if child.dispatch('on_touch_down', touch):
                stop_screensaver()
                return True

    root.on_touch_down = on_touch_app

    ##### FIN VEILLE
    
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

