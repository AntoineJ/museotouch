from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty


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


class QuizzItem(Scatter):

    #: Reference of the application
    app = ObjectProperty(None)
    
    #: Backend item reference
    item = ObjectProperty(None)

    #: Image filename to use
    source = StringProperty(None)

    #: Element that will contain the content/description
    container = ObjectProperty(None)

    #: Element created the first time the widget is flipped
    content = ObjectProperty(None)

    #: Border that can be used to draw outline 
    border = NumericProperty(5)

    #: For animation
    flip_alpha = NumericProperty(1.)
    flip_front = BooleanProperty(True)

    #: Button animation
    alpha_button = NumericProperty(0.)

    #: Touch counter
    counter = NumericProperty(0)

    #: Basket widget
    basket = ObjectProperty(None)

    #: Last touch_down to date
    last_touch_down_pos = ObjectProperty(None)

    #: Color
    color = ListProperty([1, 1, 1, 1])

    #: If we want a square img
    img_square = ObjectProperty(None)
    
    def __init__(self, *args, **kwargs):

        square = False
        if 'square' in kwargs and kwargs['square'] == True:
            square = True
            del kwargs['square']
        super(QuizzItem, self).__init__(**kwargs)
        self.on_start()
        if square:
            # Rognage => maximum square :
            my_ceil = lambda n: 0 if n < 0 else n
            L,H = self.img_square.texture.size
            x = my_ceil(L-H)/2
            y = my_ceil(H-L)/2
            w = min(L,H)
            h = min(L,H)
            self.img_square.texture = self.img_square.texture.get_region(x, y, w, h)

    def on_start(self):
        #Replace this function in init.py to personnalize dynamically an image item 
        pass

    def on_touch_down(self, touch): 
        ret = super(QuizzItem, self).on_touch_down(touch)
        if not ret:
            return

        return True
    
    def on_touch_move(self, touch):
        ret = super(QuizzItem,self).on_touch_move(touch)

        return ret

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        ret = super(QuizzItem, self).on_touch_up(touch)


        return ret

    def flip(self):
        self.flip_front = not self.flip_front
        # first time ? create content

    def on_flip_front(self, instance, value):
        self.color[3] = 1
        # do animation ?
        alpha = 1. if value else 0.
        k = {}
        if self.app.mode == 'mobile':
            k['rotation'] = 0
            if not self.flip_front:
                scale = max(1., self.scale)
            else:
                scale = min(.30, self.scale)
            k['scale'] = scale
        else:
            if not self.flip_front:
                scale = max(1., self.scale)
                k['scale'] = scale
        if is_android:
            k['rotation'] = 0.
        Animation(flip_alpha=alpha,
            t='out_quad', d=0.3, **k).start(self)

    def ensure_content(self):
        if self.content is not None:
            return
        self.content = QuizzItemContent(item=self.item,
                flip_alpha=self.flip_alpha, QuizzItem=self)

    def on_flip_alpha(self, instance, value):
        content = self.content
        if content is None and value != 1:
            self.ensure_content()
            content = self.content

        if value == 1 and content is not None:
            self.container.remove_widget(content)
        elif content not in self.container.children:
            self.container.add_widget(content)
        content.flip_alpha = value

    def on_btn_close(self, *largs):
        # called when close button have been released
        if self.alpha_button < 0.8:
            return
        self.parent.remove_widget(self)

    def on_btn_moreinfo(self, *largs):
        # called when moreinfo button have been released
        print 'moreinfo button released'
        if self.alpha_button < 0.8:
            return
        self.flip()

    def collide_point(self, x, y):
        # custom collision. some button are outside widget, so check if
        # collision can happen on them too.
        x, y = self.to_local(x, y)
        ret = 0 <= x <= self.width and 0 <= y <= self.height
        if ret:
            return ret
        for child in self.children:
            ret = child.collide_point(x, y)
            if ret:
                return ret
        return False

    def on_center(self, instance, value):
        parent = self.parent
        if not parent:
            return
        # causing problems when the item scale was too important
        # x, y = value
        # x = max(parent.x, x)
        # y = max(parent.y, y)
        # x = min(parent.right, x)
        # y = min(parent.top, y)
        # self.center = x, y

    def on_parent(self, instance, value):
        if value is None and self.content:
            self.content.stop()





def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    # -------------------------------------------------------------------------
    # Add a date slider to our root widget.
    print '***********************'
    print dir(app.db.items)
    print '***********************'

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

