from os.path import join
from kivy.uix.floatlayout import FloatLayout
from museolib.widgets.basket import Basket

from kivy.properties import ListProperty, StringProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.core.window import Window
from museolib.widgets.imageitem import ImageItem
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image, AsyncImage
from os.path import join, isfile, basename

import os, time

from kivy.vector import Vector
from kivy.clock import Clock
from kivy.animation import Animation
import weakref, math
from kivy.graphics import Color, Ellipse, Line
from museolib.widgets.contentcontainer import ContentContainer
from museolib.utils import no_url
from glob import glob

from museolib.widgets.imagebuttons import ImageButtons 
from kivy.uix.button import Button
from random import random, randint, choice, shuffle

# from autobahn.websocket import WebSocketServerFactory, \
#                                WebSocketServerProtocol, \
#                                listenWS

import pymunk as pm
from pymunk import Vec2d

class ContentLine(Line):
    black = ObjectProperty(None)
    white = ObjectProperty(None)
    color = (1,1,1,1)

    def __init__(self, *args, **kwargs):
        super(ContentLine, self).__init__(**kwargs)
    
PARENT_SCALE_OPEN = .7
PARENT_SCALE_DEFAULT = .6
PARENT_SCALE_CLOSED = .5
CHILD_SCALE_OPEN = .42
CHILD_SCALE_DEFAULT = .35
CHILD_SCALE_CLOSED = .25

# PARENT_SCALE_OPEN = .8
# PARENT_SCALE_DEFAULT = .6
# PARENT_SCALE_CLOSED = .3
# CHILD_SCALE_OPEN = .6
# CHILD_SCALE_DEFAULT = .35
# CHILD_SCALE_CLOSED = .25

#### IMAGE ITEM
ImageItem.default_scale = NumericProperty(.6)
ImageItem.isOpening = BooleanProperty(False)
# ImageItem.radius = NumericProperty(64)

def my_on_start(self):

    def on_scale(self, scale):
        self.radius = self.orig_radius * self.scale +5
        if hasattr(self, 'shape') and self.shape != None:
            if round(self.shape.radius,1) != round(self.radius,1):
                self.shape.unsafe_set_radius(self.radius)
                # self.shape.cache_bb()
                sp = self.space()
                for shape in self.space().shapes:
                    sp.reindex_shape(shape)
                    shape.body.activate()

    if 'orig_geo_prec' in self.item and 'nom' in self.item and 'datation' in self.item:
        self.details = self.item.orig_geo_prec + ' [i]' + self.item.nom + '[/i] ' + self.item.datation

    match = {'media': 286, 'objet': 285, 'usage': 287}

    if str(match['media']) in self.item.keywords:
        self.color = (0.015,0.658,0.698,1)
    elif str(match['objet']) in self.item.keywords:
        self.color = (0.015,0.529,0.702,1)
    elif str(match['usage']) in self.item.keywords:
        self.color = (0.055,0.447,0.537,1)
    else:
        self.color = (1,1,1,.5)

    self.red = self.color[0]
    self.green = self.color[1]
    self.blue = self.color[2]
    self.alpha = self.color[3]

    self.opacity = 0
    self.family_text.opacity = 0

    if len(self.item['children']) == 0:
        self.isParent = False
        self.scale = CHILD_SCALE_DEFAULT
        self.diam = self.width * self.scale
        self.orig_radius = 128
        self.radius = 128
        self.default_scale = PARENT_SCALE_DEFAULT
        self.remove_widget(self.family_text)
    else:
        self.scale = PARENT_SCALE_DEFAULT
        self.isParent = True
        self.orig_radius = 128
        self.radius = 128
        self.is_open_return_button = False
        self.default_scale = PARENT_SCALE_DEFAULT
        

        def display_img(dt):
            def mask_txt(dt):
                self.family_text.opacity = 0
            anim = Animation(opacity=1, d=1)
            anim.on_complete = mask_txt
            anim.start(self.img_square)


        def should_display_name(dt):
            if randint(1,100) > 50 and round(self.img_square.opacity) == 1 and self.scale == PARENT_SCALE_DEFAULT:
                self.family_text.opacity = 1
                anim = Animation(opacity=0, d=1)
                anim.start(self.img_square)
                Clock.schedule_once(display_img, 15)

        interval = randint(10,30)
        Clock.schedule_interval(should_display_name, interval)

        # Clock.schedule_once(callback, .1)
        # def look_for_children(*largs):
        #     if self.app.items_to_add == 0:
        #         callback
        #         Clock.unschedule(look_for_children)
        # Clock.schedule_interval(look_for_children, 0.001) # add physics attribute to new items

        ## cest un parent donc -> declencher selon un temps aleatoire un callback qui activera aleatoiremet laffichage du mot.

    self.inertia = True
    self.bind(scale=on_scale)

ImageItem.on_start = my_on_start


# def run_animation(self): 
#     # create an animation object. 
#     x,y = self.body.position
#     x = int(x)
#     y = int(y)
#     print x, y
#     animation = Animation(pos=(x+5, y), t='out_bounce') 
#     animation += Animation(pos=(x, y+5), t='out_bounce') 
#     animation += Animation(pos=(x, y-5), t='out_bounce') 
#     animation += Animation(pos=(x-5, y), t='out_bounce') 
#     animation.start(self) 

# ImageItem.run_animation = run_animation

def move_children(self):
    if self.isParent:
        for child in self.children_refs:
            child = child()
            #process new angle of each child
            x, y = self.body.position
            x1, y1 = child.body.position
            ab = (x1-x)
            bc = (y1-y)
            new_angle = Vec2d(ab,bc).get_angle()
            child.angle = new_angle
            # repositionning child
            new_pos = get_child_pos(child)
            child.body.position = new_pos

ImageItem.move_children = move_children

def my_on_touch_down(self, touch):
    
    d = Vector(touch.pos).distance(self.center)
    if d > self.radius or len(self._touches) != 0 :
        return False
    if hasattr(self, 'space') and self.inertia == True: 
        sp = self.space()
        shape = sp.point_query_first(touch.pos)
        if shape != None:
            ##### PYMUNK TRANSLATION
            if not hasattr(self, 'mouse_body') or self.mouse_body == None:
                self.mouse_body = mouse_body = pm.Body(1, 1e9)
                mouse_body.position = touch.pos
                self.mouse_joint = ds = pm.PivotJoint(mouse_body, shape.body, (0,0))
                sp.add(mouse_body, ds)
            else:
                mouse_body = self.mouse_body
            mouse_body.position = touch.pos
            # for shape in self.space().shapes:
            #     self.space().reindex_shape(shape)
            #     shape.body.activate()
            touch.grab(self)
            self._touches.append(touch)
    return True

    ret = super(ImageItem, self).on_touch_down(touch)
    if not ret:
        return
    return True

def my_on_touch_move(self, touch):
    if self.inertia:
        if touch in self._touches and touch.grab_current == self:
            if hasattr(self, 'mouse_body') and self.mouse_body != None:
                if hasattr(self, 'mouse_body') and self.body != None:
                    self.body.activate()
                self.mouse_body.position = touch.pos 
                if abs(touch.dx)!= 0.0 and abs(touch.dy) != 0.0:
                    touch.ud['last_delta'] = (abs(touch.dx), abs(touch.dy))
            # if not self.isParent:
            #     print self.item.id, self.joint.impulse
            return True
    else:
        ret = super(ImageItem,self).on_touch_move(touch)
        return ret

def my_on_touch_up(self, touch):
    if self.inertia:
        if touch in self._touches and touch.grab_state:
            touch.ungrab(self)
            self._touches.remove(touch)

            sp = self.space()
            if hasattr(self, 'mouse_joint') and self.mouse_joint != None:
                sp.remove(self.mouse_joint)
                self.mouse_joint = None
            if hasattr(self, 'mouse_body') and self.mouse_body != None:
                sp.remove(self.mouse_body)
                self.mouse_body = None

            #print 'item touch up'
            #if touch.is_double_tap:
            #   print 'is double Tap'
            deltaTime = touch.time_update - touch.time_start
            if (deltaTime < .25) and not touch.is_double_tap:
                if self.isParent:
                    if self.isOpening == False:
                        self.isOpening = True
                        self.open()
                else:
                    if self.parent_node != None:
                        if self.parent_node().isOpening == False:
                            self.parent_node().isOpening = True
                            self.open()

            #   print 'opening container'
#            if (len(touch.ud) > 0 and hasattr(touch.ud, 'last_delta')) or touch.is_double_tap:
#                delta = touch.ud['last_delta']
#                if abs(delta[0]) < 6 and abs(delta[1]) < 6:
#                    self.open(
#                   |print 'opening container'
            # if touch.is_double_tap == False and t < .15 and abs(touch.dx) <= 1 and abs(touch.dy) <= 1: # check for tap (mouse only)
            #     self.open()
            #     print 'yes'
            return True
        return self.collide_point(*touch.pos)
    else:
        if not touch.grab_current == self:
            return False
        ret = super(ImageItem, self).on_touch_up(touch)
        return ret

ImageItem.on_touch_up = my_on_touch_up
ImageItem.on_touch_down = my_on_touch_down
ImageItem.on_touch_move = my_on_touch_move

def get_angle_container(item):
    x,y = item.center
    if item.isParent:
        if len(item.children_refs) > 0:
            x_total = 0
            y_total = 0
            for child in item.children_refs:
                child = child()
                x_total += child.center_x
                y_total += child.center_y

            x_moy = x_total / len(item.children_refs)
            y_moy = y_total / len(item.children_refs)

            v1 = Vector(x - x_moy, y - y_moy)

            angle = v1.angle((-1,0))
            angle = angle -90
        else:
            angle = 0
    elif hasattr(item, 'parent_node') and item.parent_node != None :
        x0, y0 = item.parent_node().center
        v1 = Vector(x0 - x, y0 -y)
        angle = v1.angle((-1,0))
        angle += 90
    return angle

def open_content_container(self):
    self.content_container = ct = ContentContainer(
        source= self.source, 
        img_item=self, 
        item=self.item,
        do_translation=True,
        auto_bring_to_front = True
        )

    # ct.height = 2*self.radius
    # ct.width = 3*self.radius
    ct.scale = 1.5
    if self.body != None:
        ct.item_pos = ct.center = self.body.position
        ct.rotation = round(get_angle_container(self))

        ct.line = Line(black=self, white=ct, color=self.color)
        # x1, y1 = ct.to_local(self.center_x, self.center_y, relative=True)
        # x0, y0 = ct.to_window(ct.width/2, ct.height/2)
        # with ct.canvas:
        #   # Color(self.color[0], self.color[1], self.color[2], self.color[3] )
        #   Color(0,0,0,1)
        #   Line(
        #       points= (ct.width/2, ct.height/2, ct.to_widget(ct.img_item.center_x, ct.img_item.center_y ) ),
        #       width= 3)

        # sp = self.space()
        # ct.body = pm.Body(1, 1e9)
        # ct.body.position = ct.center
        # sp.add(ct.body)
        
        # ct.joint = jt = pm.PivotJoint(self.body, ct.body, (0,0))
        # sp.add(jt)

        if self.isParent == True:
            ct.isParent = True
        else:
            ct.isParent = False

        if not hasattr(self.app, 'root_content_layout'):
            self.app.root_content_layout = FloatLayout()
            self.app.root.add_widget(self.app.root_content_layout)

        self.app.root_content_layout.add_widget(self.content_container)
        # self.app.root_images.add_widget(self.content_container)

        self.close_button.y = 140
        self.finishOpening()
        
        # print 'finish opening'

ImageItem.open_content_container = open_content_container

def close_content_container(self, d=.2, close_parent=False): 
    def remove(dt):
        if self.content_container != None:
            if close_parent == True:
                self.open()
            if hasattr(self.content_container,'joint') and self.content_container.joint != None:
                self.space().remove(self.content_container.joint)
                self.content_container.joint = None
            # self.app.root_images.remove_widget(self.content_container)
            self.app.root_content_layout.remove_widget(self.content_container)
            self.content_container = None
    if self.content_container != None:
        anim = Animation(scale=.2, d=d)
        anim.on_complete=remove
        anim.start(self.content_container)
        anim2 = Animation(y=52, d=d)
            # anim = Animation(y=y0 - 80, d=d)
        anim2.start(self.close_button)

ImageItem.close_content_container = close_content_container

def finishOpening(self):
    if self.isParent:
        self.isOpening = False
    else:
        if self.parent_node != None:
            self.parent_node().isOpening = False


ImageItem.finishOpening = finishOpening

def open(self, close_all=False):
    # offset = .3
    # child_offset = .1

    def toggle_joints(wid):
        if self.isParent:
            # self.move_children()
            for child in self.children_refs:
                add_joint_to_child(child(), self.space())

    def anim_scale(item, scale, on_progress = None, on_complete=None):
        Animation.stop_all(item)
        anim = Animation(scale = scale, duration=.2)
        if on_progress != None:
            anim.on_progress = on_progress
        if on_complete:
            anim.on_complete = on_complete
        anim.start(item)

    def close_item(item, scale):
        anim_scale(item, scale, on_complete=toggle_joints)
        item.isOpen=False
        if item.isParent == True:
            pass

    def open_item(item, scale):
        item.isOpen = True
        anim_scale(item, scale, on_complete=toggle_joints) 

    def close_children(item, scale):
        for child in item.children_refs:
            child=child()
            close_item(child, scale)

    def open_return_button(item):
        if item.isParent == True and item.is_open_return_button == False:
            # y0= item.return_button.pos[1]
            # anim = Animation(y=132, d=.2)
            # # anim = Animation(y=y0 + 80, d=.2)
            # anim.start(item.return_button)
            item.is_open_return_button = True

    def close_return_button(item, d=.2):
        if item.isParent == True and item.is_open_return_button == True:
            y0= item.return_button.pos[1]
            anim = Animation(y=52, d=d)
            # anim = Animation(y=y0 - 80, d=d)
            anim.start(item.return_button)
            item.is_open_return_button = False
    
    def open_content(dt):
        self.open_content_container()

    remove_joints_from_parent(self)

    if close_all == True:
        if hasattr(self, 'content_container') and self.content_container != None:
            # self.space().remove(self.content_container.joint)     ################################ CONTENT CONTAINER PHYSICS CLEAN UP
            # self.content_container.joint = None
            self.app.root_content_layout.remove_widget(self.content_container)
            # self.app.root_images.remove_widget(self.content_container)
            self.content_container = None
        if self.isParent:
            # close_return_button(item=self, d=0.05)
            self.return_button.y = self.return_button.y - 80
            self.is_open_return_button = False
#            self.scale = PARENT_SCALE_DEFAULT
            self.is_child_open = False
#        else:
            #self.scale = CHILD_SCALE_DEFAULT
 #       self.isOpen = False
    else:
        if not hasattr(self, 'isOpen') or self.isOpen == False:
            if self.isParent:
                if round(self.scale,1) == PARENT_SCALE_CLOSED:
                    close_item(self, PARENT_SCALE_DEFAULT)
                    self.finishOpening()
                elif round(self.scale,1) == PARENT_SCALE_DEFAULT:
                    open_item(self, PARENT_SCALE_OPEN)
                    Clock.schedule_once(open_content, .2)
                    # close_children(self, CHILD_SCALE_CLOSED)
                if hasattr(self, 'is_child_open') and self.is_child_open==True:
                    close_return_button(self)

                    self.is_child_open = False
                    for child in self.children_refs:
                        child = child()
                        close_item(child, CHILD_SCALE_DEFAULT)
                        if hasattr(child,'content_container') and child.content_container != None:
                            child.close_content_container()
            else:
                open_item(self, CHILD_SCALE_OPEN)
                Clock.schedule_once(open_content, .2)
                if self.parent_node:
                    parent = self.parent_node()
                    parent.is_child_open = True
                    
                    close_item(parent, PARENT_SCALE_CLOSED)
                    if hasattr(parent,'content_container') and parent.content_container != None:
                            parent.close_content_container()
                    open_return_button(parent)

                    for child in parent.children_refs:
                        child = child()
                        if child is not self:
                            close_item(child, CHILD_SCALE_CLOSED)
                            if hasattr(child,'content_container') and child.content_container != None:
                                child.close_content_container()
        else:
            if hasattr(self,'content_container') and self.content_container != None:
                self.close_content_container()
                self.finishOpening()
            if self.isParent:
                close_item(self, PARENT_SCALE_DEFAULT)
            else:
                close_item(self, CHILD_SCALE_DEFAULT)
                if self.parent_node:
                    parent = self.parent_node()
                    parent.is_child_open = False

                    close_item(parent, PARENT_SCALE_DEFAULT)
     
                    close_return_button(parent)
                    
                    for child in parent.children_refs:
                        child = child()
                        if child is not self:
                            close_item(child, CHILD_SCALE_DEFAULT)
            self.isOpen = False
        # ON PROGRESS DEPLACER LES SATELLITES OU PARENTS RELIES POUR CONSERVER UNE DISTANCE MIN/MAX
        # ENTRE LES OBJETS.

ImageItem.open = open

def remove_from_space(self):
    if hasattr(self, 'space') and self.space != None:
        sp = self.space()
        if hasattr(self, 'body') and self.body != None:
            sp.remove(self.body)
            self.body = None
        if hasattr(self, 'shape') and self.shape != None:
            sp.remove(self.shape)
            self.shape = None
        if hasattr(self, 'joint') and self.joint != None:
            sp.remove(self.joint)
            self.joint = None

ImageItem.remove_from_space = remove_from_space

def on_remove(self):
    # self.app.child_position
    filename = self.item.filename
    # self.app.images_pos[filename] = {
    #     'center': self.center,
    #     'rotation': self.rotation,
    #     'first_time': False
    #     }
    self.remove_from_space()
    self.open(close_all=True)

ImageItem.on_remove = on_remove


def remove_joints_from_parent(parent):
    if parent.isParent and hasattr(parent, 'children_refs'):
        for child in parent.children_refs:
            child = child()
            if hasattr(child, 'space'):
                if hasattr(child, 'joint'):
                    if child.joint != None and child.space() != None:
                        child.space().remove(child.joint)
                        child.joint = None

def get_child_pos(child):
    parent = child.parent_node()
    dist = 250 * parent.scale
    centerx, centery = parent.body.position.x, parent.body.position.y
    child.x = centerx + math.cos(child.angle) * dist
    child.y = centery + math.sin(child.angle) * dist
    return child.x, child.y

def add_joint_to_child(child, space):
    if child.isParent == False and hasattr(child, 'parent_node'):
        if child.parent_node().body != None and child.body != None:
            child.joint = pj = pm.PinJoint(
                                child.parent_node().body,  #body a
                                child.body,                 #body b
                                anchr1=(0,0),               #anchor point 1
                                anchr2=(0,0))               #anchor point 2
            pj.draw = True
            space.add(pj)

def set_up_item_bodies(items, space):
    # pos_list = []
    for child in items:
        child.rotation = 0
        # scale = 0
        if not hasattr(child, 'body') or child.body == None:
            if child.isParent:
                child.body = body = pm.Body(1, 1e9)
                # if len(pos_list) > 0:
                #     for pos in pos_list:
                #         if 
                # pos_list.append(child.center)
                body.position = child.center 
                child.pos_children = [0,60,120,180,240,300]
                # print child.radius
            else:
                child.body = body = pm.Body(1, 1e9)
                parent = child.parent_node()
                pos = parent.pos_children
                child.angle = angle = choice(pos)
                pos.remove(angle)

                body.position = get_child_pos(child)
                # GET PREVIOUS POS IF ALREADY DISPLAYED
                # if child.source in child.app.images_pos:
                #     p = child.app.images_pos[child.source]
                #     if child.source in child.app.bodies_created: 
                #         body.position = p['center']
                # scale = CHILD_SCALE_DEFAULT
            body.sprite = weakref.ref(child)

            child.shape = shape = pm.Circle(body, child.radius)
            child.space = weakref.ref(space)
            shape.elasticity = 0.8
            shape.friction = .5
            space.add(body, shape)


            # if child.source not in child.app.bodies_created:
            #     child.app.bodies_created.append(child.source)
        
        # joints
        if not hasattr(child, 'joint') or child.joint == None:
            add_joint_to_child(child, space)
       
        # child.scale = .1
        # anim = Animation(scale=scale, d=.5)
        op = .2
        for key in child.app.keywords_ids:
            if key in child.item.keywords:
                op = 1
            else:
                child.color= (.2,.2,.2,1)

        anim = Animation(opacity=op, d=.5)
        anim.start(child)

# class EchoServerProtocol(WebSocketServerProtocol):
 
#    def onMessage(self, msg, binary):
#       self.sendMessage(msg, binary)
#       print 'message received'

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    
    # -------------------------------------------------------------------------
    # BACKGROUND
    # ------------------------------------------  
    background = Image(source ='widgets/background.jpg', pos_hint={'center_x':.5, 'center_y':.5})
    root.add_widget(background)


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                    PHYSICS
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    constraints_layout = FloatLayout()
    root.add_widget(constraints_layout)

    app.bodies_created = []

    def update_objects():
        constraints_layout.canvas.clear() 
        if hasattr(app, 'root_images'):
            for child in app.root_images.children:
                if hasattr(child, 'body'):
                    p = child.body.position
                    child.center = p.x , p.y
                    if hasattr(child, 'content_container') and child.content_container != None:
                        with constraints_layout.canvas:
                            opacity = min(child.opacity, child.content_container.opacity)
                            Color(child.color[0], child.color[1], child.color[2], opacity ) 
                            # Color(0.2,0.5,0.85,1)
                            Line(   points=[child.center_x,child.center_y, child.content_container.center_x, child.content_container.center_y],
                                    width=3,
                                    dash_offset=5)              

        for c in app.space.constraints:
            if c.a != None and c.b != None:
                if hasattr(c, 'draw') and c.draw == True:
                    p1x, p1y = c.a.position.x, c.a.position.y 
                    p2x, p2y = c.b.position.x, c.b.position.y 
                    
                    opacity = 1
                    
                    if hasattr(c.a, 'sprite') and hasattr(c.b, 'sprite'):
                        if c.a.sprite() != None and c.b.sprite() != None:
                            opacity = min(c.a.sprite().opacity, c.b.sprite().opacity)
                        else:
                            app.space.remove(c)

                    with constraints_layout.canvas:
                        Color(1,1,1,opacity) 
                        # Color(0.2,0.5,0.85,1)
                        Line(   points=[p1x,p1y, p2x,p2y],
                                width=1,
                                dash_offset=5)
            else:
                app.space.remove(c)

    def step(dt):
        app.space.step(1/6.)
        update_objects()

    def link_parent_and_children():
        for item in app.root_images.children: # looking on all items displayed
            if item.isParent == True: # is parent
                children = item.item.children #list of children ids
                item.children_refs = [] # list for children refs
                for child in app.root_images.children: # looking for child in displayed items
                    if str(child.item.id) in children:
                        child.parent_node = weakref.ref(item) #adding a ref of parent in child
                        item.children_refs.append(weakref.ref(child)) # adding a ref of child in parent

    def init_items_bodies(dt, *args):
        link_parent_and_children()
        items = []
        for child in app.root_images.children:
            if child.isParent:
                items.append(child)
        for child in app.root_images.children:
            if not child.isParent and hasattr(child, 'radius') :
                items.append(child)
        set_up_item_bodies(items, app.space) 

    def update_bounds(*largs):
        assert(len(app.bounds) == 4)
        a, b, c, d = app.bounds
        x0, y0 = -100,-100
        x1 = Window.width + 100
        y1 = Window.height + 100

        app.space.remove(a)
        app.space.remove(b)
        app.space.remove(c)
        app.space.remove(d)
        a.a = (x0, y0)
        a.b = (x1, y0)
        b.a = (x1, y0)
        b.b = (x1, y1)
        c.a = (x1, y1)
        c.b = (x0, y1)
        d.a = (x0, y1)
        d.b = (x0, y0)
        app.space.add(a)
        app.space.add(b)
        app.space.add(c)
        app.space.add(d)

    def init_physics():
        print 'init_physics'
        app.bounds = []
        app.space = space = pm.Space()
        space.iterations = 30
        space.damping = .2
        space.gravity = (0, 0)
        space.sleep_time_threshold = 0.5
        space.collision_stop = 0.5    

        for x in xrange(4):
            seg = pm.Segment(space.static_body,
                    Vec2d(0,0), Vec2d(0,0), 100)
            seg.elasticity = 0.9
            app.bounds.append(seg)
            space.add(seg)

        Clock.schedule_interval(step, 1./60)
        update_bounds()
        # Window.bind(size=update_bounds)
        # Clock.schedule_once(init_items_bodies, 1.)

    init_physics()

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                    BUTTONS AND WIDGETS
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Create an image Button
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '-active' not in x]
    app.imageButtons = imageButtons = ImageButtons(
                           size_hint=(None, None),
                           size=(350, 350),
                           sources=sources,
                           suffix='-active',
                           show_objects_when_empty=False,
                           show_one_cat_only=True,
                           is_circular = True)
    scatter = scatter_imageButtons = Scatter(
                            auto_bring_to_front=True,
                            size=imageButtons.size,
                            size_hint=(None, None), rotation=0, scale=1,
                            center=Window.center,
                            do_scale=False,
                            scale_min=.8,
                            scale_max=1.2) 
    img = Image(source = 'widgets/background_menu.png', size=(350,350))
#    halo = Image(source = 'widgets/halo.png', size=(3600,3600), pos=(-1800,-1800))
#    scatter.add_widget(halo)
    scatter.add_widget(img)
    scatter.add_widget(imageButtons)
    # halo.center = img.center
    root.add_widget(scatter, 25)


    def on_imgButton_center(self, value):
        parent = self.parent
        if not parent:
            return
        x, y = value
        x = max(parent.x, x)
        y = max(parent.y, y)
        x = min(parent.right, x)
        y = min(parent.top, y)
        self.center = x, y
    
    scatter_imageButtons.bind(center=on_imgButton_center)

    def default_value_for_imageButton(dt):
        for child in app.imageButtons.children:
            if child.source == 'expos/39/data/widgets/map/Reliures.png':
                child.set_active()

    Clock.schedule_once(default_value_for_imageButton, 1)

    img = Image(source='widgets/glossaire.png', size=(900,698))

    close_button = Button(
        background_normal='widgets/btn-close.png',
        background_down='widgets/btn-close-active.png',
        size_hint=(None,None),
        size=(60,60),
        border=(0,0,0,0))
    scatter_button = Scatter(
                    size_hint=(None,None),
                    size=close_button.size, scale=.8,
                    pos=(img.width - close_button.width +8, img.height - close_button.height + 8))
   
    scatter = scatter_glossaire = Scatter(
                        size_hint=  (None,None),
                        size=       img.size, 
                        scale=      .5, 
                        scale_min=  0.5, 
                        scale_max=  1.5,
                        x=          10,
                        center_y=   340)
    scatter_button.add_widget(close_button)
    scatter.add_widget(img)
    scatter.add_widget(scatter_button)

    
    with scatter.canvas:
        Color(0.827,0.286,0.023,0)
        Line(
            points= (0,0, 0,scatter.height, scatter.width,scatter.height, scatter.width,0),
            close= True,
            width= 2)

    def on_close_glossaire(but=None):
        if scatter_glossaire in root.children:
            root.remove_widget(scatter_glossaire)
    close_button.bind(on_release=on_close_glossaire)

    glossaireButton = Button(
        background_normal='widgets/caption-glossaire.png',
        background_down='widgets/caption-glossaire-active.png',
        size_hint=(None,None),
        size=(100,100),
        border=(0,0,0,0),
        x=0, 
        y=Window.height-100)

    def show_glossaire(but):
        if scatter_glossaire not in root.children:
            root.add_widget(scatter_glossaire)
            scatter_glossaire.scale = .5
            scatter_glossaire.rotation = 0
            scatter_glossaire.x = 10
            scatter_glossaire.center_y = 340
        else:
            on_close_glossaire()
    
    root.add_widget(glossaireButton)
    glossaireButton.bind(on_release=show_glossaire)

    # media : 286, objet : 285, usage : 287
    # if str(match['media']) in self.item.keywords:
    #     self.color = (0.015,0.658,0.698,1)
    # elif str(match['objet']) in self.item.keywords:
    #     self.color = (0.015,0.529,0.702,1)
    # elif str(match['usage']) in self.item.keywords:
    #     self.color = (0.055,0.447,0.537,1)
    #
    match = {'media': 286, 'objet': 285, 'usage': 287}

    def magnify_items(button):
        if hasattr(button, 'cat'):
            id_keyword = match[button.cat]
            for child in app.root_images.children:
                if isinstance(child, ImageItem):
                    previous_opacity = child.opacity
                    previous_color = child.color
                    child.opacity = 0
                    
                    child.color = (0.055,0.447,0.537,1)

                    if str(id_keyword) in child.item.keywords:
                        child.img_square.color = child.color
                        Animation.stop_all(child)
                        anim = Animation(opacity = 1, d=1) + Animation(opacity = previous_opacity, d=5)
                        anim.start(child)
                    else:
                        opacity_min = .1
                        Animation.stop_all(child)
                        anim = Animation(opacity = opacity_min, d=1) + Animation(opacity=previous_opacity, d=5)
                        anim.start(child)
                        if hasattr(child, 'content_container') and child.content_container != None:
                            anim2 = Animation(opacity = opacity_min, d=.5) + Animation(opacity = opacity_min, d=2) + Animation(opacity=1, d=1)
                            anim2.start(child.content_container)
                    anim1 = Animation(color=(1,1,1,1), d=10)
                    anim1.start(child.img_square)
                    
                    anim2 = Animation(color=previous_color, d=10)
                    anim2.start(child)

    mediaButton = Button(
        background_normal='widgets/caption-media.png',
        background_down='widgets/caption-media-active.png',
        size_hint=(None,None),
        size=(100,100),
        border=(0,0,0,0),
        x=Window.width - 100, 
        y=0)
    mediaButton.cat = 'media'
    mediaButton.bind(on_release=magnify_items)
    root.add_widget(mediaButton)

    objetButton = Button(
        background_normal='widgets/caption-objet.png',
        background_down='widgets/caption-objet-active.png',
        size_hint=(None,None),
        size=(100,100),
        border=(0,0,0,0),
        x=0, 
        y=0)
    objetButton.cat = 'objet'
    objetButton.bind(on_release=magnify_items)
    root.add_widget(objetButton)

    usageButton = Button(
        background_normal='widgets/caption-usage.png',
        background_down='widgets/caption-usage-active.png',
        size_hint=(None,None),
        size=(100,100),
        border=(0,0,0,0),
        x=Window.width - 100, 
        y=Window.height-100)
    usageButton.cat = 'usage'
    usageButton.bind(on_release=magnify_items)
    root.add_widget(usageButton)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                    APP MODIFICATIONS
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    # remove all children from filtered items list
    app.all_items = app.db.items
    tmp = []
    for item in app.all_items:
        if len(item['children']) != 0: # item is parent
            tmp.append(item)
    app.db.items = tmp

    local_pos = []
    i = 5
    j = 3
    while j > 0:
        while i > 0:
            i -= 1
            local_pos.append((344*i + 300, 293*j ))
        i = 5
        j -= 1

    def show_objects(objects):
        self = app
        root = self.root
        positions = local_pos[:]
        shuffle(positions)
        app.images_pos.clear()

        if isinstance(self.root_images.x, (int, long)):
            if root.type_expo == 'normal':
                # images = [x.source for x in self.root_images.children]
                images = []
                # for x in self.root_images.children[:]:
                #     if isinstance(x, ImageItem):
                #         images.append(x.source)

                images_to_add = []
                images_displayed = []
                for item in objects[:]:
                    # is the current filename is already showed ?
                    filename = item.filename
                    # if filename in images:
                    #     images.remove(filename)
                    #     continue

                    x = randint(self.root_images.x + 200, self.root_images.right - 200)
                    y = randint(root.y + 300, root.top - 100)
                    
                    if len(item.children) > 0:
                        if len(positions) > 0:                    
                            x,y = choice(positions)
                            positions.remove((x,y))

                    angle = randint(0, 360) 
                    image = dict(source=filename, rotation=angle + 90,
                            center=(x, y), item=item, app=self)
                    images_to_add.append(image)
                    images_displayed.append(filename)
                    objects.remove(item)

                # remove all the previous images
                for child in self.root_images.children[:]:
                        if isinstance(child, ImageItem):
                            # for filename in images:
                            #     if filename == child.source:
                                    # self.images_pos[filename] = {
                                    #     'center': child.center,
                                    #     'rotation': child.rotation }
                            if hasattr(child, 'on_remove'):
                                child.on_remove() # close everything and remove all physics attributes from child
                            self.root_images.remove_widget(child)

                self.images_displayed = images_displayed
                self.delayed_work(self.show_object, images_to_add)
            
            def add_physics_bodies(*largs):
                if app.items_to_add == 0:
                    init_items_bodies(.5)
                    Clock.unschedule(add_physics_bodies)
            Clock.schedule_interval(add_physics_bodies, 0.1) # add physics attribute to new items

    app.show_objects = show_objects

    def bring_content_to_front(dt):
        if app.items_to_add == 0:
            parent = app.root
            if hasattr(app, 'root_content_layout'):
                parent.remove_widget(app.root_content_layout)
                parent.add_widget(app.root_content_layout)
            Clock.unschedule(bring_content_to_front)
            
    def trigger_content_layout_to_front():
        Clock.schedule_interval(bring_content_to_front, .1)

    def my_update_objects_from_filter(dt, *largs):
        '''Update the objects displayed from filters (date range, origin...)
        '''
        self = app
        items = self.db.items

        # filter from keywords but with image buttons, only if there is group of keyword with 'filtre' in the group's name
        if app.imageButtons:
            keywords_names = app.imageButtons.active_ids
            app.keywords_ids = keywords_ids = []
            groups = self.db.keywords
            items_result = []  
            keywords_all = []
            time_keyword = ['297', '298', '299', '300', '301', '302']

            for group in groups:
                if group['group'].find('filtre') != -1:
                    keywords_all = group['children']
            if (keywords_all):
                for name in keywords_names:
                    for keyword in keywords_all:
                        if name == keyword['name']:
                            keywords_ids.append(keyword['id'])

                for item in items:
                    for key in keywords_ids:
                        if key in item.keywords:
                            items_result.append(item)

                if app.imageButtons.show_objects_when_empty == True:
                    if not keywords_names and not items_result: #si aucune image activee et aucun resultat
                      items_result = items # on affiche tout

                # Adding parents which have children selected by keyword
                tmp = []
                for parent in items:
                    if parent not in items_result:
                        for child_id in parent.children:
                            for child in self.all_items:
                                if child.id == int(child_id):
                                    for key in keywords_ids:
                                        if key in child.keywords and parent not in tmp:                                
                                            tmp.append(parent)
                items_result = items_result + tmp

                # Limit at 15 parents
                # del items_result[len(local_pos):]
                del items_result[15:]
                shuffle(items_result)

                #adding children of parents
                for item in items_result:
                    if len(item.children) > 0:
                        for child in self.all_items:
                            if str(child.id) in item.children:
                                items_result.append(child)

                items = items_result
            self.show_objects(items)
            trigger_content_layout_to_front()

    # create trigger for updating objects
    my_trigger_objects_filtering = Clock.create_trigger(
            my_update_objects_from_filter, 0)

    app.trigger_objects_filtering = my_trigger_objects_filtering

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                           SCREENSAVER
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    def screensaver(dt=None, stop=False):
        Animation.stop_all(scatter_imageButtons)
        if not stop:
            anim = Animation(opacity = .5, d=5)
            anim.start(scatter_imageButtons)
        else:
            scatter_imageButtons.opacity = 1
        
        for child in app.root_images.children:
            if child.isParent and child.__class__.__name__ == 'ImageItem':
                if hasattr(child, 'body') and child.body != None:
                    if stop == False:
                        forces = [-5,5,0]
                        rx = choice(forces)
                        ry = choice(forces)
                        child.body.reset_forces()
                        child.body.apply_force((rx,ry), r=(0, 0))
                    else:
                        child.body.reset_forces()
    
    def launch_screensaver(dt):
        delay = time.time() - app.last_touch_time
        if delay > 5:
            Clock.schedule_interval(screensaver, 5)
            Clock.unschedule(launch_screensaver)

    # Clock.schedule_interval(launch_screensaver, 1)

    def stop_screensaver():
        Clock.unschedule(screensaver)
        Clock.schedule_interval(launch_screensaver, 1)
        scatter_imageButtons.opacity = 1
        screensaver(stop=True)

    app.last_touch_time = 0
    def on_touch_app(touch):
        app.last_touch_time = touch.time_start
        for child in root.children[:]:
            if child.dispatch('on_touch_down', touch):
                stop_screensaver()
                return True
        
    # root.on_touch_down = on_touch_app

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                           NETWORK PART
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------    

    # factory = WebSocketServerFactory("ws://localhost:9000") 
    # factory.protocol = EchoServerProtocol
    # listenWS(factory)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    #                           BASKET
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

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

    return root

