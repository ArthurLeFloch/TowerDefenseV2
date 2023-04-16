import pygame
import os

from tower_description import InstanceDescription as desc
from tower_description import ShopDescription as shop_desc
from tower_description import TowerDescription
from enemies import Enemy, Knight, Goblin, Dragon, KingOfKnights, Giant, Healer, HealZone
from enemy_effects import EnemyEffect, Fire, Poison, Slowness
from logs import Logs
from timer import Timer
import json

def printf(args):
	Logs.print('towers', args)


def get_image(size, place):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey((255, 255, 255))
	return tmp

def dist2(x1, y1, x2, y2):
	return (x2-x1)**2 + (y2-y1)**2


def getRangeIm(dist, valid = True, boosted = False):
	color = (255,255,255)
	if boosted:
		color = (200, 0, 200)
	if not valid:
		color = (140,10,10)
	range_im = pygame.Surface((2*dist, 2*dist), pygame.SRCALPHA)
	pygame.draw.circle(range_im, (*color, 100),
					   (dist, dist), radius=dist, width=5)
	pygame.draw.circle(range_im, (*color, 70),
					   (dist, dist), radius=dist-5, width=7)
	pygame.draw.circle(range_im, (*color, 40),
					   (dist, dist), radius=dist-12, width=10)
	return range_im


def getSimpleRangeIm(dist, valid = True, boosted = False):
	color = (255,255,255)
	if boosted:
		color = (200, 0, 200)
	if not valid:
		color = (140,10,10)
	range_im = pygame.Surface((2*dist, 2*dist), pygame.SRCALPHA)
	pygame.draw.circle(range_im, (*color, 100),
					   (dist, dist), radius=dist, width=5)
	return range_im

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

def black_and_white(img):
	new = img.copy()
	n, m = img.get_size()
	for i in range(n):
		for j in range(m):
			r, g, b, a = img.get_at((i, j))
			if (r, g, b) != (255, 255, 255):
				grey = 0.30 * r + 0.40 * g + 0.30 * b
				color = (grey, grey, grey, a)
				new.set_at((i, j), color)
	new.set_colorkey((255, 255, 255))
	return new.convert_alpha()

def rect_gradient(width, height, valid = True, rotation = 0, boosted = False):
	color = (255, 255, 255)
	if boosted:
		color = (200, 0, 200)
	if not valid:
		color = (140, 10, 10)
	surface = pygame.Surface((width, height), pygame.SRCALPHA)
	for k in range(height):
		new_alpha = int(200 * (1. - k*1./height))
		pygame.draw.line(surface, (*color,new_alpha), (0, k), (width, k))
	
	pygame.transform.rotate(surface, rotation).convert_alpha()
	return surface

class Tower:
	amount = 0

	speed = 1

	subclasses = []
	boosters = []
	dict = {}

	tile_size = None
	xoffset = 0
	yoffset = 0

	new_rects = []
	last_rects = []

	COST_TEXT = None

	LEVEL_TEXT = None
	
	FONT = None
	PRICE_FONT = None
	
	_LVL_PROPORTION = 1/2.

	SHOP_ELEMENT_MIN_HEIGHT = 95
	
	lvl_colors = [
		(28, 29, 30),
		(55, 57, 59),
		(129, 129, 129),
		(200, 200, 200),
		(230, 229, 166),
		(223, 222, 100),
		(201, 169, 53),
		(186, 125, 43),
		(162, 78, 34),
		(145, 42, 21),
		(92, 8, 8)
	]
	lvl_indicators = []
	lvl_indicator_size = 0
	
	looked = None
	
	def __init__(self, pos, lvl):
		cls = self.__class__
		tile_size = Tower.tile_size

		# * Grid relative
		a, b = pos
		xtmp = [a+k for k in range(cls.SIZE)]
		ytmp = [b+k for k in range(cls.SIZE)]
		self.pos = []
		for x in xtmp:
			for y in ytmp:
				self.pos.append((x, y))

		# * Window relative
		self.rect = [a*tile_size + Tower.xoffset, b*tile_size + Tower.yoffset, cls.SIZE*tile_size, cls.SIZE*tile_size]
		self.center = (a+cls.SIZE/2)*tile_size + \
			Tower.xoffset, (b+cls.SIZE/2)*tile_size + Tower.yoffset

		self.damage_multiplier = 1
		self.range_multiplier = 1
		self.speed_multiplier = 1
		
		self.lvl = lvl

		self.chosen_boost = 0
		self.shot = 0
		Tower.amount += 1

		cls.amount += 1
		Tower.dict[cls.__name__].append(self)

		Tower.update_boosters()
		
		if hasattr(cls, "CLASSIC_RELOAD_SPEED"):
			self.is_loaded = Timer(cls.CLASSIC_RELOAD_SPEED[lvl] / self.speed_multiplier)

	def __repr__(self):
		return f'Tower located at x = {self.x}, y = {self.y}\n{self.pos}'
	
	#region SETUP
	def setup_config():
		with open('config/towers.json', 'r') as cfg:
			data = json.load(cfg)
			for cls in Tower.subclasses:
				cls.load_config(data[cls.__name__])
	
	@classmethod
	def load_config(cls, data):
		printf(f"Loading {cls.__name__}")
		cls.SIZE = data['size']
		cls.ALLOWED_LEVEL = data['allowed_level']
		cls.COST = data['cost']
		if 'range' in data:
			cls.CLASSIC_RANGE = data['range']
		if 'reload_speed' in data:
			cls.CLASSIC_RELOAD_SPEED = data['reload_speed']
		if 'damage' in data:
			cls.CLASSIC_DAMAGE = data['damage']
		if 'can_attack' in data:
			cls.CAN_ATTACK = Tower.classes_from_name_list(data['can_attack'])
		if 'explosion_radius' in data:
			cls.CLASSIC_EXPLOSION_RADIUS = data['explosion_radius']
		if 'effect_level' in data:
			cls.EFFECT_LEVEL = data['effect_level']
		if 'effect_duration' in data:
			cls.CLASSIC_DURATION = data['effect_duration']
		if 'earns' in data:
			cls.EARNS = data['earns']
		if 'can_effect' in data:
			cls.CAN_EFFECT = Tower.tower_classes_from_name_list(data['can_effect'])
		if 'damage_multiplier' in data:
			cls.DAMAGE_MULTIPLIER = data['damage_multiplier']
		if 'range_multiplier' in data:
			cls.RANGE_MULTIPLIER = data['range_multiplier']
		if 'speed_multiplier' in data:
			cls.SPEED_MULTIPLIER = data['speed_multiplier']

		if hasattr(cls, 'load_custom_config'):
			cls.load_custom_config(data)

	def classes_from_name_list(names):
		result = []
		for cls in Enemy.subclasses:
			if cls.__name__ in names:
				result.append(cls)
		return result
	
	def tower_classes_from_name_list(names):
		result = []
		for cls in Tower.subclasses:
			if cls.__name__ in names:
				result.append(cls)
		return result
	
	def setup_subclasses():
		Tower.subclasses = Classic.__subclasses__() + Booster.__subclasses__()
	
	def setup_boosters(*args):
		Tower.boosters = Booster.__subclasses__()
	
	def setup_language(tr):
		Tower.COST_TEXT = tr.money_format
		Tower.LEVEL_TEXT = tr.shop_required_level

		Hut.name = tr.tower_hut
		Hut.desc_boost1 = tr.tower_hut_boost1
		Hut.desc_boost2 = tr.tower_hut_boost2

		Mortar.name = tr.tower_mortar
		Wizard.name = tr.tower_wizard
		FlameThrower.name = tr.tower_flame_thrower
		PoisonDiffuser.name = tr.tower_poison_diffuser
		Freezer.name = tr.tower_freezer
		Bank.name = tr.tower_bank
		DamageBooster.name = tr.tower_damage_booster
		RangeBooster.name = tr.tower_range_booster
		SpeedBooster.name = tr.tower_speed_booster

		TowerDescription.setup_language(tr)
	
	def setup(game):
		tile_size = game.tile_size
		Tower.clear()
		Tower.tile_size = tile_size
		Tower.xoffset = game._xoffset
		Tower.yoffset = game._yoffset
		Tower.setup_lvl_indicators()
		Tower.setup_place_indicator()
	#endregion

	#region IMAGES SETUP
	def setup_tower_shop_images(size):
		Hut.shop_image = get_image(size, 'images/towers/hut.png')
		Mortar.shop_image = get_image(size, 'images/towers/mortar.png')
		Wizard.shop_image = get_image(size, 'images/towers/wizard.png')
		FlameThrower.shop_image = get_image(size, 'images/towers/flame_thrower.png')
		PoisonDiffuser.shop_image = get_image(size, 'images/towers/poison_diffuser.png')
		Freezer.shop_image = get_image(size, 'images/towers/freezer.png')
		Bank.shop_image = get_image(size, 'images/towers/bank.png')
		DamageBooster.shop_image = get_image(size, 'images/towers/damage_booster.png')
		RangeBooster.shop_image = get_image(size, 'images/towers/range_booster.png')
		SpeedBooster.shop_image = get_image(size, 'images/towers/speed_booster.png')
	
	def setup_tower_game_images(tile_size):
		Hut.image = get_image((tile_size*Hut.SIZE, tile_size*Hut.SIZE), 'images/towers/hut.png')
		Mortar.image = get_image((tile_size*Mortar.SIZE, tile_size*Mortar.SIZE), 'images/towers/mortar.png')
		Wizard.image = get_image((tile_size*Wizard.SIZE, tile_size*Wizard.SIZE), 'images/towers/wizard.png')
		FlameThrower.image = get_image((tile_size*FlameThrower.SIZE, tile_size*FlameThrower.SIZE), 'images/towers/flame_thrower.png')
		PoisonDiffuser.image = get_image((tile_size*PoisonDiffuser.SIZE, tile_size*PoisonDiffuser.SIZE), 'images/towers/poison_diffuser.png')
		Freezer.image = get_image((tile_size*Freezer.SIZE, tile_size*Freezer.SIZE), 'images/towers/freezer.png')
		Bank.image = get_image((tile_size*Bank.SIZE, tile_size*Bank.SIZE), 'images/towers/bank.png')
		DamageBooster.image = get_image((tile_size*DamageBooster.SIZE, tile_size*DamageBooster.SIZE), 'images/towers/damage_booster.png')
		RangeBooster.image = get_image((tile_size*RangeBooster.SIZE, tile_size*RangeBooster.SIZE), 'images/towers/range_booster.png')
		SpeedBooster.image = get_image((tile_size*SpeedBooster.SIZE, tile_size*SpeedBooster.SIZE), 'images/towers/speed_booster.png')

	def setup_place_indicator():
		tile_size = Tower.tile_size
		border_size = int(.5 * tile_size)
		
		for cls in Tower.subclasses:
			for valid in [0, 1, 2]:
				highlight_size = cls.SIZE * tile_size + 2*int(.5*cls.SIZE * tile_size)
				saved_gradient = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
				
				gradient_bottom = rect_gradient(cls.SIZE * tile_size, border_size, valid=(valid > 0), boosted=(valid == 2))
				saved_gradient.blit(gradient_bottom, (border_size, cls.SIZE*tile_size + border_size))
				gradient_left = pygame.transform.rotate(gradient_bottom, -90).convert_alpha()
				saved_gradient.blit(gradient_left, (0, border_size))
				gradient_top = pygame.transform.rotate(gradient_left, -90).convert_alpha()
				saved_gradient.blit(gradient_top, (border_size, 0))
				gradient_right = pygame.transform.rotate(gradient_top, -90).convert_alpha()
				saved_gradient.blit(gradient_right, (cls.SIZE*tile_size + border_size, border_size))
				
				cls.gradient_rect[valid] = saved_gradient

	def setup_lvl_indicators():
		Tower.lvl_indicators = []
		
		def lower_brightness(color, factor=1):
			r, g, b = color
			r = int(factor*r)
			b = int(factor*b)
			g = int(factor*g)
			return (r,g,b)
		
		display_size = 4*int(Tower.tile_size * Tower._LVL_PROPORTION / 4)
		Tower.lvl_indicator_size = display_size+2
		
		for k in range(len(Tower.lvl_colors)):
			color = Tower.lvl_colors[k]
			surf = pygame.Surface((4,4), pygame.SRCALPHA)
			surf.set_at((1,0), lower_brightness(color))
			surf.set_at((2,0), lower_brightness(color, 0.8))
			surf.set_at((0,1), lower_brightness(color))
			surf.set_at((0,2), lower_brightness(color, 0.8))
			surf.set_at((3,1), lower_brightness(color, 0.6))
			surf.set_at((3,2), lower_brightness(color, 0.4))
			surf.set_at((1,3), lower_brightness(color, 0.6))
			surf.set_at((2,3), lower_brightness(color, 0.4))
			
			surf.set_at((1,1), lower_brightness(color))
			surf.set_at((2,1), lower_brightness(color, 0.8))
			surf.set_at((1,2), lower_brightness(color, 0.8))
			surf.set_at((2,2), lower_brightness(color, 0.7))
			
			surf = pygame.transform.scale(surf, (display_size, display_size)).convert_alpha()
			Tower.lvl_indicators.append(glow(surf))

	def setup_shop_item(cls, shop_width, item_height, description):
		item = pygame.Surface((shop_width, item_height), pygame.SRCALPHA)
		width = cls.shop_image.get_width()
		texts = [cls.name, f"{cls.SIZE} x {cls.SIZE}"]
		for desc in description:
			texts.append(f"{desc.text}{desc.value}")
		
		for k in range(len(texts)):
			text = texts[k]
			shown_text = Tower.FONT.render(text, (255, 255, 255) if k == 0 else (150, 150, 150))
			item.blit(shown_text[0], (40 + width + (shop_width-40-width) / 2 - shown_text[0].get_width()/2, 10 + 22*k - 3))
		
		item.convert_alpha()

		# CAN BUY
		item1 = item.copy()
		tmptext = Tower.PRICE_FONT.render(Tower.COST_TEXT.format(money=cls.COST[0]), (90, 255, 90))

		text_pos = (48 - tmptext[0].get_width()/2, item_height-24)
		image_pos = (text_pos[0] + tmptext[0].get_width() / 2 - cls.shop_image.get_width() / 2, text_pos[1] / 2 - cls.shop_image.get_height()/2)

		item1.blit(tmptext[0], text_pos)
		item1.blit(cls.shop_image, image_pos)

		# CANNOT BUY
		item2 = item.copy()
		tmptext = Tower.PRICE_FONT.render(Tower.COST_TEXT.format(money=cls.COST[0]), (240, 20, 20))
		item2.blit(tmptext[0], text_pos)
		item2.blit(black_and_white(cls.shop_image), image_pos)

		# LOW LEVEL
		item3 = item.copy()
		tmptext = Tower.PRICE_FONT.render(Tower.LEVEL_TEXT.format(level=cls.ALLOWED_LEVEL[0]), (114, 22, 224))

		text_pos = (48 - tmptext[0].get_width()/2, item_height-24)

		item3.blit(tmptext[0], text_pos)
		item3.blit(black_and_white(cls.shop_image), image_pos)

		return [cls, [item1, item2, item3]]
	#endregion

	#region SCREEN RELATIVE FUNCTIONS
	def update(SCREEN, GAME_SCREEN, xc, yc, show_range = True, selected = None, update_game_screen = True, logic_update = True):
		Tower.last_rects = Tower.new_rects.copy()
		Tower.new_rects = []

		EnemyEffect.update(logic_update)
		Tower.looked = None
		
		for cls in Tower.subclasses:
			for tower in Tower.dict[cls.__name__]:
				if selected and selected[0].pos[0] in tower.pos:
					Tower.looked = tower, cls
				elif (xc, yc) in tower.pos:
					Tower.looked = tower, cls
				
				if logic_update:
					tower.on_update()
				
				if update_game_screen:
					tower.display(GAME_SCREEN)
		
		if update_game_screen:
			Tower.new_rects.append((0, 0, *GAME_SCREEN.get_size()))
			SCREEN.blit(GAME_SCREEN, (0, 0))
		
		if selected:
			tower, cls = selected
			if hasattr(cls, "CLASSIC_RANGE"):
				radius = tower.range
				is_boosted = (tower.range_multiplier != 1)
				range_im = getRangeIm(radius, boosted = is_boosted)
				rect = (tower.center[0]-radius, tower.center[1]-radius, *range_im.get_size())
				Tower.new_rects.append(rect)
				SCREEN.blit(range_im, (rect[0], rect[1]))
		elif Tower.looked and show_range:
			tower,cls = Tower.looked
			if hasattr(cls, "CLASSIC_RANGE"):
				radius = tower.range
				is_boosted = (tower.range_multiplier != 1)
				range_im = getSimpleRangeIm(radius, boosted = is_boosted)
				rect = (tower.center[0]-radius, tower.center[1]-radius, *range_im.get_size())
				Tower.new_rects.append(rect)
				SCREEN.blit(range_im, (rect[0], rect[1]))

	def display_possible_place(SCREEN, xc, yc, cls, is_valid):
		tile_size = Tower.tile_size
		border_size = int(.5 * tile_size)
		center = Tower.xoffset + tile_size * (xc + cls.SIZE/2), Tower.yoffset + tile_size * (yc + cls.SIZE/2)
		if Tower.is_place_boosted(cls, *center) and is_valid == 1:
			is_valid += 1
		rect = (xc * tile_size + Tower.xoffset - border_size, yc*tile_size + Tower.yoffset - border_size, *cls.gradient_rect[is_valid].get_size())
		Tower.new_rects.append(rect)
		SCREEN.blit(cls.gradient_rect[is_valid], (rect[0], rect[1]))
		if hasattr(cls, "CLASSIC_RANGE"):
			boost = Tower.get_range_boost(cls, *center)
			range = (cls.CLASSIC_RANGE[0]*boost + cls.SIZE/2) * Tower.tile_size
			range_im = getSimpleRangeIm(range, is_valid, (boost != 1))
			rect = (center[0] - range, center[1] - range, *range_im.get_size())
			Tower.new_rects.append(rect)
			SCREEN.blit(range_im, (rect[0], rect[1]))
	
	def display(self, GAME_SCREEN):
		cls = self.__class__
		Tower.new_rects.append(self.rect)
		GAME_SCREEN.blit(cls.image, (self.rect[0], self.rect[1]))
		rect = (self.rect[0] + self.rect[2]-Tower.lvl_indicator_size, self.rect[1] + self.rect[3]-Tower.lvl_indicator_size, *Tower.lvl_indicators[self.lvl].get_size())
		Tower.new_rects.append(rect)
		GAME_SCREEN.blit(Tower.lvl_indicators[self.lvl], (rect[0], rect[1]))
	#endregion

	#region TOWER RELATIVE FUNCTION
	@property
	def deletion_refund(self):
		return round(self.__class__.COST[self.lvl] / 5)
	
	def clear():
		for cls in Tower.subclasses:
			Tower.dict[cls.__name__] = []
			cls.amount = 0
		Tower.amount = 0

	def get(xc, yc):
		for cls in Tower.subclasses:
			for tower in Tower.dict[cls.__name__]:
				if (xc, yc) in tower.pos:
					return tower,cls
		return None

	def remove(xc, yc):
		found = False
		for cls in Tower.subclasses:
			if not found:
				for tower in Tower.dict[cls.__name__]:
					if (xc, yc) in tower.pos:
						found = True
						tower.delete()
						break
	
	def delete(self):
		self.__class__.amount -= 1
		Tower.dict[self.__class__.__name__].remove(self)
		if hasattr(self, "on_delete"):
			self.on_delete()
		Tower.amount -= 1
	
	def level_up(self):
		self.lvl += 1
		if hasattr(self, "on_level_up"):
			self.on_level_up()

	@property
	def range(tower):
		cls = tower.__class__
		return (tower.__class__.CLASSIC_RANGE[tower.lvl]*tower.range_multiplier + cls.SIZE/2) * Tower.tile_size
	
	@property
	def explosion_radius(tower):
		return tower.__class__.CLASSIC_EXPLOSION_RADIUS[tower.lvl] * Tower.tile_size
	
	@property
	def damage(tower):
		cls = tower.__class__
		return cls.CLASSIC_DAMAGE[tower.lvl]*tower.damage_multiplier
	
	@property
	def is_choosing_boost(self):
		return self.lvl == self.__class__.SPLIT_LEVEL and self.chosen_boost == 0
	
	def get_range_boost(cls, x, y):
		multiplier = 1
		if cls in RangeBooster.CAN_EFFECT:
			for booster in Tower.dict[RangeBooster.__name__]:
				if dist2(x, y, *booster.center) <= booster.range**2:
					multiplier *= RangeBooster.RANGE_MULTIPLIER[booster.lvl]
		return multiplier
	
	def is_place_boosted(cls, x, y):
		for booster_cls in Tower.boosters:
			if cls in booster_cls.CAN_EFFECT:
				for booster in Tower.dict[booster_cls.__name__]:
					if dist2(x, y, *booster.center) <= booster.range**2:
						return True
		return False
	
	def update_boosters():
		printf("Updating boosters")
		for cls in Tower.subclasses:
			for tower in Tower.dict[cls.__name__]:
				tower.damage_multiplier = 1
				tower.range_multiplier = 1
				tower.speed_multiplier = 1

		for booster in Tower.dict[DamageBooster.__name__]:
			for tower_cls in DamageBooster.CAN_EFFECT:
				for tower in Tower.dict[tower_cls.__name__]:
					if dist2(*booster.center, *tower.center) <= booster.range**2:
						tower.damage_multiplier *= DamageBooster.DAMAGE_MULTIPLIER[booster.lvl]
		for booster in Tower.dict[RangeBooster.__name__]:
			for tower_cls in RangeBooster.CAN_EFFECT:
				for tower in Tower.dict[tower_cls.__name__]:
					if dist2(*booster.center, *tower.center) <= booster.range**2:
						tower.range_multiplier *= RangeBooster.RANGE_MULTIPLIER[booster.lvl]
		for booster in Tower.dict[SpeedBooster.__name__]:
			for tower_cls in SpeedBooster.CAN_EFFECT:
				for tower in Tower.dict[tower_cls.__name__]:
					if dist2(*booster.center, *tower.center) <= booster.range**2:
						tower.speed_multiplier *= SpeedBooster.SPEED_MULTIPLIER[booster.lvl]
	#endregion

	def save(path):
		try:
			os.mkdir(path)
		except:
			pass
		for cls in Tower.subclasses:
			with open(path + cls.__name__ + '.alf', 'w') as file:
				for tower in Tower.dict[cls.__name__]:
					file.write(f"{tower.pos[0][0]},{tower.pos[0][1]},{tower.lvl}\n")
							
class Booster(Tower):
	def on_update(self): #? Doesn't need updates, all happens on construction, destruction, or construction of an other tower.
		pass

	def on_delete(self):
		Tower.update_boosters()

	def on_level_up(self):
		Tower.update_boosters()

class Classic(Tower):
	def on_delete(self):
		self.is_loaded.delete()
	
	def on_level_up(self):
		cls = self.__class__
		self.is_loaded.change_duration(cls.CLASSIC_RELOAD_SPEED[self.lvl] / self.speed_multiplier)

class Hut(Classic):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]

	desc_boost1 = None
	effect = Poison
	EFFECT_LEVEL = [0,0,0,0,0,0,1,2,2,3,4]
	CLASSIC_DURATION = [4000,4000,4000,4000,4000,4000,5000,7000,10000,14000,20000]
	GOLD_TOUCH_AMOUNT = [1,1,1,1,1,1,1,2,4,6,10]
	desc_boost2 = None
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	CLASSIC_DAMAGE = None
	CLASSIC_RANGE = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = 5
	
	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(sniper):
		if sniper.is_loaded:
			closer = Enemy.get_closer(Hut.CAN_ATTACK, sniper.center, sniper.range)
			if closer != None:
				closer.get_damage(sniper.damage)
				if sniper.chosen_boost == 1:
					effect = Poison(closer, Hut.EFFECT_LEVEL[sniper.lvl], Hut.CLASSIC_DURATION[sniper.lvl])
					closer.apply_effect(Poison, effect)
				elif sniper.chosen_boost == 2:
					Enemy.last_earned += Hut.GOLD_TOUCH_AMOUNT[sniper.lvl]
				sniper.is_loaded.reset()
				sniper.shot += 1
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		dpt = shop_desc.damage_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, dpt])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			if self.chosen_boost == 1:
				effect_level = desc.effect_level(self, upgrade)
				duration = desc.effect_duration(self, upgrade)
				dpt = desc.effect_damage_per_sec(self, upgrade)
				return [level, effect_level, duration, dpt]
			elif self.chosen_boost == 2:
				gold_touch = desc.gold_touch(self, upgrade)
				return [level, gold_touch]
		else:
			radius = desc.range(self, upgrade)
			damage = desc.damage(self, upgrade)
			damage_per_sec = desc.damage_per_sec(self, upgrade)
			return [level, radius, damage, damage_per_sec]

class Mortar(Classic):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	CLASSIC_DAMAGE = None
	CLASSIC_RANGE = None
	CLASSIC_EXPLOSION_RADIUS = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(mortar):
		if mortar.is_loaded:
			closer = Enemy.get_closer(Mortar.CAN_ATTACK, mortar.center, mortar.range)
			if closer:
				Enemy.zone_damage(Mortar.CAN_ATTACK, (closer.x, closer.y), mortar.explosion_radius, mortar.damage)
				mortar.is_loaded.reset()
				mortar.shot += 1
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		dpt = shop_desc.damage_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, dpt])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			damage = desc.damage(self, upgrade)
			explosion_radius = desc.explosion_radius(self, upgrade)
			damage_per_sec = desc.damage_per_sec(self, upgrade)
			return [level, radius, damage, explosion_radius, damage_per_sec]


class Wizard(Classic):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	CLASSIC_DAMAGE = None
	CLASSIC_RANGE = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(wizard):
		if wizard.is_loaded:
			at_least_one = Enemy.zone_damage(Wizard.CAN_ATTACK, wizard.center, wizard.range, wizard.damage)
			if at_least_one:
				wizard.shot += 1
				wizard.is_loaded.reset()
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		dpt = shop_desc.damage_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, dpt])

	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			damage = desc.damage(self, upgrade)
			damage_per_sec = desc.damage_per_sec(self, upgrade)
			return [level, radius, damage, damage_per_sec]


class FlameThrower(Classic):
	name = None
	effect = Fire
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	EFFECT_LEVEL = None
	CLASSIC_RANGE = None
	CLASSIC_DURATION = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(flame_thrower):
		if flame_thrower.is_loaded:
			damaged = Enemy.get_all(FlameThrower.CAN_ATTACK, flame_thrower.center, flame_thrower.range)
			for enemy in damaged:
				effect = Fire(enemy, FlameThrower.EFFECT_LEVEL[flame_thrower.lvl], FlameThrower.CLASSIC_DURATION[flame_thrower.lvl])
				enemy.apply_effect(Fire, effect)
			if damaged != []:
				flame_thrower.shot += 1
				flame_thrower.is_loaded.reset()
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		duration = shop_desc.effect_duration(cls)
		dpt = shop_desc.effect_damage_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [duration, dpt])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)		
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			effect_level = desc.effect_level(self, upgrade)
			duration = desc.effect_duration(self, upgrade)
			dpt = desc.effect_damage_per_sec(self, upgrade)
			return [level, radius, effect_level, duration, dpt]

class PoisonDiffuser(Classic):
	name = None
	effect = Poison
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	EFFECT_LEVEL = None
	CLASSIC_RANGE = None
	CLASSIC_DURATION = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(poison_diffuser):
		if poison_diffuser.is_loaded:
			damaged = Enemy.get_all(PoisonDiffuser.CAN_ATTACK, poison_diffuser.center, poison_diffuser.range)
			for enemy in damaged:
				effect = Poison(enemy, PoisonDiffuser.EFFECT_LEVEL[poison_diffuser.lvl], PoisonDiffuser.CLASSIC_DURATION[poison_diffuser.lvl])
				enemy.apply_effect(Poison, effect)
			if damaged != []:
				poison_diffuser.shot += 1
				poison_diffuser.is_loaded.reset()
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		duration = shop_desc.effect_duration(cls)
		dpt = shop_desc.effect_damage_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [duration, dpt])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			effect_level = desc.effect_level(self, upgrade)
			duration = desc.effect_duration(self, upgrade)
			dpt = desc.effect_damage_per_sec(self, upgrade)
			return [level, radius, effect_level, duration, dpt]


class Freezer(Classic):
	name = None
	effect = Slowness
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_ATTACK = None
	CLASSIC_RELOAD_SPEED = None
	EFFECT_LEVEL = None
	CLASSIC_RANGE = None
	CLASSIC_DURATION = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(freezer):
		if freezer.is_loaded:
			damaged = Enemy.get_all(Freezer.CAN_ATTACK, freezer.center, freezer.range)
			for enemy in damaged:
				if hasattr(enemy, "v"):
					effect = Slowness(enemy, Freezer.EFFECT_LEVEL[freezer.lvl], Freezer.CLASSIC_DURATION[freezer.lvl])
					enemy.apply_effect(Slowness, effect)
			if damaged != []:
				freezer.shot += 1
				freezer.is_loaded.reset()
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		duration = shop_desc.effect_duration(cls)
		rate = shop_desc.slowness_factor(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [duration, rate])

	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			effect_level = desc.effect_level(self, upgrade)
			duration = desc.effect_duration(self, upgrade)
			rate = desc.slowness_factor(self, upgrade)
			return [level, radius, effect_level, duration, rate]


class Bank(Classic):
	name = None
	amount = 0
	
	image = None
	shop_image = None
	gradient_rect = [None, None, None]

	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CLASSIC_RELOAD_SPEED = None
	EARNS = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1
	
	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)

	def on_update(bank):
		if bank.is_loaded:
			Enemy.last_earned += bank.EARNS[bank.lvl]
			bank.is_loaded.reset()
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		earns = shop_desc.earn_per_action(cls)
		earns_by_sec = shop_desc.earn_per_sec(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [earns, earns_by_sec])

	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			earns = desc.earn_per_action(self, upgrade)
			earns_per_sec = desc.earn_per_sec(self, upgrade)
			duration = desc.reload_speed(self, upgrade)
			return [level, earns, earns_per_sec, duration]

class DamageBooster(Booster):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_EFFECT = None
	DAMAGE_MULTIPLIER = None
	CLASSIC_RANGE = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		multiplier = shop_desc.damage_multiplier(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, multiplier])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			multiplier = desc.damage_multiplier(self, upgrade)
			return [level, radius, multiplier]

class RangeBooster(Booster):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_EFFECT = None
	RANGE_MULTIPLIER = None
	CLASSIC_RANGE = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		multiplier = shop_desc.range_multiplier(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, multiplier])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			multiplier = desc.range_multiplier(self, upgrade)
			return [level, radius, multiplier]

class SpeedBooster(Booster):
	name = None
	amount = 0

	image = None
	shop_image = None
	gradient_rect = [None, None, None]
	
	SIZE = None
	ALLOWED_LEVEL = None
	COST = None
	CAN_EFFECT = None
	SPEED_MULTIPLIER = None
	CLASSIC_RANGE = None

	MAX_LEVEL = 10
	SPLIT_LEVEL = -1

	def __init__(self, x, y, level = 0):
		Tower.__init__(self, (x, y), lvl=level)
	
	@classmethod
	def shop_item(cls, shop_width, item_height):
		range = shop_desc.range(cls)
		multiplier = shop_desc.speed_multiplier(cls)
		return Tower.setup_shop_item(cls, shop_width, item_height, [range, multiplier])
	
	def description_texts(self, upgrade, boost):
		level = desc.level(self, upgrade)
		if boost:
			return [level, desc("TODO", 0)]
		else:
			radius = desc.range(self, upgrade)
			multiplier = desc.speed_multiplier(self, upgrade)
			return [level, radius, multiplier]

