from random import randint as rdi
import pygame
import os
import numpy as np
from datetime import datetime

from towers import Tower
from enemies import Enemy
from setup_game_tools import generate, findpath
from chunks import Chunk
from waves import Wave
from logs import Logs
from levels import Level

today = datetime.now()

def printf(args):
	Logs.print('game_data', args)

"""path = os.getenv("appdata")

PACKAGE_NAME = "TowerDefenseV2"
PACKAGE_PATH = path + '/' + PACKAGE_NAME

directories = os.listdir(path)
if not PACKAGE_NAME in directories:
	os.mkdir(path + '/' + PACKAGE_NAME)"""

def get_image(size, place):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey((255, 255, 255))
	return tmp

colors = {'background': (10, 14, 18),
		  'settings': (100, 100, 100),
		  'life_ok': (30, 150, 40),
		  'life_dead': (60, 0, 10),
		  'xp_ok': (114, 22, 224),
		  'xp_dead': (55, 30, 100),
		  'critic': (255, 40, 80),
		  'game': [{'center': (18, 22, 27),
					'border': (42, 47, 51),
					'Ocenter': (14, 18, 23),
					'Oborder': (21, 24, 26),
					'path': (10, 20, 50),
					'start': (0, 38, 125),
					'end': (125, 10, 20),
					'Pcenter': (73, 102, 123),
					'Pborder': (50, 70, 80)},
				   {'center': (18, 22, 27),
					'border': (42, 47, 51),
					'Ocenter': (14, 18, 23),
					'Oborder': (21, 24, 26),
					'path': (40, 0, 10),
					'start': (100, 70, 0),
					'end': (20, 20, 60),
					'Pcenter': (106, 152, 163),
					'Pborder': (100, 70, 80)}]}

class Game:
	DEFAULT_COST_NEW_TILE = 100
	TILE_PRICE_INCREASE = 50
	COST_TREE_REMOVAL = 100

	LIFEMAX = 20

	tiles_im = {}
	trees_im = []

	delete_im = None
	new_tile_im = None

	menu = None
	
	def __init__(self, size, start_count=0, minimum=0.55, empty_forest=False):
		if start_count == 0 :
			start_count = rdi(1, 3)
		array, paths, starts, end, trees = generate(*size, start_count, minimum, empty_forest)
		
		self.array = array
		self.paths = paths
		self.starts = starts
		self.end = end
		self.trees = trees

		self.new_tile_cost = Game.DEFAULT_COST_NEW_TILE
		
		self.size = size
		self.n, self.m = size
		
		self.lengths = [len(path) for path in paths]

		self.lvl = Level()
		
		self.coins = 0
		self.wave_count = 0

		self.selected_tiles = []
		self.selection_type = None
		self.potential_path = None
		self.tile_size = None

		self.need_tile_update = True		

		self.set_life(Game.LIFEMAX)
		self.set_coin(500)
		self.set_level()
		Wave.currentLevel = 0
		self.new_wave()
		
		Chunk.setup_array(*size)
		
		self._xoffset, self._yoffset = None, None
		
		"""self.save_path = PACKAGE_PATH + '/' + datetime.now().strftime("%H-%M-%S-%d-%m-%y") + '/'
		try:
			os.mkdir(self.save_path)
		except:
			pass"""
	
	@property
	def xp_ratio(self):
		return self.lvl.xp / self.lvl.needed_xp()

	def update_level(self):
		result = self.lvl.try_leveling_up()
		if result:
			self.menu.update_val_level(self.lvl.level)
	
	def gain_xp(self, amount):
		self.lvl.xp += amount
		self.menu.update_val_xp_ratio(self.xp_ratio)
	
	def add_coins(self, amount):
		self.coins += amount
		self.menu.update_val_coin(self.coins)
	
	def set_level(self):
		self.menu.update_val_level(self.lvl.level)

	def set_coin(self, value):
		self.coins += value
		self.menu.update_val_coin(self.coins)
	
	def set_life(self, value):
		self.life = value
		self.menu.update_val_life(self.life)

	def new_wave(self):
		self.wave_count += 1
		self.wave = Wave()
		self.menu.update_val_wave(self.wave_count)
	
	def set_speed(self, value):
		self.speed = value
		self.menu.update_val_speed(self.speed)
		Tower.speed = value
		Enemy.change_speed(value)
	
	def get_damage(self, value):
		self.life = max(0, self.life-value)
		self.menu.update_val_life(self.life)
	
	#region PATH LOGIC
	def set_tile(self, val, xc, yc, width=1, height=None):
		"""
		change paths to match with new game array
		"""
		n, m = self.size
		if height == None:
			height = width
		g = self.array.copy()
		for i in range(n):
			for j in range(m):
				if self.array[i, j] == 2:
					g[i, j] = 1
		try:
			for i in range(width):
				for j in range(height):
					if self.trees[xc+i, yc+j] == 0 or self.array[xc+i, yc+j] == val:
						g[xc+i, yc+j] = val
					else:
						raise KeyError
			p = findpath(g, self.size, self.starts, self.end)
		except KeyError:
			printf('Refused to place tower : no usable path after placement')
			return False
		else:
			self.array = g
			self.paths = p
			self.lengths = [len(p) for p in self.paths]
			Enemy.change_path(self.wave, self.paths, self.lengths)
		return True
	
	def still_completable_path(self, val, xc, yc, width, height=0):
		"""
		change paths to match with new game array
		"""
		n, m = self.size
		gcopy = self.array.copy()
		if height == 0:
			height = width
		for i in range(n):
			for j in range(m):
				if self.array[i, j] == 2:
					gcopy[i, j] = 1
		for i in range(width):
			for j in range(height):
				gcopy[xc+i, yc+j] = val
		try:
			p = findpath(gcopy, self.size, self.starts, self.end)
		except KeyError:
			printf('Failed to perform this action !')
			return None
		return p

	def is_placement_valid(self, cls, xc, yc):
		n, m = self.size
		zone = self.array[xc:xc+cls.SIZE, yc:yc+cls.SIZE]
		for i in [0, 3, 4, 5]:
			if i in zone:
				return None
		tree_zone = self.trees[xc:xc+cls.SIZE, yc:yc+cls.SIZE]

		if np.sum(tree_zone) != 0:
			return None

		if xc + cls.SIZE <= n and yc + cls.SIZE <= m and xc >= 0 and yc >= 0:
			return self.still_completable_path(5, xc, yc, width=cls.SIZE)
		return None

	def try_place(self, cls, xc, yc):
		n, m = self.size
		tower_size = cls.SIZE
		tree_zone = self.trees[xc:xc+cls.SIZE, yc:yc+cls.SIZE]
		for i in [0, 3, 4, 5]:
			if i in self.array[xc:xc+tower_size, yc:yc+tower_size]:
				return False
		if xc + tower_size <= n and yc + tower_size <= m and xc >= 0 and yc >= 0 :
			if self.set_tile(5, xc, yc, width=tower_size):
				if np.sum(tree_zone) == 0:
					printf(f"Placing {cls.__name__}")
					cls(xc, yc)
					return True
		printf('Unable to place tower : unavailable place')
		return False
	#endregion

	#region SAVE AND LOAD
	def save(self):
		"""np.savetxt(self.save_path + 'game_array.alf', self.array.transpose(), fmt="%d")
		Tower.save(self.save_path + 'towers/')"""
		
	def load(path):
		pass
	#endregion
	
	#region IMAGES SETUP
	def setup_tree_images(self):
		MONTH = datetime.now().month
		tile_size = self.tile_size
		tree_images = [None]
		if MONTH in [3, 4, 5, 6, 7, 8]:
			printf("Setting up assets for spring / summer")
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_pine.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_fir.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_bonsai.png'))
		elif MONTH in [9, 10, 11]:
			printf("Setting up assets for autumn")
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_autumn.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_pine_autumn.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_fir_autumn.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_bonsai_autumn.png'))
		else:
			printf("Setting up assets for winter")
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_snowy.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_pine_snowy.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_fir_snowy.png'))
			tree_images.append(get_image((tile_size-2, tile_size-2), 'images/trees/tree_bonsai_snowy.png'))
		self.trees_im = tree_images
	
	def set_game_images(self):
		Tower.setup_tower_game_images(self.tile_size)
		Enemy.setup_enemy_images(self.tile_size)
	#endregion

	def has_neighbor_tile(self, i, j):
		n, m = self.size
		if i+1 < n and self.array[i+1][j] != 0:
			return True
		elif i-1 >= 0 and self.array[i-1][j] != 0:
			return True
		elif j+1 < m and self.array[i][j+1] != 0:
			return True
		elif j-1 >= 0 and self.array[i][j-1] != 0:
			return True
		return False
	
	def add_tile(self, xc, yc):
		self.set_tile(1, xc, yc)
		self.new_tile_cost += Game.TILE_PRICE_INCREASE
	
	def add_selected_tiles(self):
		for (xc, yc) in self.selected_tiles:
			self.set_tile(1, xc, yc)
			self.new_tile_cost += Game.TILE_PRICE_INCREASE
	
	def selection_costs(self, tree_count, tile_count):
		tree_cost = Game.COST_TREE_REMOVAL * tree_count
		tile_cost = self.new_tile_cost * tile_count + Game.TILE_PRICE_INCREASE * tile_count * (tile_count - 1)/2
		return int(tree_cost), int(tile_cost)
	
	def selection_tile_cost(self):
		tile_count = len(self.selected_tiles)
		return int(self.new_tile_cost * tile_count + Game.TILE_PRICE_INCREASE * tile_count * (tile_count - 1)/2)
	
	def selection_tree_cost(self):
		return Game.COST_TREE_REMOVAL * len(self.selected_tiles)

	def fill_all(self):
		for i in range(self.n):
			for j in range(self.m):
				if self.array[i, j] in [0, 1, 2]:
					self.array[i, j] = 1
		self.paths = findpath(self.array, self.size, self.starts, self.end)
		self.lengths = [len(p) for p in self.paths]
		Enemy.change_path(self.wave, self.paths, self.lengths)

	def delete_selected_trees(self):
		for (xc, yc) in self.selected_tiles:
			self.trees[xc, yc] = 0
	
	def set_tile_images(self, theme, tile_size):
		self.tile_size = tile_size

		imtile = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(imtile, colors['game'][theme]['border'], (0, 0, tile_size-1, tile_size-1))
		pygame.draw.rect(imtile, colors['game'][theme]['center'], (1, 1, tile_size-2, tile_size-2))
		Game.tiles_im['tile'] = imtile.convert_alpha()

		imout = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(imout, colors['game'][theme]['Oborder'], (0, 0, tile_size-1, tile_size-1))
		pygame.draw.rect(imout, colors['game'][theme]['Ocenter'], (1, 1, tile_size, tile_size))
		Game.tiles_im['out'] = imout.convert_alpha()

		impath = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(impath, colors['game'][theme]['path'], (0, 0, tile_size, tile_size))
		Game.tiles_im['path'] = impath.convert_alpha()

		imstart = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(imstart, colors['game'][theme]['path'], (0, 0, tile_size, tile_size))
		pygame.draw.circle(imstart, colors['game'][theme]['start'], (tile_size/2, tile_size/2), tile_size/2 - 1)
		Game.tiles_im['start'] = imstart.convert_alpha()

		imend = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(imend, colors['game'][theme]['path'], (0, 0, tile_size, tile_size))
		pygame.draw.circle(imend, colors['game'][theme]['end'], (tile_size/2, tile_size/2), tile_size/2 - 1)
		Game.tiles_im['end'] = imend.convert_alpha()

		impotential = pygame.Surface((tile_size, tile_size))
		pygame.draw.rect(impotential, colors['game'][theme]['Pborder'], (0, 0, tile_size, tile_size))
		pygame.draw.rect(impotential, colors['game'][theme]['Pcenter'], (1, 1, tile_size-2, tile_size-2))
		Game.tiles_im['pot_path'] = impotential.convert_alpha()

		Game.new_tile_im = get_image((tile_size, tile_size), 'images/others/new_tile.png')
		Game.delete_im = get_image((tile_size, tile_size), 'images/others/delete.png')

		self.setup_tree_images()
		self.set_game_images()

		Enemy.tile_size = tile_size
		Tower.tile_size = tile_size
	
	def display_tiles(self, surface):
		xoffset, yoffset = self._xoffset, self._yoffset
		tile_size = self.tile_size
		surface.fill((10, 14, 18))

		it = np.nditer(self.array, flags=['multi_index'])
		for x in it:
			i, j = it.multi_index
			if x == 1 or x == 5:
				surface.blit(Game.tiles_im['tile'], (xoffset + i*tile_size, yoffset + j*tile_size))
			elif x == 2:
				surface.blit(Game.tiles_im['path'], (xoffset + i*tile_size, yoffset + j*tile_size))
			elif x == 3:
				surface.blit(Game.tiles_im['start'], (xoffset + i*tile_size, yoffset + j*tile_size))
			elif x == 4:
				surface.blit(Game.tiles_im['end'], (xoffset + i*tile_size, yoffset + j*tile_size))
			elif x == 0 and self.has_neighbor_tile(i, j):
				surface.blit(Game.tiles_im['out'], (xoffset + i*tile_size, yoffset + j*tile_size))
		if self.potential_path:
			for (i, j) in self.potential_path:
				if self.array[i, j] == 1:
					surface.blit(Game.tiles_im['pot_path'], (xoffset + i*tile_size, yoffset + j*tile_size))

		it = np.nditer(self.trees, flags=['multi_index'])
		for x in it:
			i, j = it.multi_index
			image = self.trees_im[int(x)]
			if image:
				surface.blit(image, (xoffset + i*tile_size+1, yoffset + j*tile_size+1))
		
		image = Game.new_tile_im
		if self.selection_type == 'tree':
			image = Game.delete_im
		for (xc, yc) in self.selected_tiles:
			surface.blit(image, (xoffset + xc*tile_size, yoffset + yc*tile_size))

	def update_screen(self, screen, surface, pos, show_range, selected):
		if self.need_tile_update:
			self.display_tiles(surface)
		else:
			screen.blit(surface, (0, 0))
		Tower.update(screen, surface, *pos, show_range, selected, self.need_tile_update)
		self.need_tile_update = False
	
	def update_left(self):
		self.need_tile_update = True