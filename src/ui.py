import pygame
from pygame.locals import *
import pygame.freetype

from logs import Logs

def printf(args):
	Logs.print('ui',args)

def get_image(size, place):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey((255, 255, 255))
	return tmp


class UI:

	dict = {}

	new_rects = []
	last_rects = []

	focused = None

	COLOR_LOCKED = (60, 60, 60), (10, 14, 17), (0, 0, 0)
	COLOR_DOWN = (0, 93, 67), (0, 66, 47), (0, 50, 27)
	COLOR_HOVERED = (93, 67, 0), (66, 47, 0), (50, 27, 0)
	COLOR_CLASSIC = (90, 90, 90), (60, 60, 60), (30, 30, 30)

	FONT = None
	BOLD_FONT = None

	last_clicked = True

	clicked_up = False
	clicked_down = False

	clicked_down_pos = None

	def __init__(self, name, pos, size, hoverable, locked, text="ERROR", font_type=1):
		cls = self.__class__

		self.pos = pos
		self.name = name
		self.size = size
		self.rect = pygame.Rect((pos[0], pos[1]), (size[0], size[1]))
		self.locked = locked

		self.down = False
		self.clickedUp = False
		self.hoverable = hoverable
		self.hovered = False

		if cls.has_text:
			self.default_text = text
			self.current_text = text
			self.font = self.adapted_font(font_type)

		UI.dict[cls.__name__][name] = self

	def adapted_font(self, font_type):
		if font_type == 1:
			return UI.FONT
		return UI.BOLD_FONT

	@classmethod
	def setup_subclasses(cls):
		for subcls in cls.__subclasses__():
			cls.dict[subcls.__name__] = {}
	
	def setup_language(tr):
		Button.CONFIRM_TEXT = tr.confirm
	
	@classmethod
	def delete(cls, *names):
		current_keys = UI.dict[cls.__name__].keys()
		for name in names:
			if name in current_keys:
				if UI.dict[cls.__name__][name] == UI.focused:
					UI.focused = None
				del UI.dict[cls.__name__][name]
	
	@classmethod
	def delete_all(cls):
		names = UI.dict[cls.__name__].keys()
		for name in names:
			if UI.dict[cls.__name__][name] == UI.focused:
				UI.focused = None
		UI.dict[cls.__name__] = {}
	
	@classmethod
	def exists(cls, name):
		return (name in UI.dict[cls.__name__].keys())
	
	@classmethod
	def ex_and_clicked(cls, name):
		return cls.exists(name) and UI.dict[cls.__name__][name].clickedUp
	
	@classmethod
	def ex_and_confirmed(cls, name):
		return cls.exists(name) and UI.dict[cls.__name__][name].confirmed
	
	@classmethod
	def ex_and_hovered(cls, name):
		return cls.exists(name) and UI.dict[cls.__name__][name].hovered
	
	@classmethod
	def clicked(cls, name):
		return UI.dict[cls.__name__][name].clickedUp
	
	@classmethod
	def lock(cls, name):
		UI.dict[cls.__name__][name].locked = True
	
	@classmethod
	def unlock(cls, name):
		UI.dict[cls.__name__][name].locked = False
	
	@classmethod
	def set_lock(cls, name, val):
		UI.dict[cls.__name__][name].locked = val
	
	@classmethod
	def confirmed(cls, name):
		return UI.dict[cls.__name__][name].confirmed
	
	def update_mouse_state(pressed):
		UI.clicked_down = (pressed and not UI.last_clicked)
		UI.clicked_up = (not pressed and UI.last_clicked)
		UI.last_clicked = pressed
	
	def update(window, x, y, pressed):
		UI.last_rects = UI.new_rects.copy()
		UI.new_rects = []
		UI.update_mouse_state(pressed)
		for cls in UI.__subclasses__():
			for key in UI.dict[cls.__name__]:
				self = UI.dict[cls.__name__][key]
				self.mouse_relative_update(x, y)
				if hasattr(self, 'on_logic_update'):
					self.on_logic_update(x, y)
				self.on_update(window)
		if not UI.last_clicked:
			if not (hasattr(UI.focused, 'need_confirmation') and UI.focused.need_confirmation and UI.focused.down):
				UI.focused = None
	
	def get_color_from_code(self, val):
		if self.locked:
			return UI.COLOR_LOCKED[val]
		elif self.down:
			return UI.COLOR_DOWN[val]
		elif self.hovered:
			return UI.COLOR_HOVERED[val]
		else:
			return UI.COLOR_CLASSIC[val]
	
	def get_third_color(self):
		return self.get_color_from_code(2)
	
	def get_second_color(self):
		return self.get_color_from_code(1)

	def get_first_color(self):
		return self.get_color_from_code(0)
	
	def mouse_relative_update(self, x, y):
		self.clickedUp = False
		self.hovered = False

		self.hovered = self.rect.collidepoint(x,y)

		if UI.clicked_down and self.hovered:
			UI.focused = self

		if UI.clicked_up and not self.hovered:
			self.clickedUp = False
			if self == UI.focused:
				UI.focused = None
		
		self.down = self.hovered and (UI.last_clicked or UI.clicked_up)
		
		if UI.clicked_up and self.down and not self.locked:
			self.clickedUp = True
		
		if self == UI.focused and not self.locked:
			self.down = True

		if UI.focused != None and UI.focused != self:
			self.down = False
			self.clickedUp = False
			self.hovered = False


class Button(UI):

	has_text = True

	thickness = 3

	CONFIRM_TEXT = None
	
	def __init__(self, name, pos=(100, 100), size=(300, 40), text="ERROR", hoverable=True, locked=False, font_type=1, need_confirmation=False):
		UI.__init__(self, name, pos, size, hoverable, locked, text, font_type)
		self.im_dict = self.setup()
		self.need_confirmation = need_confirmation
		self.confirmed = False
		self.first_click = False
	
	def setup(self):
		thickness = Button.thickness

		locked = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[1], (thickness, thickness,self.size[0]-2*thickness, self.size[1]-2*thickness),border_radius=8)
		
		down = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(down, UI.COLOR_DOWN[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(down, UI.COLOR_DOWN[1], (thickness, thickness,self.size[0]-2*thickness, self.size[1]-2*thickness),border_radius=8)
		
		hovered = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[1], (thickness, thickness,self.size[0]-2*thickness, self.size[1]-2*thickness),border_radius=8)
		
		classic = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[1], (thickness, thickness,self.size[0]-2*thickness, self.size[1]-2*thickness),border_radius=8)

		locked = locked.convert_alpha()
		down = down.convert_alpha()
		hovered = hovered.convert_alpha()
		classic = classic.convert_alpha()
		return {'locked':locked, 'down':down, 'hovered':hovered, 'classic':classic}
	
	def set_text(name, value):
		UI.dict[Button.__name__][name].current_text = value
		UI.dict[Button.__name__][name].default_text = value
	
	def on_logic_update(self, x, y):
		self.confirmed = False
		if self.need_confirmation and self.clickedUp:
			if not self.first_click:
				self.first_click = True
				self.current_text = Button.CONFIRM_TEXT
			else:
				self.first_click = False
				self.confirmed = True
				self.current_text = self.default_text
				if UI.focused == self:
					UI.focused = None

		if UI.clicked_up and not self.hovered:
			self.first_click = False
			self.confirmed = False
			if self.need_confirmation:
				self.current_text = self.default_text
		
		if UI.focused != None and UI.focused != self:
			self.confirmed = False
			
	
	def on_update(self, window):
		rect = (*self.pos, *self.size)
		UI.new_rects.append(rect)

		if self.locked:
			window.blit(self.im_dict['locked'], (rect[0], rect[1]))
		elif self.down or self.first_click:
			window.blit(self.im_dict['down'], (rect[0], rect[1]))
		elif self.hovered and self.hoverable:
			window.blit(self.im_dict['hovered'], (rect[0], rect[1]))
		else:
			window.blit(self.im_dict['classic'], (rect[0], rect[1]))
		
		color = (255, 255, 255)
		if self.locked:
			color = (70, 70, 70)
		text = self.font.render(self.current_text, color)

		rect = (self.pos[0]+self.size[0]//2-text[1].width//2, self.pos[1]+self.size[1]//2-text[1].height//2, *text[0].get_size())
		UI.new_rects.append(rect)
		window.blit(text[0], (rect[0], rect[1]))


class ImageButton(UI):

	has_text = False

	thickness = 3

	extern_thickness = 1
	intern_thickness = 2
	
	def __init__(self, name, image_path, pos=(100, 100), size=(50, 50), hoverable=True, locked=False):
		UI.__init__(self, name, pos, size, hoverable, locked)
		thickness, intern_thickness, extern_thickness = ImageButton.thickness, ImageButton.intern_thickness, ImageButton.extern_thickness
		self.im_size = (size[0]-2*thickness - 2*intern_thickness - 2*extern_thickness, size[1]-2*thickness - 2*intern_thickness -2*extern_thickness)
		self.mask_size = (size[0]-2*thickness-2*extern_thickness, size[1]-2*thickness-2*extern_thickness)
		self.set_image(image_path)
	
	def set_image(self, image_path):
		self.image = get_image(self.im_size, image_path)
		self.setup()

	def set_button_image(name, image_path):
		UI.dict[ImageButton.__name__][name].set_image(image_path)

	def setup(self):
		thickness, intern_thickness, extern_thickness = ImageButton.thickness, ImageButton.intern_thickness, ImageButton.extern_thickness

		locked = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[1], (thickness, thickness, self.size[0] - 2*thickness, self.size[1] -2*thickness),border_radius=8)
		locked.blit(self.image, (thickness + intern_thickness + extern_thickness, thickness + intern_thickness + extern_thickness))
		mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
		pygame.draw.rect(mask, (10, 14, 17, 120), (0, 0, *self.mask_size),border_radius=8)
		locked.blit(mask, (thickness + extern_thickness, thickness + extern_thickness))

		down = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(down, UI.COLOR_DOWN[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(down, UI.COLOR_DOWN[1], (thickness, thickness, self.size[0] - 2*thickness, self.size[1] -2*thickness),border_radius=8)
		down.blit(self.image, (thickness + intern_thickness + extern_thickness, thickness + intern_thickness + extern_thickness))
		mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
		pygame.draw.rect(mask, (255, 255, 255, 40), (0, 0, *self.mask_size),border_radius=8)
		down.blit(mask, (thickness + extern_thickness, thickness + extern_thickness))

		hovered = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[1], (thickness, thickness, self.size[0] - 2*thickness, self.size[1] -2*thickness),border_radius=8)
		hovered.blit(self.image, (thickness + intern_thickness + extern_thickness, thickness + intern_thickness + extern_thickness))
		mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
		pygame.draw.rect(mask, (255, 255, 255, 20), (0, 0, *self.mask_size),border_radius=8)
		hovered.blit(mask, (thickness + extern_thickness, thickness + extern_thickness))

		classic = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[0], (0, 0, self.size[0], self.size[1]),border_radius=10)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[1], (thickness, thickness, self.size[0] - 2*thickness, self.size[1] -2*thickness),border_radius=8)
		classic.blit(self.image, (thickness + intern_thickness + extern_thickness, thickness + intern_thickness + extern_thickness))

		locked = locked.convert_alpha()
		down = down.convert_alpha()
		hovered = hovered.convert_alpha()
		classic = classic.convert_alpha()
		self.im_dict = {'locked':locked, 'down':down, 'hovered':hovered, 'classic':classic}
	
	def on_update(self, window):
		rect = (*self.pos, *self.size)
		UI.new_rects.append(rect)

		if self.locked:
			window.blit(self.im_dict['locked'], (rect[0], rect[1]))
		elif self.down:
			window.blit(self.im_dict['down'], (rect[0], rect[1]))
		elif self.hovered and self.hoverable:
			window.blit(self.im_dict['hovered'], (rect[0], rect[1]))
		else:
			window.blit(self.im_dict['classic'], (rect[0], rect[1]))


class Slider(UI):

	has_text = False

	thickness = 3

	COLOR_TICK = (200, 200, 200)
	COLOR_BUTTON_SIDE = (10, 14, 18)
	
	def __init__(self, name, pos, size, hoverable=True, locked=False, default_value=7, values=(0, 10), ticks=0):
		UI.__init__(self, name, pos, size, hoverable, locked)
		self.a, self.b = values
		if ticks > 0:
			self.step = (self.b - self.a) / ticks
		self.radius = (size[1] - 2 * Slider.thickness) / 2
		self.center_width = self.size[0] - 2 * self.radius - 2 * Slider.thickness
		self.default_value = default_value
		self.value = default_value
		self.ticks = ticks
		self.im_dict = self.setup()
		
	def on_value_changed(self):
		pass
	
	def setup(self):
		thickness = Slider.thickness
		radius = int(self.radius)
		size = self.size

		locked = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[0], (0, 0, *size), border_radius=radius)
		pygame.draw.rect(locked, UI.COLOR_LOCKED[1], (thickness, thickness, size[0] - 2 * thickness, size[1] - 2 * thickness), border_radius=radius)

		down = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(down, UI.COLOR_DOWN[0], (0, 0, *size), border_radius=radius)
		pygame.draw.rect(down, UI.COLOR_DOWN[1], (thickness, thickness, size[0] - 2 * thickness, size[1] - 2 * thickness), border_radius=radius)

		hovered = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[0], (0, 0, *size), border_radius=radius)
		pygame.draw.rect(hovered, UI.COLOR_HOVERED[1], (thickness, thickness, size[0] - 2 * thickness, size[1] - 2 * thickness), border_radius=radius)

		classic = pygame.Surface(self.size, pygame.SRCALPHA)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[0], (0, 0, *size), border_radius=radius)
		pygame.draw.rect(classic, UI.COLOR_CLASSIC[1], (thickness, thickness, size[0] - 2 * thickness, size[1] - 2 * thickness), border_radius=radius)

		locked = locked.convert_alpha()
		down = down.convert_alpha()
		hovered = hovered.convert_alpha()
		classic = classic.convert_alpha()
		return {'locked':locked, 'down':down, 'hovered':hovered, 'classic':classic}

	def update_value(self, x):
		x = x - self.pos[0] - self.radius - Slider.thickness
		x = x * (self.b - self.a) / self.center_width
		val = x + self.a
		self.value = self.nearest_value(val)
	
	def nearest_value(self, val):
		k = max(0, round((val - self.a) / self.step))
		return min(self.a + k * self.step, self.b)
	
	def get_button_pos(self):
		val = (self.value - self.a) * self.center_width / (self.b - self.a)
		return self.pos[0] + Slider.thickness + self.radius + val
	
	def get_tick_color(self, tick_value):
		if tick_value > self.value:
			return Slider.COLOR_TICK
		else:
			return self.get_second_color()
	
	def display(self, surface):
		x = self.get_button_pos()

		if self.value != self.a:
			pygame.draw.rect(surface, self.get_third_color(), (self.pos[0] + Slider.thickness, self.pos[1] + Slider.thickness, x - self.pos[0] - Slider.thickness, self.size[1] - 2 * Slider.thickness), 
			border_bottom_left_radius=int(self.radius), border_top_left_radius=int(self.radius))

		if self.ticks:
			for tick in range(1, self.ticks):
				value = self.a + tick * self.step
				normed_value = (value - self.a) / int((self.b - self.a))
				pos = Slider.thickness + self.radius + normed_value * self.center_width
				pygame.draw.line(surface, self.get_tick_color(value), (self.pos[0] + pos, self.pos[1] + Slider.thickness), (self.pos[0] + pos, self.pos[1] + self.size[1] - Slider.thickness-1), width=2)
		
		pygame.draw.circle(surface, Slider.COLOR_BUTTON_SIDE, (x, self.pos[1] + self.size[1] / 2), self.radius)
		pygame.draw.circle(surface, self.get_first_color(), (x, self.pos[1] + self.size[1] / 2), self.radius - 2)

	def on_logic_update(self, x, y):
		if self == UI.focused and not self.locked:
			self.update_value(x)
	
	def on_update(self, window):
		rect = (*self.pos, *self.size)
		UI.new_rects.append(rect)

		if self.locked:
			window.blit(self.im_dict['locked'], (rect[0], rect[1]))
		elif self.down:
			window.blit(self.im_dict['down'], (rect[0], rect[1]))
		elif self.hovered and self.hoverable:
			window.blit(self.im_dict['hovered'], (rect[0], rect[1]))
		else:
			window.blit(self.im_dict['classic'], (rect[0], rect[1]))
		
		self.display(window)


class CheckBox(UI):

	has_text = True
	
	def __init__(self, name, pos, size, text="ERROR", hoverable=True, locked=False, font_type=1):
		UI.__init__(self, name, pos, size, hoverable, locked, text, font_type)
	
	def setup(self):
		pass

	def on_update(self, window, x, y, pressed, clicked_up):
		pass


class RadioButton(UI):

	has_text = True
	
	def __init__(self, name, pos, size, text="ERROR", hoverable=True, locked=False, font_type=1):
		UI.__init__(self, name, pos, size, hoverable, locked, text, font_type)
	
	def setup(self):
		pass

	def on_update(self, window, x, y, pressed, clicked_up):
		pass



if __name__ == '__main__':
	UI.setup_subclasses()

	pygame.init()

	WIDTH, HEIGHT = 800, 800

	UI.FONT = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", 24)
	UI.BOLD_FONT = pygame.freetype.Font("fonts/MonoglycerideBold.ttf", 19)

	SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("UI Elements Tests")
	clock = pygame.time.Clock()

	execute = True

	last_click_state = False
	clicked_up = False

	Slider('test', (20, 20), (300, 28), ticks=10)
	Slider('test2', (20, 68), (300, 28), ticks=20)

	Button.CONFIRM_TEXT = "Confirm ?"

	Button('test', (340, 20), text="Classic")
	Button('test2', (340, 80), text="No hover", hoverable=False)
	Button('test3', (340, 140), text="Small font", font_type=0)
	Button('test4', (340, 200), text="Need confirmation", need_confirmation=True)
	Button('locked', (340, 260), text="Locked", locked=True)

	while execute:
		SCREEN.fill((10, 14, 18))

		pressed_mouse_keys = pygame.mouse.get_pressed()
		current_click_state = pressed_mouse_keys[0]

		if Button.clicked('test'):
			printf("Button 1 pushed")
		
		if Button.clicked('test2'):
			printf("Button 2 pushed")
		
		if Button.clicked('test3'):
			printf("Button 3 pushed")
		
		if Button.clicked('test4'):
			printf("Button 4 clicked")
		if Button.confirmed('test4'):
			printf("Button 4 confirmed")
		
		if Button.clicked('locked'):
			printf("Locked button pushed")

		x, y = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == QUIT:
				execute = False
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					execute = False
		
		UI.update(SCREEN, x, y, current_click_state)
		pygame.display.update()
		clock.tick(60)

		last_click_state = current_click_state