from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ReferenceListProperty, NumericProperty, StringProperty, ObjectProperty


class SizeSlider(FloatLayout):
    bound_min = NumericProperty(0.0)
    value_min = NumericProperty(0.0)
    value_max = NumericProperty(1.0)
    value_range = ReferenceListProperty(value_min, value_max)
    text_min = StringProperty('')
    text_max = StringProperty('')
    padding = NumericProperty(0.0)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        self.update_from_touch(touch)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            touch.ungrab(self)
            return True

    def update_from_touch(self, touch):
        value = (touch.x - self.x + self.padding/2) / (self.width - self.padding)
        value = min(1.0, max(self.bound_min, value))
        value_center = (self.value_min + self.value_max) / 2.
        name = 'value_min' if value < value_center else 'value_max'
        setattr(self, name, value)

    def reset(self):
        self.value_min = self.bound_min
        self.value_max = 1

if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(SizeSlider(
        size_hint=(None, None),
        pos_hint={'right': 1, 'center_y': 0.5},
        size=(300, 600)
    ))

