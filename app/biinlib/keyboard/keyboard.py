#:kivy 1.8

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.button import Button
from json import load
from os.path import dirname,abspath, join, isfile
from kivy.graphics import Color, Rectangle
from kivy.uix.scatter import Scatter
from kivy.animation import Animation

class Key(Button):
	wd = NumericProperty(1)
	hgt = NumericProperty(1)
	wd_fix = NumericProperty(1)
	hgt_fix = NumericProperty(1)
	centre = ObjectProperty([1,2])
	img = StringProperty('')


class Keyboard(Scatter):
	"""Custom keyboard with input text"""

	# label to show the input string
	label_text = ObjectProperty(None) 

	# clear button near to label_text
	btnClear = ObjectProperty(None)

	# filename of the layout's JSON 
	layout_filename = StringProperty('layout.json')

	# layout data read from the JSON file (layout_filename)
	layout = ObjectProperty(None)

	# If true use the alternative layout
	alternative = BooleanProperty(False) 

	# List of all the keys
	keys = ListProperty(None)

	def __init__(self, **kwargs):
		self.register_event_type('on_input')
		super(Keyboard, self).__init__(**kwargs)
		self.size = (240,420)

		curdir = dirname(__file__)
		self.layout_filename = join(curdir, 'layout.json')

		# self.label_text = Label(text='',
		# 			font_size = 36, 
		# 			color = (0,0,0,1),
		# 			# shorten = True,
		# 			text_size = (self.size[0] - 60 - 22, 50),
		# 			size = (self.size[0] - 60 - 22, 50),
		# 			size_hint = (None, None),
		# 			pos = (self.pos[0] + 30, self.pos[1] + self.size[1] - 50),
		# 			pos_hint = {},
		# 			valign = 'middle',
		# 			halign = 'center',
		# 			font_name = join(curdir, 'ProximaNova-Thin-webfont.ttf'))

		self.btnClear = Button(text='x',
								size = (20, 48), 
								size_hint = (None, None),
								# center = (self.pos[0] + self.size[0] - 30 - 22.5/2,self.pos[1] + self.size[1] - 45/2),
								# pos = (self.pos[0] + self.size[0] - 30, self.pos[1] + 9*self.size[1]/10), 
								border = [0,0,0,0],
								background_normal = join(curdir,'btn.png'),
								background_down = join(curdir,'btn_down.png'),
								background_color = [0.8,0.8,0.8,1],
								color = [0,0,0,1])

		self.btnClear.center = (self.pos[0] + self.size[0] - 30 - 24/2.,self.pos[1] + self.size[1] - 50/2)

		self.btnClear.bind(on_press = self.clear_text)

		self.load_layout()
		self.generate()

		self.add_widget(self.btnClear)


		# self.add_widget(self.label_text)
	def on_input(self, *args):
		return True

	def load_layout(self):
		"""load the JSON file"""
		with open(self.layout_filename, 'r') as fd:
			self.layout = load(fd)

	def keyInput(self, key):
		"""manage the inputs. Here you can define an action for a specific key"""


		if key.prop[0] == 'input':
			if len(self.label_text.text) < 8:
				
				if not self.alternative:
					self.label_text.text += key.prop[4]
				else:
					self.label_text.text += key.prop[6]
				self.dispatch('on_input', self.label_text.text)
		elif key.prop[0] == 'back':
			if len(self.label_text.text) > 0:
				self.label_text.text = self.label_text.text[0:len(self.label_text.text) - 1] #moche mais fait le taf
				self.dispatch('on_input', self.label_text.text)
		elif key.prop[0] == 'clear':
			self.clear_text()
		elif key.prop[0] == 'change':
			self.switch()

		# center_tmp = (key.center[0], key.center[1])
		# key.size = (key.size[0] + 15, key.size[1] + 15)
		# key.wd = key.wd + 15
		# key.hgt = key.hgt + 15
		Animation.stop_all(key)
		anim = Animation(wd = key.wd_fix + 15, hgt = key.hgt_fix + 15, duration = 0.1, t='out_circ')
		anim.start(key)
		# key.center = center_tmp

		parent = key.parent
		parent.remove_widget(key)
		parent.add_widget(key)

		key.background_color = [1,1,1,1]


	def keyRelease(self, key):
		# center_tmp = (key.center[0], key.center[1])
		# key.size = (key.size[0] - 15, key.size[1] - 15)
		# print key.pic.size
		# key.wd = key.wd - 15
		# key.hgt = key.hgt - 15
		Animation.stop_all(key)
		anim = Animation(wd = key.wd_fix, hgt = key.hgt_fix, duration = 0.1, t='out_circ')
		anim.start(key)
		# key.center = center_tmp
		key.background_color = self.layout['bgr_color'][key.prop[1]]

	def switch(self):
		"""switch keys to the alternative layout"""
		curdir = dirname(__file__)
		self.alternative = not self.alternative
		for key in self.keys:
			if not self.alternative:
				# key.canvas.after.clear()
				if (isfile(join(curdir, key.prop[3] + '.png'))):
					key.text = ' '
					key.img = join(curdir, key.prop[3] + '.png')
					# key.pic.color = [1,1,1,1]

					# with key.canvas.after:
					# 	Color(1,1,1,1)
					# 	Rectangle(size = key.size, pos = key.pos, source = join(curdir, key.prop[3] + '.png'))

				else:
					key.text = key.prop[3]
					# key.pic.color = [0,0,0,0]
					key.img = ''

				if key.text == '':
					key.disabled = True
				else:
					key.disabled = False
			else:
				# key.canvas.after.clear()
				if (isfile(join(curdir,  key.prop[5] + '.png'))):
					key.text = ' '
					key.img = join(curdir, key.prop[5] + '.png')
					# key.pic.color = [1,1,1,1]
					# with key.canvas.after:
					# 	Color(1,1,1,1)
					# 	Rectangle(size = key.size, pos = key.pos, source = join(curdir, key.prop[5] + '.png'))

				else:
					key.text = key.prop[5]
					key.img = ''
					# key.pic.color = [0,0,0,0]
				if key.text == '':
					key.disabled = True
				else:
					key.disabled = False

	def generate(self):
		"""Generate buttons"""
		# Width of a key
		w = (self.size[0]-60) / self.layout['cols']
		
		# Height of a key
		# h = 9*self.size[1]/(10 * self.layout['rows'])

		curdir = dirname(__file__)
		j = 0
		h_tmp = 0 #s'incremente pour connaitre la pos des touches
		for i in range(0, self.layout['rows']):
			j=0
			h = self.layout['button'][i][0]
			w_tmp = 0
			h_tmp += h
			for key_prop in self.layout['button'][i]:
				if isinstance(key_prop, (int, float, long, complex)): #the first item is the height of the row
					continue
				key = Key(text = key_prop[3], 
								wd = w * key_prop[2],
								hgt = h,
								wd_fix = w * key_prop[2],
								hgt_fix = h,

								centre = (self.pos[0] + 30 + w_tmp + w * key_prop[2]/2, self.pos[1] + 30 + h_tmp - h/2),
								# size = (w * key_prop[2] - 2, h - 2),
								# size_hint = (None, None),
								# pos = (self.pos[0] + j*w, self.pos[1] + i * h),
								# border = [0,0,0,0],
								# background_normal = join(curdir,'special-carac-icon.png'),
								# background_normal = join(curdir,'btn.png'),
								# background_disabled_normal = join(curdir,'btn.png'),
								# background_disabled_down = join(curdir,'btn.png'),
								# background_down = join(curdir,'btn.png'),
								# background_color = [0,0,0,0],
								background_color = self.layout['bgr_color'][key_prop[1]],
								color = [0,0,0,1])
								# font_size = h / 2)
								# font_name = join(curdir, 'ProximaNova-Thin-webfont.ttf' ))



				# key.center = (self.pos[0] + 30 + j*45 + 45/2, self.pos[1] + 30 + i*45 + 45/2)
				# key.centre = (self.pos[0] + 30 + w_tmp + w * key_prop[2]/2, self.pos[1] + 30 + h_tmp - h/2)

				

				if (isfile(join(curdir, key_prop[3] + '.png'))):
					key.text = ' '
					key.img = join(curdir, key_prop[3] + '.png')
					# key.pic.color = [1,1,1,1]
					# with key.canvas.after:
					# 	Color(1,1,1,1)
					# 	Rectangle(size = key.size, pos = key.pos, source = join(curdir, key_prop[3] + '.png'))



				key.prop = key_prop

				w_tmp += w * key_prop[2]

				key.bind(on_press = self.keyInput)
				key.bind(on_release = self.keyRelease)

				if key.text == '':
					key.disabled = True
				else:
					key.disabled = False

				j += key_prop[2]

				self.add_widget(key, 0)
				self.keys.append(key)





	def clear_text(self, *args):
		"""Clear the input text"""

		self.label_text.text = ''
		self.dispatch('on_input', self.label_text.text)

	def get_text(self):
		"""Return the input text"""
		return self.label_text.text



