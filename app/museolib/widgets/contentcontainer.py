from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty

from os.path import join, isfile, basename, getsize
from kivy.core.window import Window
from kivy.uix.image import Image, AsyncImage

from kivy.clock import Clock

import pymunk as pm

class ContentContainer(Scatter):

    source = StringProperty(None)

    img_item = ObjectProperty(None)

    item = ObjectProperty(None)

    current = NumericProperty(0)

    isMoving = BooleanProperty(False)

    count = NumericProperty(1)

    medias = ListProperty(None)

    item_pos = ObjectProperty((0,0))


    def __init__(self, *args, **kwargs):
        super(ContentContainer, self).__init__(**kwargs)
        for filedata in self.item.data:
            if self.item.data.index(filedata) == 0:
                self.medias.append(self.source)
            else:
                fileurl = filedata['fichier']
                filename = basename(fileurl)
                filepath = join(self.img_item.app.expo_dir, 'otherfiles', filename)
                if isfile(filepath) and getsize(filepath) > 0:
                    self.medias.append(filepath)
        self.count = len(self.medias)
        self.on_current()

        # self.load_other_images()

    def on_current(self, *largs):
        if self.prev_button != None and self.next_button != None:
            if self.count != 1:
                if self.current == 0:
                    self.next_button.opacity = 0
                    self.prev_button.opacity = 1
                    return
                elif self.current == self.count - 1:
                    self.prev_button.opacity = 0
                    self.next_button.opacity = 1
                    return
            else:
                self.prev_button.opacity = 0
                self.next_button.opacity = 0
                return
            self.prev_button.opacity = 1
            self.next_button.opacity = 1

    # def load_other_images(self, dt=None):
        # i=1
        # files = reversed(self.item.data)

        # for filedata in files:
        #     fileurl = filedata['fichier']
        #     filename = basename(fileurl)
        #     filepath = join(self.img_item.app.expo_dir, 'otherfiles', filename)
            
        #     if isfile(filepath):
        #         x0 = self.width-46
        #         aimg = Image(
        #             source=filepath,                    
        #             size_hint = (None, None),
        #             size= (x0, self.height-48))
        #         aimg.height = 50
        #         # aimg.center_y = self.center_y
        #         aimg.y = 0

        #         if i != 1:
        #             aimg.center_x = x0 * i  + aimg.width/2 + (x0 -aimg.width)/2 
        #         else:
        #             aimg.center_x = x0 * i  + aimg.width/2 + (x0 -aimg.width)/2 +4 
        #         # aimg.center_y = self.height/2 - 13
        #         # aimg.color=0,1,1,1
        #         self.stencil_layout.add_widget(aimg)
        #         self.count += 1
        #         aimg.x0 = aimg.x
                
        #         i+=1
        # self.on_current()
    
    def replace_img(self, index):
        # print index, self.count
        filepath = self.medias[index]
        img = AsyncImage(
                source=filepath,                    
                size_hint = (None, None),
                pos=(23,23),
                size= (self.width - 46, self.height-46))
        self.stencil_layout.clear_widgets()
        self.stencil_layout.add_widget(img)
        self.img = img

    def reset_viewer(self, dt):
        self.isMoving = False  

    def my_on_prev_button(self):
        # if self.isMoving == False and self.prev_button.opacity != 0:
            # self.isMoving = True
            # for child in self.stencil_layout.children:
            #     anim = Animation(x=child.x - 314, d=.3)
            #     anim.on_complete = self.reset_viewer
            #     anim.start(child)
            # self.current += 1
        if self.prev_button.opacity == 1:
            self.current += 1
            self.replace_img(self.current)
        

    def my_on_next_button(self):
        # if self.isMoving == False and self.next_button.opacity != 0:
            #     self.isMoving = True
            #     for child in self.stencil_layout.children:
            #         anim = Animation(x=child.x + 314, d=.3)
            #         anim.on_complete = self.reset_viewer
            #         anim.start(child)
            #     self.current -= 1
        if self.next_button.opacity == 1:
            self.current -= 1
            self.replace_img(self.current)
       

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isnt on the widget we do nothing
        if not self.do_collide_after_children:
            if not self.collide_point(x, y):
                return False

        if super(ContentContainer, self).on_touch_down(touch):
            if self.parent:
                parent = self.parent
                parent_0 = self.parent.parent 
                parent_0.remove_widget(parent)
                parent_0.add_widget(parent)
            return True
        # if len(self._touches) < 2:
        #   ret = super(ContentContainer, self).on_touch_down(touch)
        #   if not ret:
        #       return

        #   if self.scale >= 1:    
        #       #print 'container touch down', self.scale
        #       self.mouse_body = mouse_body = pm.Body(1, 1e9)
        #       mouse_body.position = touch.pos
        #       self.mouse_joint = pj = pm.PivotJoint(self.mouse_body, self.body, (0,0))
        #       self.img_item.space().add(mouse_body, pj)
        #     # for shape in self.img_item.space().shapes:
        #     #     self.img_item.space().reindex_shape(shape)
        #     #     shape.body.activate()
        #   return True
        #     # self.img_item.on_touch_down(touch)
        # elif self.collide_point(*touch.pos):
        #   return True

  #   def on_touch_move(self, touch):    
  #       # print self.item.id, self.pos, 
  #       try:
  #           ret = super(ContentContainer,self).on_touch_move(touch)
  #       except Exception:
  #           print 'on Touch move exception'

  #       if touch in self._touches and touch.grab_current == self:
  #           if not hasattr(self, 'body'):
  #               if 0 < self.center[0] < Window.width and 0 < self.center[1] < Window.height:
  #                   self.body.activate()
  #                   self.img_item.body.position = self.center
  #                   for shape in self.img_item.space().shapes:
  #                       self.img_item.space().reindex_shape(shape)
  #                       shape.body.activate()
  #           elif hasattr(self, 'mouse_body') and self.mouse_body != None:
  #               # self.body.position = touch.pos
  #               self.mouse_body.position = touch.pos
  #       return ret
  #   # self.img_item.on_touch_move(touch)

  #   def on_touch_up(self, touch):
  #       if not touch.grab_current == self:
  #           return False
  #       ret = super(ContentContainer, self).on_touch_up(touch)
  #   #     if touch in self._touches and touch.grab_current == self:
  #   #         if 0 < self.center[0] < Window.width and 0 < self.center[1] < Window.height:
  #   #             self.img_item.body.position = self.center
  #       sp = self.img_item.space()
  #       if hasattr(self, 'mouse_joint') and self.mouse_joint != None:
  #           sp.remove(self.mouse_joint)
  #           self.mouse_joint = None
  #       if hasattr(self, 'mouse_body') and self.mouse_body != None:
  #           sp.remove(self.mouse_body)
  #           self.mouse_body = None
  #       return True
  #       # self.img_item.on_touch_up(touch)

    def on_btn_close(self, *largs):
        self.img_item.close_content_container(close_parent=True)
        return True

    def on_remove(self):
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
