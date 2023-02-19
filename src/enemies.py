from math import sqrt
import time
import pygame
from random import randint as rdi

from enemy_effects import EnemyEffect
from chunks import Chunk
from logs import Logs
from timer import Timer

def printf(args):
	Logs.print('enemies', args)


def get_image(size, place):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey((255, 255, 255))
	return tmp


def _norm(v):
	return sqrt(v[0]**2 + v[1]**2)


def _vect(a, b):
	x, y = b[0]-a[0], b[1]-a[1]
	n = _norm((x, y))
	return x/n, y/n


def _dist_2(x1, y1, x2, y2):
	return (x2-x1)**2 + (y2-y1)**2


def _on_rect(pos, rect):
	# Rect : top left x,y and width, height
	x, y = pos
	b1 = rect[0][0] <= x <= rect[0][0]+rect[1]
	b2 = rect[0][1] <= y <= rect[0][1]+rect[2]
	return b1 and b2

class Enemy:
	amount = 0
	corrupted = 0

	xoffset = 0
	yoffset = 0
	tile_size = None

	time_since_last_update = 0.0
	last_update = 0.0

	last_pause = None

	new_rects = []
	last_rects = []

	lifebar = [None, None]

	starts = None
	end = None
	paths = []
	lengths = []
	speed = 1
	
	last_earned = 0
	last_killed = 0
	last_lost_life = 0
	SHOW_LIFE_TIME = 5
	
	path_followers = []
	others = []
	subclasses = []
	dict = {}

	def __init__(self, pos=None, start = None, current_on_path=None, corrupted=False):
		cls = self.__class__
		if start != None:
			self.start_index = start
		else:
			self.start_index = rdi(0, len(Enemy.starts) - 1)
		
		if pos:
			self.x, self.y = pos
		else:
			self.x, self.y = Enemy.starts[self.start_index]  # Window relative
			self.x += Enemy.xoffset
			self.y += Enemy.yoffset
		
		nx, ny = Chunk.coords_to_chunk(self.x, self.y, Enemy.xoffset, Enemy.yoffset, Enemy.tile_size)
		Chunk.game[nx][ny].content[cls.__name__].append(self)
		
		self.health = cls.MAX_HEALTH[corrupted]
		self.dead = False

		self.health_bar = None
		self.health_bar_size = None

		if cls.follow_path:
			self.vx,self.vy = 0, 0
			xp, yp = 0,0
			if not current_on_path:
				xp, yp = Enemy.paths[self.start_index][1]
				
			else:
				xp, yp = Enemy.paths[self.start_index][current_on_path+1]
			xp = Enemy.xoffset + xp * Enemy.tile_size
			yp = Enemy.yoffset + yp * Enemy.tile_size
			self.vx, self.vy = _vect(Enemy.starts[self.start_index], (xp, yp))
			if current_on_path:
				self.current_on_path = current_on_path
			else:
				self.current_on_path = 0
		
		self.effects = {'Fire':None, 'Poison':None, 'Slowness':None}
		self.last_hit = 10

		Enemy.amount += 1
		cls.amount += 1
		Enemy.dict[cls.__name__].append(self)

		self.corrupted = corrupted
		if corrupted:
			Enemy.corrupted += 1
			cls.corrupted += 1
	
	def setup_subclasses():
		Enemy.subclasses = Enemy.__subclasses__()
		Chunk.setup(Enemy.subclasses)

	def setup(game):
		tile_size = game.tile_size
		xoffset, yoffset = game._xoffset, game._yoffset
		
		Enemy.starts = [(start[0]*tile_size+tile_size/2, start[1]*tile_size+tile_size/2) for start in game.starts]
		Enemy.end = xoffset + game.end[0] * tile_size + tile_size/2, yoffset + game.end[1] * tile_size + tile_size/2

		Enemy.clear()
		EnemyEffect.clear()

		Enemy.paths = game.paths.copy()
		Enemy.lengths = game.lengths.copy()
		Enemy.xoffset = game._xoffset
		Enemy.yoffset = game._yoffset

		Enemy.time_since_last_update = 1
		Enemy.last_update = time.time()
		
		for cls in Enemy.subclasses:
			cls.MAX_HEALTH = cls.DEFAULT_HEALTH.copy()
	
	def setup_enemy_images(tile_size):
		Knight.imrad = tile_size/3
		Goblin.imrad = tile_size/3
		Dragon.imrad = tile_size/3
		KingOfKnights.imrad = tile_size/2
		Healer.imrad = tile_size/3
		HealZone.imrad = tile_size/2
		Giant.imrad = tile_size/2

		Enemy.lifebar[0] = get_image((2*tile_size, 2*tile_size/3), 'images/enemies/lifebar.png')
		Enemy.lifebar[1] = get_image((2*tile_size, 2*tile_size/3), 'images/enemies/lifebar_corrupted.png')

		Knight.image[0] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/knight.png')
		Knight.image[1] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/knight_corrupted.png')

		Goblin.image[0] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/goblin.png')
		Goblin.image[1] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/goblin_corrupted.png')

		Dragon.image[0] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/dragon.png')
		Dragon.image[1] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/dragon_corrupted.png')

		KingOfKnights.image[0] = get_image((tile_size, tile_size), 'images/enemies/king_of_knights.png')
		KingOfKnights.image[1] = get_image((tile_size, tile_size), 'images/enemies/king_of_knights_corrupted.png')

		Healer.image[0] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/healer.png')
		Healer.image[1] = get_image((2*tile_size/3, 2*tile_size/3), 'images/enemies/healer_corrupted.png')

		HealZone.image[0] = get_image((tile_size, tile_size), 'images/enemies/healzone.png')
		HealZone.image[1] = get_image((tile_size, tile_size), 'images/enemies/healzone_corrupted.png')

		Giant.image[0] = get_image((tile_size, tile_size), 'images/enemies/giant.png')
		Giant.image[1] = get_image((tile_size, tile_size), 'images/enemies/giant_corrupted.png')

		tmp = HealZone.DEFAULT_RADIUS[0] * tile_size
		tmp2 = pygame.Surface((tmp*2, tmp*2), pygame.SRCALPHA)
		pygame.draw.circle(tmp2, (255, 100, 150, 15), (tmp, tmp), tmp)
		pygame.draw.circle(tmp2, (200, 50, 100, 50), (tmp, tmp), tmp, width=5)
		HealZone.range_im[0] = tmp2

		tmp = HealZone.DEFAULT_RADIUS[1] * tile_size
		tmp2 = pygame.Surface((tmp*2, tmp*2), pygame.SRCALPHA)
		pygame.draw.circle(tmp2, (255, 100, 150, 15), (tmp, tmp), tmp)
		pygame.draw.circle(tmp2, (150, 0, 50, 50), (tmp, tmp), tmp, width=5)
		HealZone.range_im[1] = tmp2
	
	def update_health(lvl, health_factor):
		for cls in Enemy.subclasses:
			new_health = int(cls.DEFAULT_HEALTH[0] + (lvl - 1) * health_factor * cls.DEFAULT_HEALTH[0])
			cls.MAX_HEALTH = [new_health, 2 * new_health]
	
	def print_health_update():
		printf("Updated enemies stats :")
		for cls in Enemy.subclasses:
			printf(f'{cls.__name__} :\t{cls.MAX_HEALTH}')

	def update(SCREEN, wave, logic_update):
		Enemy.time_since_last_update = time.time() - Enemy.last_update
		Enemy.last_rects = Enemy.new_rects.copy()
		Enemy.new_rects = []
		for cls in Enemy.subclasses:
			for enemy in Enemy.dict[cls.__name__][::-1]:
				enemy.display(SCREEN)
				if enemy.can_show_health:
					enemy.show_health(SCREEN)
				if hasattr(enemy, "on_display"):
					enemy.on_display(SCREEN)
				
				if logic_update:
					if hasattr(enemy, "on_update"):
						enemy.on_update()
					if cls.follow_path:
						Enemy.update_path_follower(SCREEN, enemy, wave)
					else:
						enemy.custom_update()
		Enemy.last_update = time.time()

	def change_path(wave, paths, lengths):
		Enemy.paths = paths.copy()
		Enemy.lengths = lengths.copy()
		for cls in Enemy.subclasses:
			if cls.follow_path:
				for enemy in Enemy.dict[cls.__name__]:
					cls.change_entity_path(enemy, wave)

	def clear():
		Enemy.amount = 0
		for cls in Enemy.subclasses:
			Enemy.dict[cls.__name__] = []
			cls.amount = cls.corrupted = 0

	def get_closer(can_see, pos, radius):
		closer = None
		d = 10000**2
		relevant_chunks = Chunk.get_range_chunk(*pos, radius, Enemy.tile_size)
		
		for cls in can_see:
			for (x_chunk, y_chunk) in relevant_chunks:
				for enemy in Chunk.game[x_chunk][y_chunk].content[cls.__name__]:
					d2 = _dist_2(*pos, enemy.x, enemy.y)
					if d2 < radius**2:
						if d2 < d:
							closer = enemy
							d = d2
		return closer

	def get_tile_position(enemy, i):
		xa, ya = Enemy.paths[enemy.start_index][i]
		xa = xa * Enemy.tile_size + Enemy.xoffset
		ya = ya * Enemy.tile_size + Enemy.yoffset
		return xa, ya

	def change_speed(speed):
		Enemy.speed = speed
		for cls in Enemy.subclasses:
			for enemy in Enemy.dict[cls.__name__]:
				if hasattr(enemy, 'heal_speed'):
					enemy.heal_speed = cls.HEALING_SPEED[enemy.corrupted] / speed
				if hasattr(enemy, 'spawn_speed'):
					enemy.spawn_speed = cls.SPAWNING_SPEED[enemy.corrupted] / speed
		EnemyEffect.change_speed(speed)
	
	def get_all(can_attack, pos, radius):
		result = []
		relevant_chunks = Chunk.get_range_chunk(*pos, radius, Enemy.tile_size)
		
		for cls in can_attack:
			for (x_chunk, y_chunk) in relevant_chunks:
				for enemy in Chunk.game[x_chunk][y_chunk].content[cls.__name__]:
					if _dist_2(*pos, enemy.x, enemy.y) < radius**2:
						result.append(enemy)
		return result

	def zone_damage(can_attack, pos, radius, amount): # Returns True if more than 1 enemy has been hit
		targets = Enemy.get_all(can_attack, pos, radius)
		if len(targets) == 0:
			return False
		for enemy in targets:
			enemy.get_damage(amount)
		return True
	
	@property
	def has_reached_end(self):
		return self.current_on_path >= Enemy.lengths[self.start_index] - 1
	
	@property
	def can_show_health(self):
		return time.time()-self.last_hit < Enemy.SHOW_LIFE_TIME
	
	@property
	def v(self):
		result = self.__class__.DEFAULT_SPEED[self.corrupted] * Enemy.tile_size * Enemy.speed * Enemy.time_since_last_update
		if self.effects['Slowness']:
			result *= self.effects['Slowness'].slowing_rate
		return result
	
	def update_path_follower(SCREEN, self, wave):
		cls = self.__class__
		tile_size = Enemy.tile_size
		if not self.has_reached_end:
			if hasattr(self, "on_update"):
				self.on_update()
			xa, ya = Enemy.get_tile_position(self, self.current_on_path)
			xb, yb = Enemy.get_tile_position(self, self.current_on_path + 1)
			if _on_rect([self.x, self.y], [[xa, ya], tile_size, tile_size]) or _on_rect([self.x, self.y], [[xb, yb], tile_size, tile_size]):
				xb, yb = xb + tile_size/2, yb + tile_size/2
				if abs(xb-self.x) + abs(yb-self.y) > self.v:
					self.vx, self.vy = _vect((self.x, self.y), (xb, yb))
					self.vx *= self.v
					self.vy *= self.v
				else:
					self.current_on_path += 1
				self.move()
			else:  # ? Enemy out of paths
				self.die(earn=False)
				wave.wave.append([cls, 1])
				wave.length += 1
		else:  # ? Enemy has reached the end
			self.die(earn=False)
			Enemy.last_lost_life += 1
	
	def change_entity_path(self, wave):
		cls = self.__class__
		xc, yc = int((self.x-Enemy.xoffset) / Enemy.tile_size), int((self.y-Enemy.yoffset)/Enemy.tile_size)
		try:
			i = Enemy.paths[self.start_index].index((xc, yc))
		except ValueError:
			self.die(earn=False)
			wave.wave.append([cls, 1])
			wave.length += 1
		else:
			self.current_on_path = i
	
	def get_damage(self, amount):
		previous = self.health
		self.health = max(min(self.health-amount,self.__class__.MAX_HEALTH[self.corrupted]), 0)
		if previous != self.health:
			self.need_health_update = True
		if self.health < self.__class__.MAX_HEALTH[self.corrupted]:
			self.last_hit = time.time()
		if self.health <= 0:
			self.die()
	
	def die(self, earn=True):
		cls = self.__class__
		nx, ny = Chunk.coords_to_chunk(self.x, self.y, Enemy.xoffset, Enemy.yoffset, Enemy.tile_size)
		Chunk.game[nx][ny].content[cls.__name__].remove(self)
		
		if earn and hasattr(self, "on_death"):
			self.on_death()
		Enemy.corrupted -= self.corrupted
		cls.corrupted -= self.corrupted
		self.dead = True
		for effect in self.effects.values():
			if effect != None:
				effect.delete()
		if hasattr(self, "is_loaded"):
			self.is_loaded.delete()

		Enemy.dict[cls.__name__].remove(self)
		cls.amount -= 1
		Enemy.amount -= 1
		if earn:
			Enemy.last_earned += cls.COIN_VALUE
			Enemy.last_killed += 1
	
	def apply_effect(self, cls, effect):
		if self.effects[cls.__name__]:
			effect2 = self.effects[cls.__name__]
			if hasattr(effect, "damages"):
				if effect.damages > effect2.damages or ((effect.damages == effect2.damages) and effect.duration > effect2.duration):
					effect2.delete()
					effect.active = True
					self.effects[cls.__name__] = effect
					EnemyEffect.affected[cls.__name__].append(effect)
				else:
					effect.delete()
			elif hasattr(effect, "slowing_rate"):
				if effect.slowing_rate < effect2.slowing_rate or ((effect.slowing_rate == effect2.slowing_rate) and effect.duration > effect2.duration):
					effect2.delete()
					effect.active = True
					self.effects[cls.__name__] = effect
					EnemyEffect.affected[cls.__name__].append(effect)
				else:
					effect.delete()
		else:
			effect.active = True
			self.effects[cls.__name__] = effect
			EnemyEffect.affected[cls.__name__].append(effect)
	
	def move(self):
		previous_chunk_pos = Chunk.coords_to_chunk(self.x, self.y, Enemy.xoffset, Enemy.yoffset, Enemy.tile_size)
		self.x += self.vx
		self.y += self.vy
		chunk_pos = Chunk.coords_to_chunk(self.x, self.y, Enemy.xoffset, Enemy.yoffset, Enemy.tile_size)
		if previous_chunk_pos != chunk_pos:
			px, py = previous_chunk_pos
			nx, ny = chunk_pos
			Chunk.game[px][py].content[self.__class__.__name__].remove(self)
			Chunk.game[nx][ny].content[self.__class__.__name__].append(self)
		
	def setup_health_bar(self):
		tmp = self.health / self.__class__.MAX_HEALTH[self.corrupted]
		width, height = Enemy.lifebar[self.corrupted].get_size()
		health_bar = pygame.Surface((width, height), pygame.SRCALPHA)
		r = int(width / 32)
		pygame.draw.rect(health_bar, (80, 0, 0), (4 * r, 2 * r, width - 8 * r, height - 3 * r))
		pygame.draw.rect(health_bar, (15, 145, 0), (4 * r, 2 * r, (width - 8 * r) * tmp, height - 3 * r))
		health_bar.blit(Enemy.lifebar[self.corrupted], (0, 0))

		self.health_bar = health_bar.convert_alpha()
		self.health_bar_size = (width, height)
	
	def show_health(self, SCREEN):
		if self.need_health_update:
			self.need_health_update = False
			self.setup_health_bar()
		
		width, height = self.health_bar_size
		rect = (self.x - width / 2, self.y - self.__class__.imrad - 10 - height / 2, *self.health_bar_size)
		Enemy.new_rects.append(rect)
		SCREEN.blit(self.health_bar, rect)
	
	def display(self, SCREEN):
		cls = self.__class__
		rect = (self.x - cls.imrad, self.y - cls.imrad, *cls.image[self.corrupted].get_size())
		Enemy.new_rects.append(rect)
		SCREEN.blit(cls.image[self.corrupted], (rect[0], rect[1]))

class Knight(Enemy):
	follow_path = True
	flying = False

	amount = 0
	corrupted = 0
	
	image = [None, None]
	imrad = 0

	COIN_VALUE = 8
	DEFAULT_HEALTH = [200, 400]
	DEFAULT_SPEED = [1.0, 2.0]
	MAX_HEALTH = [200, 400]

	def __init__(self, corrupted=0, pos=None, start=None, current_on_path=None):
		Enemy.__init__(self, pos=pos, start=start, current_on_path=current_on_path, corrupted=corrupted)

class Goblin(Enemy):
	follow_path = True
	flying = False

	amount = 0
	corrupted = 0

	image = [None, None]
	imrad = 0

	COIN_VALUE = 14
	DEFAULT_SPEED = [1.4, 2.8]
	DEFAULT_HEALTH = [100, 200]
	MAX_HEALTH = [100, 200]

	def __init__(self, corrupted=0):
		Enemy.__init__(self, corrupted=corrupted)

class Dragon(Enemy):
	follow_path = False
	flying = True

	amount = 0
	corrupted = 0

	image = [None, None]
	imrad = 0
	
	COIN_VALUE = 40
	DEFAULT_SPEED = [1.2, 2.4]
	DEFAULT_HEALTH = [300, 600]
	MAX_HEALTH = [300, 600]

	def __init__(self, corrupted=0):
		Enemy.__init__(self, corrupted=corrupted)

	def custom_update(self):
		xb, yb = Enemy.end
		if abs(xb-self.x) + abs(yb-self.y) > self.v:
			self.vx, self.vy = _vect((self.x, self.y), Enemy.end)
			self.vx *= self.v
			self.vy *= self.v
			self.move()
		else:  # ? A Dragon has reached the end
			self.die(earn=False)
			Enemy.last_lost_life += 1


class KingOfKnights(Enemy):
	follow_path = True
	flying = False

	amount = 0
	corrupted = 0

	image = [None, None]
	imrad = 0

	COIN_VALUE = 300
	SPAWNING_SPEED = [5, 3.5]
	DEFAULT_SPEED = [0.7, 1.4]
	DEFAULT_HEALTH = [2000, 4000]
	MAX_HEALTH = [2000, 4000]

	def __init__(self, corrupted=0):
		Enemy.__init__(self, corrupted=corrupted)
		self.is_loaded = Timer(KingOfKnights.SPAWNING_SPEED[self.corrupted])
	
	def on_update(self):
		if self.is_loaded:
			Knight(self.corrupted, pos=(self.x, self.y), start=self.start_index, current_on_path=self.current_on_path)
			self.is_loaded.reset()

class Giant(Enemy):
	follow_path = True
	flying = False

	amount = 0
	corrupted = 0

	image = [None, None]
	imrad = 0

	COIN_VALUE = 1000
	DEFAULT_SPEED = [0.5, 1.0]
	DEFAULT_HEALTH = [8000, 16000]
	MAX_HEALTH = [8000, 16000]

	def __init__(self, corrupted=0):
		Enemy.__init__(self, corrupted=corrupted)

class Healer(Enemy):
	follow_path = False
	flying = True

	amount = 0
	corrupted = 0

	image = [None, None]
	imrad = 0

	COIN_VALUE = 100
	CAN_HEAL = [Knight, Goblin, Dragon, KingOfKnights, Giant]
	MAX_RANGE = [7, 10]
	HEALING_SPEED = [0.5, 0.25]
	HEALING_AMOUNT = [120, 200]
	DEFAULT_SPEED = [1.6, 3.2]
	DEFAULT_HEALTH = [2000, 4000]
	MAX_HEALTH = [2000, 4000]

	def __init__(self, corrupted=0):
		Enemy.__init__(self, corrupted=corrupted)
		self.vx, self.vy = _vect((self.x, self.y), Enemy.end)
		self.is_loaded = Timer(Healer.HEALING_SPEED[corrupted])
		self.focus = None

	def custom_update(self):		
		if self.focus:
			if self.focus.dead or _dist_2(self.x,self.y,self.focus.x,self.focus.y) > (Healer.MAX_RANGE[self.corrupted]*Enemy.tile_size)**2:
				self.focus = Enemy.get_closer(self.CAN_HEAL,(self.x,self.y),Healer.MAX_RANGE[self.corrupted]*Enemy.tile_size)
			if self.focus and _dist_2(self.x,self.y,self.focus.x,self.focus.y) < (4*Enemy.tile_size)**2:
				if not self.focus.dead and self.is_loaded:
					self.focus.get_damage(-Healer.HEALING_AMOUNT[self.corrupted])
					self.is_loaded.reset()
		else:
			self.focus = Enemy.get_closer(Healer.CAN_HEAL,(self.x,self.y),Healer.MAX_RANGE[self.corrupted]*Enemy.tile_size)
		
		if self.focus and _dist_2(self.x,self.y,self.focus.x,self.focus.y) > (2*Enemy.tile_size)**2:
			self.vx, self.vy = _vect((self.x, self.y), (self.focus.x, self.focus.y))
			self.vx *= self.v
			self.vy *= self.v
			self.move()
		elif (not self.focus) or (self.focus and self.focus.dead):
			self.vx, self.vy = _vect((self.x, self.y), Enemy.end)
			self.vx *= self.v
			self.vy *= self.v
			self.move()
		if self.focus and self.focus.dead:
			self.focus = None
		
		xb,yb = Enemy.end
		if abs(xb-self.x) + abs(yb-self.y) < self.v:
			self.die(earn=False)
			Enemy.last_lost_life += 1
	
	def on_death(self):
		HealZone(pos=(self.x,self.y))

class HealZone(Enemy):
	follow_path = False
	flying = False

	amount = 0
	corrupted = 0
	
	image = [None, None]
	imrad = 0
	range_im = [None,None]
	
	COIN_VALUE = 200
	CAN_HEAL = [Knight, Goblin, Dragon, KingOfKnights, Giant]
	DEFAULT_RADIUS = [7, 10]
	HEALING_SPEED = [0.075, 0.125]
	HEALING_AMOUNT = [200, 400]
	DEFAULT_HEALTH = [20000, 40000]
	MAX_HEALTH = [20000, 40000]
	MAX_DURATION = [7, 10]

	def __init__(self, corrupted=0, pos=None):
		Enemy.__init__(self, pos=pos, corrupted=corrupted)
		self.is_loaded = Timer(HealZone.HEALING_SPEED[corrupted])
		self.is_loaded2 = Timer(1)
		self.radius = HealZone.DEFAULT_RADIUS[corrupted] * Enemy.tile_size

	def custom_update(self):
		if self.is_loaded:
			at_least_one = Enemy.zone_damage(HealZone.CAN_HEAL, (self.x,self.y), self.radius, -HealZone.HEALING_AMOUNT[self.corrupted])
			if at_least_one:
				self.is_loaded.reset()
		if self.is_loaded2:
			self.is_loaded2.reset()
			self.get_damage(HealZone.MAX_HEALTH[self.corrupted] / HealZone.MAX_DURATION[self.corrupted])

	def on_display(self, SCREEN):
		rect = (self.x-self.radius, self.y-self.radius, *HealZone.range_im[self.corrupted].get_size())
		Enemy.new_rects.append(rect)
		SCREEN.blit(HealZone.range_im[self.corrupted], (rect[0], rect[1]))
