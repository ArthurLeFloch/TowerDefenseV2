import time

class EnemyEffect:
	
	speed = 1
	affected = {}
	subclasses = []
	
	def __init__(self, enemy, level, duration):
		self.target = enemy
		self.level = level
		self.duration = duration
		self.creation = time.time()
		self.last_hit = time.time()
	
	def update():
		for cls in EnemyEffect.subclasses:
			cls._update()
	
	def setup_subclasses():
		EnemyEffect.subclasses = EnemyEffect.__subclasses__()
	
	def has_elapsed(self, last, duration):
		return (time.time() - last) >= duration / EnemyEffect.speed
	
	def _delete(cls, self):
		if self == self.target.effects[cls.__name__]:
			self.target.effects[cls.__name__] = None
		if self.active:
			EnemyEffect.affected[cls.__name__].remove(self)
	
	def change_speed(speed):
		EnemyEffect.speed = speed
	
	def clear():
		for cls in EnemyEffect.subclasses:
			EnemyEffect.affected[cls.__name__] = []

class Fire(EnemyEffect):
	name = "Feu"
	DAMAGES = [30,40,50,65,80]
	CLASSIC_RELOAD_SPEED = [0.25, 0.225, 0.2, 0.175, 0.15]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.damages = Fire.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Fire"]:
			if effect.active:
				if effect.target.dead or effect.has_elapsed(effect.creation, effect.duration):
					effect.delete()
				elif effect.has_elapsed(effect.last_hit, Fire.CLASSIC_RELOAD_SPEED[effect.level]):
					effect.last_hit = time.time()
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete()
	
	def delete(self):
		EnemyEffect._delete(Fire, self)


class Poison(EnemyEffect):
	name = "Poison"
	DAMAGES = [100, 120, 140, 180, 250]
	CLASSIC_RELOAD_SPEED = [0.75, 0.7, 0.625, 0.5, 0.375]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.damages = Poison.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Poison"]:
			if effect.active:
				if effect.target.dead or effect.has_elapsed(effect.creation, effect.duration):
					effect.delete()
				elif effect.has_elapsed(effect.last_hit, Poison.CLASSIC_RELOAD_SPEED[effect.level]):
					effect.last_hit = time.time()
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete()
		
	def delete(self):
		EnemyEffect._delete(Poison, self)


class Slowness(EnemyEffect):
	name = "Lenteur"
	SLOWING_RATE = [0.8, 0.7, 0.6, 0.5, 0.4]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.slowing_rate = Slowness.SLOWING_RATE[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Slowness"]:
			if effect.active:
				if effect.target.dead or effect.has_elapsed(effect.creation, effect.duration):
					effect.delete()
	
	def delete(self):
		EnemyEffect._delete(Slowness, self)
	
EnemyEffect.setup_subclasses()
