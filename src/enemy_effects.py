class EnemyEffect:
	
	speed = 1
	affected = {}
	subclasses = []
	
	def __init__(self, enemy, level, duration):
		self.tick = 0
		self.target = enemy
		self.level = level
		self.duration = duration
	
	def update():
		for cls in EnemyEffect.subclasses:
			cls._update()
	
	def setup_subclasses():
		EnemyEffect.subclasses = EnemyEffect.__subclasses__()
	
	def _delete(cls, self, active = True):
		self.target.effects[cls.__name__] = None
		if active:
			EnemyEffect.affected[cls.__name__].remove(self)
		del self
	
	def change_speed(speed):
		EnemyEffect.speed = speed
		for cls in EnemyEffect.subclasses:
			for effect in EnemyEffect.affected[cls.__name__]:
				if hasattr(cls, "CLASSIC_RELOAD_SPEED"):
					effect.reload_speed = cls.CLASSIC_RELOAD_SPEED[effect.level] / speed
	
	def clear():
		for cls in EnemyEffect.subclasses:
			EnemyEffect.affected[cls.__name__] = []

class Fire(EnemyEffect):
	name = "Feu"
	DAMAGES = [30,40,50,65,80]
	CLASSIC_RELOAD_SPEED = [100,90,80,70,60]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.reload_speed = Fire.CLASSIC_RELOAD_SPEED[level] / EnemyEffect.speed
		self.damages = Fire.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Fire"]:
			if effect.active:
				effect.duration -= 1
				effect.tick = min(effect.tick + 1, effect.reload_speed)
				if effect.target.dead:
					effect.delete()
				elif effect.tick >= effect.reload_speed:
					effect.tick = 0
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete()
				elif effect.duration <= 0:
					effect.delete()
	
	def delete(self, active=True):
		EnemyEffect._delete(Fire, self, active)


class Poison(EnemyEffect):
	name = "Poison"
	DAMAGES = [100, 120, 140, 180, 250]
	CLASSIC_RELOAD_SPEED = [300, 280, 250, 200, 150]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.reload_speed = Poison.CLASSIC_RELOAD_SPEED[level] / EnemyEffect.speed
		self.damages = Poison.DAMAGES[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Poison"]:
			if effect.active:
				effect.duration -= 1
				effect.tick = min(effect.tick + 1, effect.reload_speed)
				if effect.target.dead:
					effect.delete()
				elif effect.tick >= effect.reload_speed:
					effect.tick = 0
					if not effect.target.dead:
						effect.target.get_damage(effect.damages)
					else:
						effect.delete(all=True)
				elif effect.duration <= 0:
					effect.delete()
		
	def delete(self, active=True):
		EnemyEffect._delete(Poison, self, active)

class Slowness(EnemyEffect):
	name = "Lenteur"
	SLOWING_RATE = [0.8,0.7,0.6,0.5,0.4]
	
	def __init__(self, enemy, level, duration):
		EnemyEffect.__init__(self, enemy, level, duration)
		self.slowing_rate = Slowness.SLOWING_RATE[level]
		self.active = False
	
	def _update():
		for effect in EnemyEffect.affected["Slowness"]:
			if effect.active:
				effect.duration = effect.duration - EnemyEffect.speed
				if effect.target.dead:
					effect.delete()
				elif effect.duration <= 0:
					effect.target.reset_enemy_speed()
					effect.delete()
	
	def delete(self, active = True):
		EnemyEffect._delete(Slowness, self, active)
	
EnemyEffect.setup_subclasses()
