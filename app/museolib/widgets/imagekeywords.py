# -*- coding: utf-8 -*-

from os import sep
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, BooleanProperty, StringProperty
from kivy.resources import resource_find
from kivy.core.image import Image as CoreImage
from kivy.vector import Vector
from kivy.animation import Animation


import os
from os.path import isdir, isfile, getsize, join, basename, splitext


class ImageKeywordsItem(Image):
    active = BooleanProperty(False)
    source_active = StringProperty(None)
    source_original = StringProperty(None)
    category = StringProperty('') # group of keywords
    key = StringProperty('') # key of keyword


    def __init__(self, **kwargs):
        super(ImageKeywordsItem, self).__init__(**kwargs)
        self.key = splitext(basename(self.source_original))[0]

    def on_touch_up(self, touch):
        if touch.grab_current is self.parent:
            delay = touch.time_update - touch.time_start
            delta = abs(touch.dx) + abs(touch.dy)
            
            if delta < 2:
                ret = self.toggle_active(touch)       
                if ret == True:
                    touch.ungrab(self.parent)
                return ret
            return False
    
    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        elif isfile(self.source):
            filename = resource_find(self.source)
            image = CoreImage(filename, keep_data=True)
            texture = image.texture
            self.texture = texture
            self._coreimage = image
    
    def set_active(self):
        self.active = not self.active
        self.source = self.source_active if self.active \
            else self.source_original
    
    def toggle_active(self, touch):
        if self.opacity == 0:
            return
        x, y = touch.pos
        x -= self.x
        y -= self.y
        x = int(x)
        y = int(y)
        y = self.parent.height - y # Because texture is flipped vertically since kivy 1.5.0
        coreimage = self._coreimage
        try:
            color = coreimage.read_pixel(x, y)
        except IndexError:
            return False
        if color[-1] == 0:
            return False

        self.set_active()

        return True

class ImageKeywordsKey(ImageKeywordsItem):
    def toggle(self):
        opacity = 0
        if self.opacity > 0:
            opacity = 0
        else:
            opacity = 1
        Animation.stop_all(self)
        anim = Animation(opacity=opacity, d=.3)
        anim.start(self)

    def on_active(self, instance, value):
        keywords = self.parent.selected_keywords
        key = (self.category, self.key)

        if value:
            if not key in keywords:
                keywords.append(key)
        else:
            if key in keywords:
                keywords.remove(key)

class ImageKeywordsGroup(ImageKeywordsItem):
    def on_active(self, instance, value):
        for child in self.parent.children:
            if isinstance(child, ImageKeywordsKey) and child.category == self.key: # Showing all keys of the group
                child.toggle()
                if self.parent.activate_keys_by_default:
                    child.set_active()
                if value == False:
                    if child.active != value: # Deselect keywords before after hidding them
                        child.set_active()

    def set_active(self):
        if self.parent.show_one_cat_only:
            for child in self.parent.children:
                if isinstance(child, ImageKeywordsGroup) and child.active == True and not child == self:
                    child.set_active()
        super(ImageKeywordsGroup, self).set_active()

class ImageKeywords(FloatLayout):
    
    suffix = StringProperty('')
    sources = StringProperty('')
    active_ids = ListProperty([])

    keywords = ListProperty([])
    selected_keywords = ListProperty([])
    selected_groups = ListProperty([])
    db = ListProperty([])

    show_objects_when_empty = BooleanProperty(False)
    show_one_cat_only = BooleanProperty(False)
    is_circular = BooleanProperty(False)
    activate_keys_by_default = BooleanProperty(True)


    
    def __init__(self, **kwargs):
        # self._update_images = Clock.create_trigger(self.update_images, -1)
        super(ImageKeywords, self).__init__(**kwargs)

        for root, dirs, files in os.walk(self.sources):
            myfiles = [x for x in files if '_active' not in x]
            myfiles = [x for x in myfiles if '.db' not in x]
            if root == self.sources:
                self.db.append({'files': myfiles, 'folder':'root'})
            else:
                self.db.append({'files': myfiles, 'folder':basename(root)})
        self.update_images(.1)
        # self.bind(suffix=self._update_images,
        #           sources=self._update_images)
        # self._update_images()

    def update_images(self, dt):
        for child in self.children[:]:
            child.unbind(active=self.on_key_active)
            child.unbind(active=self.on_group_active)
            self.remove_widget(child)
        
        for group in self.db:
            if group['folder'] == 'root':
                basefolder = self.sources
            else:
                basefolder = join(self.sources, group['folder'])

            for pic in group['files']:
                filename = join(basefolder, pic)
                print filename
                parts = filename.rsplit('.', 1)
                if len(parts) != 2:
                    continue
                filename_suffix = '%s%s.%s' % (parts[0], self.suffix, parts[1])
                if group['folder'] == 'root':
                    image = ImageKeywordsGroup(source=filename,
                                    pos_hint={'x': 0, 'y': 0},
                                    source_original=filename,
                                    category=group['folder'],
                                    source_active=filename_suffix)
                    image.bind(active=self.on_group_active)
                else:
                    image = ImageKeywordsKey(source=filename,
                                    pos_hint={'x': 0, 'y': 0},
                                    source_original=filename,
                                    category=group['folder'],
                                    source_active=filename_suffix)
                    image.bind(active=self.on_key_active)
                    image.opacity = 0

                self.add_widget(image)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)

    
    def get_filename_id(self, filename):
        return filename.rsplit(sep, 1)[-1].rsplit('.', 1)[0]
    
    def on_key_active(self, instance, value):
        # print instance, value
        pass

    def on_group_active(self, instance, value):
        key = instance.key
        if value:
            if not key in self.selected_groups:
                self.selected_groups.append(key)
        else:
            if key in self.selected_groups:
                self.selected_groups.remove(key)

    def clear_all(self):
        for img in self.children:
            if img.active == True:
                img.set_active()
