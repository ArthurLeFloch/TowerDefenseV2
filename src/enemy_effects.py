from timer import Timer

class EnemyEffect:
	
	speed = 1
	affected = {}
	subclasses = []

	last_pause = None
	
	def __init__(self, enemy, level, duration):
		self.target = enemy
		self.level = level
		self.duration = duration
		self.is_dead = Timer(duration)
	
	def update():
		for cls in EnemyEffect.subclasses:
			cls._update()
	
	def setup_subclasses():
		EnemyEffect.subclasses = EnemyEffect.__subclasses__()
	
	def delete(self):
		name = self.__class__.__name__
		if self == self.target.effects[name]:
			self.target.effects[name] = None
		if self.active:
			EnemyEffect.affected[name].remove(self)
		self.is_dead.delete()
		if hasattr(self, "is_loaded"):
			self.is_loaded.delete()
	
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
		self.is_loaded = Timer(Fire.CLASSIC_RELOAD_SPEED[level])
		self.damages = Fire.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Fire"]:
			if effect.active:
				if effect.target.dead or effect.is_dead:
					effect.delete()
				elif effect.is_loaded:
					effect.is_loaded.reset()
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete()


class Poison(EnemyEffect):
	name = "Poison"
	DAMAGES = [100, 120, 140, 180, 250]
	CLASSIC_RELOAD_SPEED = [0.75, 0.7, 0.625, 0.5, 0.375]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.is_loaded = Timer(Poison.CLASSIC_RELOAD_SPEED[level])
		self.damages = Poison.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Poison"]:
			if effect.active:
				if effect.target.dead or effect.is_dead:
					effect.delete()
				elif effect.is_loaded:
					effect.is_loaded.reset()
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete()


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
				if effect.target.dead or effect.is_dead:
					effect.delete()


EnemyEffect.setup_subclasses()
