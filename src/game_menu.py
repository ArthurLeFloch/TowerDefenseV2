import pygame
from towers import Tower
from logs import Logs
from tower_description import InstanceDescription

def printf(args):
	Logs.print('game_menu',args)

WHITE = (255, 255, 255)

def glow(img):
	surface = pygame.Surface(
		(img.get_width() + 2, img.get_height() + 2), pygame.SRCALPHA)
	mask = pygame.mask.from_surface(img)
	mask_surf = mask.to_surface()
	mask_surf.set_colorkey((0, 0, 0))
	surface.blit(mask_surf, (0, 1))
	surface.blit(mask_surf, (2, 1))
	surface.blit(mask_surf, (1, 0))
	surface.blit(mask_surf, (1, 2))
	surface.blit(img, (1, 1))
	return surface

def get_image(size, place, glowing=False):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey(WHITE)
	if glowing:
		return glow(tmp)
	return 

def format_money(amount, separator=','):
	amount = int(amount)
	if amount == 0:
		return "$ 0"
	result = ""
	i = 0
	while amount != 0:
		if i and i % 3 == 0:
			result = separator + result
		number = amount % 10
		amount = amount // 10
		result = str(number) + result
		i += 1
	return "$ " + result

def is_on_rect(pos, rect):
	# Rect : top left x,y and width, height
	x, y = pos
	b1 = rect[0][0] <= x <= rect[0][0]+rect[1]
	b2 = rect[0][1] <= y <= rect[0][1]+rect[2]
	return b1 and b2

class Menu:

	#region CONSTANTS
	
	BOLD = None
	FONT = None

	# Setting up LEVEL layout
	LEVEL_POS = None

	LEVEL_HOR_MARGIN = 4
	LEVEL_VER_MARGIN = 4

	LEVEL_WIDTH = None
	LEVEL_HEIGHT = 90

	LEVEL_ICON_WIDTH = 50
	LEVEL_ICON_HEIGHT = 50

	LEVEL_BAR_POS = None
	LEVEL_BAR_WIDTH = None
	LEVEL_BAR_HEIGHT = 10
	LEVEL_BAR_HOR_MARGIN = 8
	LEVEL_BAR_VER_MARGIN = 8

	# Setting up COIN layout
	COIN_POS = None

	COIN_HOR_MARGIN = 4
	COIN_VER_MARGIN = 4

	COIN_WIDTH = None
	COIN_HEIGHT = 70

	COIN_ICON_WIDTH = 50
	COIN_ICON_HEIGHT = 48

	# Setting up WAVE layout
	WAVE_POS = None

	WAVE_HOR_MARGIN = 4
	WAVE_VER_MARGIN = 4

	WAVE_WIDTH = None
	WAVE_HEIGHT = 60

	RECT_WAVE_PAUSE = None

	# Setting up SPEED layout
	SPEED_POS = None

	SPEED_HOR_MARGIN = 4
	SPEED_VER_MARGIN = 4

	SPEED_WIDTH = None
	SPEED_HEIGHT = 40

	RECT_SPEED_UP = None
	RECT_SPEED_DOWN = None

	# Setting up LIFE layout
	LIFE_POS = None

	LIFE_HOR_MARGIN = 4
	LIFE_VER_MARGIN = 4

	LIFE_PADDING = 5
	LIFE_INTERN_WIDTH = 16

	LIFE_WIDTH = LIFE_INTERN_WIDTH + 2 * LIFE_PADDING
	LIFE_HEIGHT = None

	LIFEMAX = 20

	# Setting up SHOP layout
	SHOP_POS = None

	SHOP_HOR_MARGIN = 4
	SHOP_VER_MARGIN = 4

	SHOP_WIDTH = None
	SHOP_HEIGHT = None
	
	SHOP_MAX_TAB = None

	SHOP_IMAGE_SIZE = (48, 48)

	# Setting up button rects
	RECT_UPGRADE = None
	RECT_DELETE = None

	RECT_STATS = None
	RECT_BSTATS = None

	RECT_BOOST1 = None
	RECT_BOOST2 = None

	BOOST_POS = None

	#endregion
	
	def __init__(self, pos, size):
		self.pos = pos
		self.width, self.height = size
		self.size = size

		self.val_coin = -1
		self.val_life = -1
		self.val_xp_ratio = -1
		self.val_level = -1
		self.val_wave = -1
		self.val_speed = -1

		self.boost1_text = None
		self.boost2_text = None

		self.upgrade_desc = None

		self.shop_items = []

		self.setup()
	
	#region SETUP
	
	def setup(self):
		self.setup_constants()

		self.setup_level()
		self.setup_coin()
		self.setup_wave()
		self.setup_speed()
		self.setup_lifebar()
		self.setup_shop()
		self.setup_boost_option()

		self.update_val_level(0)
		self.update_val_xp_ratio(0)
		self.update_val_coin(0)
		self.update_val_wave(0)
		self.update_val_speed(1)
		self.update_val_life(0)
	
	def update(self, screen):
		self.update_level(screen)
		self.update_coin(screen)
		self.update_wave(screen)
		self.update_speed(screen)
		self.update_lifebar(screen)

	def setup_constants(self):
		width, height = self.size
		x, y = self.pos

		# Setting up LEVEL constants
		Menu.LEVEL_POS = (x + Menu.LEVEL_HOR_MARGIN, y + Menu.LEVEL_VER_MARGIN)
		Menu.LEVEL_WIDTH = width - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 2 * Menu.LEVEL_HOR_MARGIN

		Menu.LEVEL_BAR_POS = (x + 16, y+Menu.LEVEL_HEIGHT - Menu.LEVEL_VER_MARGIN - Menu.LEVEL_BAR_HEIGHT - 4)
		Menu.LEVEL_BAR_WIDTH = width - 2 * Menu.LEVEL_BAR_HOR_MARGIN - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 16
		
		# Setting up COIN constants
		Menu.COIN_POS = (x + Menu.COIN_HOR_MARGIN, y + Menu.LEVEL_HEIGHT + 2 * Menu.LEVEL_VER_MARGIN + Menu.COIN_VER_MARGIN)
		Menu.COIN_WIDTH = width - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 2 * Menu.COIN_HOR_MARGIN

		# Setting up WAVE constants
		Menu.WAVE_POS = (x + Menu.WAVE_HOR_MARGIN, y + Menu.LEVEL_HEIGHT + 2 * Menu.LEVEL_VER_MARGIN + Menu.COIN_HEIGHT + 2 * Menu.COIN_VER_MARGIN + Menu.WAVE_VER_MARGIN)
		Menu.WAVE_WIDTH = width - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 2 * Menu.WAVE_HOR_MARGIN
		tmp = 16*2 + 12
		Menu.RECT_WAVE_PAUSE = (Menu.WAVE_POS[0] + 10, Menu.WAVE_POS[1] + (Menu.WAVE_HEIGHT - tmp) / 2 - 2), (tmp, tmp)
		
		# Setting up SPEED constants
		Menu.SPEED_POS = (x + Menu.SPEED_HOR_MARGIN, y + Menu.LEVEL_HEIGHT + 2 * Menu.LEVEL_VER_MARGIN + Menu.COIN_HEIGHT + 2 * Menu.COIN_VER_MARGIN + Menu.WAVE_HEIGHT + 2 * Menu.WAVE_VER_MARGIN + Menu.SPEED_VER_MARGIN)
		Menu.SPEED_WIDTH = width - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 2 * Menu.SPEED_HOR_MARGIN

		xp, yp = Menu.SPEED_POS
		wp = Menu.SPEED_WIDTH
		Menu.RECT_SPEED_UP = (xp + 10, yp), (16*2 + 12, 15*2 + 12)
		Menu.RECT_SPEED_DOWN = (xp + wp - 10 - 44, yp), (16*2 + 12, 15*2 + 12)

		# Setting up LIFE constants
		Menu.LIFE_POS = (x + width - Menu.LIFE_HOR_MARGIN - Menu.LIFE_WIDTH, y + Menu.LIFE_VER_MARGIN)
		Menu.LIFE_HEIGHT = height - 2 * Menu.LIFE_VER_MARGIN

		# Setting up SHOP constants
		max_height = height - 8 - Menu.LEVEL_HEIGHT - Menu.COIN_HEIGHT - Menu.WAVE_HEIGHT - Menu.SPEED_HEIGHT - 2 * Menu.LEVEL_VER_MARGIN - 2 * Menu.COIN_VER_MARGIN - 2 * Menu.WAVE_VER_MARGIN - 2 * Menu.SPEED_VER_MARGIN - 8
		Menu.SHOP_ITEM_PER_TAB = int(max_height / Tower.SHOP_ELEMENT_MIN_HEIGHT)
		Menu.SHOP_ELEMENT_HEIGHT = max_height / Menu.SHOP_ITEM_PER_TAB
		Menu.SHOP_MAX_TAB = len(Tower.subclasses) / Menu.SHOP_ITEM_PER_TAB

		Menu.SHOP_POS = (x + Menu.SHOP_HOR_MARGIN, y + Menu.LEVEL_HEIGHT + 2 * Menu.LEVEL_VER_MARGIN + Menu.COIN_HEIGHT + 2 * Menu.COIN_VER_MARGIN + Menu.WAVE_HEIGHT + 2 * Menu.WAVE_VER_MARGIN + Menu.SPEED_HEIGHT + 2 * Menu.SPEED_VER_MARGIN + Menu.SHOP_VER_MARGIN)
		Menu.SHOP_HEIGHT = Menu.SHOP_ITEM_PER_TAB * Menu.SHOP_ELEMENT_HEIGHT + 6
		Menu.SHOP_WIDTH = width - Menu.LIFE_WIDTH - 2 * Menu.LIFE_HOR_MARGIN - 2 * Menu.SHOP_HOR_MARGIN

		# Setting up RECT constants
		swidth = Menu.SHOP_WIDTH
		x0 = Menu.SHOP_HOR_MARGIN
		Menu.RECT_UPGRADE = (x0 + x + 20, Menu.SHOP_HEIGHT + Menu.SHOP_POS[1] - Menu.SHOP_VER_MARGIN - 20 - 40 - 50), (swidth - 40, 40)
		Menu.RECT_DELETE = (x0 + x + 20, Menu.SHOP_HEIGHT + Menu.SHOP_POS[1] - Menu.SHOP_VER_MARGIN - 20 - 40), (swidth - 40, 40)

		y2 = Menu.SHOP_POS[1] + Menu.SHOP_IMAGE_SIZE[1]
		bwidth = (swidth-20) / 2 - 10
		Menu.RECT_STATS = (x0 + x + 10, y2 + 40), (bwidth, 40)
		Menu.RECT_BSTATS = (x0 + x + swidth - bwidth - 16, y2 + 40), (bwidth, 40)

		Menu.RECT_BOOST1 = (x0 + x + 20, y2 + 20 + 110), (swidth - 40, 40)
		Menu.RECT_BOOST2 = (x0 + x + 20, y2 + 20 + 230), (swidth - 40, 40)

		Menu.BOOST_POS = (x + 13, y2 + 80)

	#endregion

	#region LEVEL

	def setup_level(self):
		level = pygame.Surface((Menu.LEVEL_WIDTH, Menu.LEVEL_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(level, (0, 0, 0), (0, 0, Menu.LEVEL_WIDTH, Menu.LEVEL_HEIGHT), border_radius=10)
		pygame.draw.rect(level, (15, 21, 27), (1, 1, Menu.LEVEL_WIDTH - 6, Menu.LEVEL_HEIGHT - 6), border_radius=10)

		x, y = Menu.LEVEL_BAR_POS
		xp_ratio = pygame.Surface((Menu.LEVEL_BAR_WIDTH, Menu.LEVEL_BAR_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(xp_ratio, (0, 0, 0), (0, 0, Menu.LEVEL_BAR_WIDTH, Menu.LEVEL_BAR_HEIGHT), border_radius=10)
		pygame.draw.rect(xp_ratio, (55, 30, 100), (2, 2, Menu.LEVEL_BAR_WIDTH - 4, Menu.LEVEL_BAR_HEIGHT - 4), border_radius=7)

		xc, yc = (Menu.LEVEL_HOR_MARGIN + Menu.LEVEL_BAR_HOR_MARGIN, (Menu.LEVEL_HEIGHT - Menu.LEVEL_BAR_HEIGHT - Menu.LEVEL_BAR_VER_MARGIN) / 2)
		level_icon = get_image((Menu.LEVEL_ICON_WIDTH, Menu.LEVEL_ICON_HEIGHT), 'images/others/xp.png', glowing=True)
		level.blit(level_icon, (xc, yc - Menu.LEVEL_ICON_HEIGHT / 2 - 3))

		self.xpbar_rect = (2, 2, Menu.LEVEL_BAR_WIDTH - 4, Menu.LEVEL_BAR_HEIGHT - 4)

		x, y = Menu.LEVEL_POS
		self.level_textpos = (x + Menu.LEVEL_WIDTH - 16, y + (Menu.LEVEL_HEIGHT - Menu.LEVEL_BAR_HEIGHT - Menu.LEVEL_BAR_VER_MARGIN) / 2)

		self.level = level.convert_alpha()
		self.xp_ratio = xp_ratio.convert_alpha()
	
	def update_level(self, screen):
		screen.blit(self.level, Menu.LEVEL_POS)
		screen.blit(self.xp_bar, Menu.LEVEL_BAR_POS)
		self.update_level_text(screen)

	def update_level_text(self, screen):
		screen.blit(self.level_text, self.level_text_pos)
	
	def update_val_level(self, new):
		if self.val_level != new:
			self.val_level = new
			tmp = Menu.BOLD.render(f"Niveau {self.val_level}", WHITE)
			x, y = self.level_textpos
			width, height = tmp[0].get_size()
			self.level_text_pos = (x - width, y - height/2)
			self.level_text = tmp[0]
	
	def update_val_xp_ratio(self, new):
		if self.val_xp_ratio != new:
			self.val_xp_ratio = new

			xp_bar = self.xp_ratio.copy()
			x, y, width, height = self.xpbar_rect
			pygame.draw.rect(xp_bar, (114, 22, 224), (x, y, width * self.val_xp_ratio, height), border_radius=7)
			self.xp_bar = xp_bar.convert_alpha()

	#endregion

	#region COIN

	def setup_coin(self):
		coin = pygame.Surface((Menu.COIN_WIDTH, Menu.COIN_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(coin, (0, 0, 0), (0, 0, Menu.COIN_WIDTH, Menu.COIN_HEIGHT), border_radius=10)
		pygame.draw.rect(coin, (15, 21, 27), (1, 1, Menu.COIN_WIDTH - 6, Menu.COIN_HEIGHT - 6), border_radius=10)

		xc, yc = (Menu.COIN_HOR_MARGIN + 8, Menu.COIN_HEIGHT / 2)
		coin_icon = get_image((Menu.COIN_ICON_WIDTH, Menu.COIN_ICON_HEIGHT), 'images/others/coin.png', glowing=True)
		coin.blit(coin_icon, (xc, yc - Menu.COIN_ICON_HEIGHT / 2 - 3))

		x, y = Menu.COIN_POS
		self.coin_textpos = (x + Menu.COIN_WIDTH - 16, y + Menu.COIN_HEIGHT / 2)

		self.coin = coin.convert_alpha()
	
	def update_coin(self, screen):
		screen.blit(self.coin, Menu.COIN_POS)
		self.update_coin_text(screen)
	
	def update_coin_text(self, screen):
		screen.blit(self.coin_text, self.coin_text_pos)
	
	def update_val_coin(self, new):
		if self.val_coin != new:
			self.val_coin = new
			tmp = Menu.BOLD.render(format_money(self.val_coin), WHITE)
			x, y = self.coin_textpos
			width, height = tmp[0].get_size()
			self.coin_text_pos = (x - width, y - height/2)
			self.coin_text = tmp[0]

	#endregion

	#region WAVE

	def setup_wave(self):
		wave = pygame.Surface((Menu.WAVE_WIDTH, Menu.WAVE_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(wave, (0, 0, 0), (0, 0, Menu.WAVE_WIDTH, Menu.WAVE_HEIGHT), border_radius=10)
		pygame.draw.rect(wave, (15, 21, 27), (1, 1, Menu.WAVE_WIDTH - 6, Menu.WAVE_HEIGHT - 6), border_radius=10)

		x, y = Menu.WAVE_POS
		self.wave_textpos = (x + Menu.WAVE_WIDTH - 16, y + Menu.WAVE_HEIGHT / 2)

		self.wave = wave.convert_alpha()
	
	def update_wave(self, screen):
		screen.blit(self.wave, Menu.WAVE_POS)
		self.update_wave_text(screen)

	def update_wave_text(self, screen):
		screen.blit(self.wave_text, self.wave_text_pos)
	
	def update_val_wave(self, new):
		if self.val_wave != new:
			self.val_wave = new
			color = WHITE
			if self.val_wave % 5 == 0:
				color = (240, 20, 20)
			tmp = Menu.BOLD.render(f"Vague n° {self.val_wave}", color)
			x, y = self.wave_textpos
			width, height = tmp[0].get_size()
			self.wave_text_pos = (x - width, y - height/2)
			self.wave_text = tmp[0]

	#endregion

	#region SPEED

	def setup_speed(self):
		x, y = Menu.SPEED_POS
		self.speed_textpos = (x + Menu.SPEED_WIDTH / 2, y + Menu.SPEED_HEIGHT / 2)
	
	def update_speed(self, screen):
		self.update_speed_text(screen)

	def update_speed_text(self, screen):
		screen.blit(self.speed_text, self.speed_text_pos)
	
	def update_val_speed(self, new):
		if self.val_speed != new:
			self.val_speed = new
			tmp = Menu.FONT.render(f"Vitesse : {self.val_speed}", WHITE)
			x, y = self.speed_textpos
			width, height = tmp[0].get_size()
			self.speed_text_pos = (x - width/2, y - height/2)
			self.speed_text = tmp[0]

	#endregion
	
	#region LIFE

	def setup_lifebar(self):
		life = pygame.Surface((Menu.LIFE_WIDTH, Menu.LIFE_HEIGHT), pygame.SRCALPHA)
		pygame.draw.rect(life, (0, 0, 0), (0, 0, Menu.LIFE_WIDTH, Menu.LIFE_HEIGHT), border_radius=10)
		pygame.draw.rect(life, (60, 0, 10), (Menu.LIFE_PADDING,  Menu.LIFE_PADDING, Menu.LIFE_WIDTH - 2 * Menu.LIFE_PADDING, Menu.LIFE_HEIGHT - 2 * Menu.LIFE_PADDING), border_radius=7)
		
		self.life_rect = (Menu.LIFE_PADDING, Menu.LIFE_PADDING, Menu.LIFE_WIDTH - 2 * Menu.LIFE_PADDING, Menu.LIFE_HEIGHT - 2 * Menu.LIFE_PADDING)

		self.life = life.convert_alpha()
	
	def update_lifebar(self, screen):
		screen.blit(self.lifebar, Menu.LIFE_POS)
	
	def update_val_life(self, new):
		if self.val_life != new:
			self.val_life = new

			lifebar = self.life.copy()
			x, y, width, height = self.life_rect
			life_height = self.val_life / Menu.LIFEMAX * height
			
			pygame.draw.rect(lifebar, (30, 150, 40), (x, y + height - life_height, width, life_height), border_radius=7)

			self.lifebar = lifebar.convert_alpha()
	
	#endregion

	#region SHOP

	def setup_shop(self):
		right_tab = pygame.Surface((Menu.SHOP_WIDTH, Menu.SHOP_HEIGHT), pygame.SRCALPHA)

		self.shop_items_per_tab = Menu.SHOP_ITEM_PER_TAB
		pygame.draw.rect(right_tab, (0, 0, 0), (0, 0, Menu.SHOP_WIDTH, Menu.SHOP_HEIGHT), border_radius=10)
		pygame.draw.rect(right_tab, (15, 21, 27), (1, 1, Menu.SHOP_WIDTH - 6, Menu.SHOP_HEIGHT - 6), border_radius=10)
		self.right_tab = right_tab

		shop = right_tab.copy()
		for k in range(self.shop_items_per_tab):
			pygame.draw.line(shop, (0, 0, 0), (0, Menu.SHOP_ELEMENT_HEIGHT * (k + 1)), (Menu.SHOP_WIDTH, Menu.SHOP_ELEMENT_HEIGHT * (k + 1)), width=3)

		self.shop = shop.convert_alpha()

		self.setup_shop_items()
	
	def update_right_tab(self, screen):
		screen.blit(self.right_tab, Menu.SHOP_POS)
	
	def update_shop(self, screen):
		screen.blit(self.shop, Menu.SHOP_POS)
		fi = self.shop_first_item
		x, y = Menu.SHOP_POS
		for k in range(fi, min(fi + Menu.SHOP_ITEM_PER_TAB, self.shop_item_count)):
			data = self.shop_items[k]
			cls = data[0]
			if self.val_level < cls.ALLOWED_LEVEL[0]:
				screen.blit(data[1][2], (x, y + Menu.SHOP_ELEMENT_HEIGHT * (k - fi)))
			elif self.val_coin < cls.COST[0]:
				screen.blit(data[1][1], (x, y + Menu.SHOP_ELEMENT_HEIGHT * (k - fi)))
			else:
				screen.blit(data[1][0], (x, y + Menu.SHOP_ELEMENT_HEIGHT * (k - fi)))

	def setup_shop_items(self):
		self.shop_first_item = 0
		self.shop_item_count = len(Tower.subclasses)
		for cls in Tower.subclasses:
			self.shop_items.append(cls.shop_item(Menu.SHOP_WIDTH, Menu.SHOP_ELEMENT_HEIGHT))

	def shop_navigate(self, offset):
		if offset > 0:
			self.shop_first_item = min(max(0, self.shop_item_count - Menu.SHOP_ITEM_PER_TAB), self.shop_first_item + offset)
		else:
			self.shop_first_item = max(0, self.shop_first_item + offset)
	
	def shop_select_tower(self, xm, ym):
		x, y = Menu.SHOP_POS
		fi = self.shop_first_item
		for k in range(fi, min(fi + Menu.SHOP_ITEM_PER_TAB, self.shop_item_count)):
			data = self.shop_items[k]
			cls = data[0]
			if is_on_rect((xm, ym), ([x, y + Menu.SHOP_ELEMENT_HEIGHT * (k - fi)], Menu.SHOP_WIDTH, 90)) and self.val_coin >= cls.COST[0]:
				return cls
		
	#endregion

	# region TOWERS

	def setup_description_boosts(self, cls_im):
		y = Menu.SHOP_IMAGE_SIZE[1] + 20

		result = self.right_tab.copy()
		result.blit(cls_im, (Menu.SHOP_WIDTH / 2 - Menu.SHOP_IMAGE_SIZE[0] / 2, 20))
		x1, y1 = Menu.BOOST_POS
		result.blit(self.boost_options, (x1 - Menu.SHOP_POS[0], y1 - Menu.SHOP_POS[1]))

		txt = "Veuillez choisir un BOOST :"
		txt_im = Menu.FONT.render(txt, WHITE)
		w = txt_im[0].get_width()
		pos = Menu.SHOP_WIDTH / 2 - w / 2, y + 30
		result.blit(txt_im[0], pos)

		boost1 = Menu.FONT.render(self.boost1_text, WHITE)
		w = boost1[0].get_width()
		pos = Menu.SHOP_WIDTH / 2 - w / 2, y + 80
		result.blit(boost1[0], pos)

		boost2 = Menu.FONT.render(self.boost2_text, WHITE)
		w = boost2[0].get_width()
		pos = Menu.SHOP_WIDTH / 2 - w / 2, y + 80 + 120
		result.blit(boost2[0], pos)

		self.boost = result.convert_alpha()

		self.boost_pos = (Menu.SHOP_POS[0], Menu.SHOP_POS[1])

	def update_description_boosts(self, screen, cls_im, txt1, txt2):
		if txt1 != self.boost1_text or txt2 != self.boost2_text:
			self.boost1_text = txt1
			self.boost2_text = txt2
			self.setup_description_boosts(cls_im)
		self.update_boost_option(screen)
		screen.blit(self.boost, self.boost_pos)
	
	def setup_boost_option(self):
		boost_options = pygame.Surface((Menu.SHOP_WIDTH - 20, 220), pygame.SRCALPHA)
		pygame.draw.rect(boost_options, (0, 0, 0), (0, 0, Menu.SHOP_WIDTH-20, 100), border_radius=10)
		pygame.draw.rect(boost_options, (15, 21, 27), (1, 1, Menu.SHOP_WIDTH-20-3, 100-3), border_radius=10)

		pygame.draw.rect(boost_options, (0, 0, 0), (0, 120, Menu.SHOP_WIDTH-20, 100), border_radius=10)
		pygame.draw.rect(boost_options, (15, 21, 27), (1, 120+1, Menu.SHOP_WIDTH-20-3, 100-3), border_radius=10)

		self.boost_options = boost_options
	
	def update_boost_option(self, screen):
		screen.blit(self.boost_options, Menu.BOOST_POS)
	
	def setup_upgrade_texts(self, cls_im, description):
		printf("Updated images for tower upgrade")
		x, y = 20, 20 + Menu.SHOP_IMAGE_SIZE[1]
		self.upgrade_desc = description

		self.upgrade_pos = (Menu.SHOP_POS[0], Menu.SHOP_POS[1])
		upgrade_classic = self.right_tab.copy()

		upgrade_classic.blit(cls_im, (Menu.SHOP_WIDTH / 2 - Menu.SHOP_IMAGE_SIZE[0] / 2, 20))
		upgrade_can_afford = upgrade_classic.copy()
		upgrade_cant_afford = upgrade_classic.copy()

		for k in range(len(description)):
			desc = description[k]

			text = Menu.FONT.render(desc.text, WHITE)
			text_width, text_height = text[0].get_size()

			value = Menu.FONT.render(desc.value, (200, 0, 200) if desc.is_boosted else WHITE)
			value_width, value_height = value[0].get_size()

			pos = (x, y + 30 * (k + 1) + 50)
			upgrade_classic.blit(text[0], pos)
			upgrade_can_afford.blit(text[0], pos)
			upgrade_cant_afford.blit(text[0], pos)

			pos = (x + text_width, y + 30 * (k + 1) + 50 + (text_height - value_height) / 2)
			upgrade_classic.blit(value[0], pos)
			upgrade_can_afford.blit(value[0], pos)
			upgrade_cant_afford.blit(value[0], pos)

			if desc.new_value:
				color = (50, 255, 50)
				new_value = Menu.FONT.render(desc.new_value, color)
				pos = (x + text_width + value_width, y + 30 * (k + 1) + 50 + (text_height - new_value[0].get_height()) / 2)
				upgrade_can_afford.blit(new_value[0], pos)

				color = (255, 40, 80)
				new_value = Menu.FONT.render(desc.new_value, color)
				pos = (x + text_width + value_width, y + 30 * (k + 1) + 50 + (text_height - new_value[0].get_height()) / 2)
				upgrade_cant_afford.blit(new_value[0], pos)
		
		self.upgrade_classic = upgrade_classic.convert_alpha()
		self.upgrade_can_afford = upgrade_can_afford.convert_alpha()
		self.upgrade_cant_afford = upgrade_cant_afford.convert_alpha()

		text = "+ BOOST Spécial"
		default = Menu.FONT.render(text, (255, 180, 0))
		rect = (Menu.SHOP_POS[0] + x, Menu.SHOP_POS[1] + y + 30 * (k + 2) + 50)

		self.upgrade_preview = (default[0], rect)

	def update_upgrade_texts(self, screen, cls_im, description, can_afford, is_boost_preview):
		if not InstanceDescription.are_identical(description, self.upgrade_desc):
			self.setup_upgrade_texts(cls_im, description)
		
		if can_afford:
			screen.blit(self.upgrade_can_afford, self.upgrade_pos)
		else:
			screen.blit(self.upgrade_cant_afford, self.upgrade_pos)
		
		if is_boost_preview:
			screen.blit(*self.upgrade_preview)

	#endregion