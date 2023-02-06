class TowerDescription:
	def __init__(self, text, value):
		self.text = text + " : "
		self.value = str(value).replace('.', ',')

class InstanceDescription(TowerDescription):
	def __init__(self, text, value, new_value=None, is_boosted=False):
		TowerDescription.__init__(self, text, value)
		if new_value:
			new_value = " -> " + str(new_value).replace('.', ',')
		self.new_value = new_value
		self.is_boosted = is_boosted
	
	@property
	def total_text(self):
		return self.text + self.value + ("" if not self.new_value else self.new_value) + ('0' if not self.is_boosted else '1')
	
	def are_identical(l1, l2):
		if None in (l1, l2):
			return False
		if len(l1) != len(l2):
			return False
		
		for k in range(len(l1)):
			self, other = l1[k], l2[k]
			if self.total_text != other.total_text:
				return False
		return True

	def level(instance, upgrade=False):
		text = "Niveau"

		if upgrade:
			value = instance.lvl+1
			new_value = instance.lvl+1+1
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = instance.lvl+1
			return InstanceDescription(text, value)

	def range(instance, upgrade=False):
		cls = instance.__class__
		text = "Portée"

		if upgrade and cls.CLASSIC_RANGE[instance.lvl] != cls.CLASSIC_RANGE[instance.lvl+1]:
			value = cls.CLASSIC_RANGE[instance.lvl]
			new_value = cls.CLASSIC_RANGE[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = round(cls.CLASSIC_RANGE[instance.lvl]*instance.range_multiplier, 2)
			is_boosted = (instance.range_multiplier != 1)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def damage(instance, upgrade=False):
		cls = instance.__class__
		text = "Dégâts"

		if upgrade and cls.CLASSIC_DAMAGE[instance.lvl] != cls.CLASSIC_DAMAGE[instance.lvl+1]:
			value = cls.CLASSIC_DAMAGE[instance.lvl]
			new_value = cls.CLASSIC_DAMAGE[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = round(instance.damage)
			is_boosted = (instance.damage_multiplier != 1)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def damage_per_tick(instance, upgrade=False):
		cls = instance.__class__
		text = "Dégâts / tick"

		if upgrade and cls.CLASSIC_DAMAGE[instance.lvl] < cls.CLASSIC_DAMAGE[instance.lvl+1]:
			value = round(cls.CLASSIC_DAMAGE[instance.lvl]/cls.CLASSIC_RELOAD_SPEED[instance.lvl], 2)
			new_value = round(cls.CLASSIC_DAMAGE[instance.lvl+1]/cls.CLASSIC_RELOAD_SPEED[instance.lvl+1], 2)
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = (instance.damage_multiplier != 1 or instance.speed_multiplier != 1)
			value = round(instance.damage*instance.speed_multiplier/cls.CLASSIC_RELOAD_SPEED[instance.lvl], 2)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def damage_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = "Mul. de dégâts"

		if upgrade and cls.DAMAGE_MULTIPLIER[instance.lvl] != cls.DAMAGE_MULTIPLIER[instance.lvl+1]:
			value = cls.DAMAGE_MULTIPLIER[instance.lvl]
			new_value = cls.DAMAGE_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.DAMAGE_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def range_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = "Mul. de portée"

		if upgrade and cls.RANGE_MULTIPLIER[instance.lvl] != cls.RANGE_MULTIPLIER[instance.lvl+1]:
			value = cls.RANGE_MULTIPLIER[instance.lvl]
			new_value = cls.RANGE_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.RANGE_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def speed_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = "Mul. de vitesse"

		if upgrade and cls.SPEED_MULTIPLIER[instance.lvl] != cls.SPEED_MULTIPLIER[instance.lvl+1]:
			value = cls.SPEED_MULTIPLIER[instance.lvl]
			new_value = cls.SPEED_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.SPEED_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def explosion_radius(instance, upgrade=False):
		cls = instance.__class__
		text = "Rayon d'explosion"

		if upgrade and cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl] != cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl+1]:
			value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl]
			new_value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl]
			return InstanceDescription(text, value)

	def effect_level(instance, upgrade=False):
		cls = instance.__class__
		text = f"Niveau de {cls.effect.name}"

		if upgrade and cls.EFFECT_LEVEL[instance.lvl] != cls.EFFECT_LEVEL[instance.lvl+1]:
			value = cls.EFFECT_LEVEL[instance.lvl]+1
			new_value = cls.EFFECT_LEVEL[instance.lvl+1]+1
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.EFFECT_LEVEL[instance.lvl]+1
			return InstanceDescription(text, value)

	def effect_duration(instance, upgrade=False):
		cls = instance.__class__
		text = "Durée"

		if upgrade and cls.CLASSIC_DURATION[cls.EFFECT_LEVEL[instance.lvl]] != cls.CLASSIC_DURATION[cls.EFFECT_LEVEL[instance.lvl+1]]:
			value = cls.CLASSIC_DURATION[cls.EFFECT_LEVEL[instance.lvl]]
			new_value = cls.CLASSIC_DURATION[cls.EFFECT_LEVEL[instance.lvl+1]]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.CLASSIC_DURATION[cls.EFFECT_LEVEL[instance.lvl]]
			return InstanceDescription(text, value)
	
	def slowness_factor(instance, upgrade=False):
		cls = instance.__class__
		text = "Facteur"

		if upgrade and cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]] != cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl+1]]:
			value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]]
			new_value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl+1]]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]]
			return InstanceDescription(text, value)
	
	def effect_damage_per_tick(instance, upgrade=False):
		cls = instance.__class__
		text = "Dégâts / tick"

		if upgrade and cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]] != cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl+1]]:
			value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl]], 2)
			new_value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl+1]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl+1]], 2)
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl]], 2)
			return InstanceDescription(text, value)
	
	def reload_speed(instance, upgrade=False):
		cls = instance.__class__
		text = "Durée action"

		if upgrade and cls.CLASSIC_RELOAD_SPEED[instance.lvl] != cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]:
			value = cls.CLASSIC_RELOAD_SPEED[instance.lvl]
			new_value = cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = instance.speed_multiplier != 1
			value = round(cls.CLASSIC_RELOAD_SPEED[instance.lvl]/instance.speed_multiplier)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def earn_per_action(instance, upgrade=False):
		cls = instance.__class__
		text = "$ / action"

		if upgrade and cls.EARNS[instance.lvl] != cls.EARNS[instance.lvl+1]:
			value = cls.EARNS[instance.lvl]
			new_value = cls.EARNS[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.EARNS[instance.lvl]
			return InstanceDescription(text, value)
	
	def earn_per_tick(instance, upgrade=False):
		cls = instance.__class__
		text = "$ / tick"

		if upgrade and (cls.EARNS[instance.lvl] != cls.EARNS[instance.lvl+1] or cls.CLASSIC_RELOAD_SPEED[instance.lvl] != cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]):
			value = round(cls.EARNS[instance.lvl]/cls.CLASSIC_RELOAD_SPEED[instance.lvl],4)
			new_value = round(cls.EARNS[instance.lvl+1]/cls.CLASSIC_RELOAD_SPEED[instance.lvl+1],4)
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = instance.speed_multiplier != 1
			value = round(cls.EARNS[instance.lvl]*instance.speed_multiplier/cls.CLASSIC_RELOAD_SPEED[instance.lvl],4)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def gold_touch(instance, upgrade=False):
		cls = instance.__class__
		text = "$ / tir"

		if upgrade and cls.GOLD_TOUCH_AMOUNT[instance.lvl] < cls.GOLD_TOUCH_AMOUNT[instance.lvl+1]:
			value = cls.GOLD_TOUCH_AMOUNT[instance.lvl]
			new_value = cls.GOLD_TOUCH_AMOUNT[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.GOLD_TOUCH_AMOUNT[instance.lvl]
			return InstanceDescription(text, value)

class ShopDescription(TowerDescription):
	def __init__(self, text, value):
		TowerDescription.__init__(self, text, value)
	
	def range(cls):
		text = "Portée"
		value = cls.CLASSIC_RANGE[0]
		return ShopDescription(text, value)
	
	def damage(cls):
		text = "Dégâts"
		value = cls.CLASSIC_DAMAGE[0]
		return ShopDescription(text, value)
	
	def damage_per_tick(cls):
		text = "Dégâts / tick"
		value = round(cls.CLASSIC_DAMAGE[0]/cls.CLASSIC_RELOAD_SPEED[0], 2)
		return ShopDescription(text, value)
	
	def damage_multiplier(cls):
		text = "Mul. de dégâts"
		value = cls.DAMAGE_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def range_multiplier(cls):
		text = "Mul. de portée"
		value = cls.RANGE_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def speed_multiplier(cls):
		text = "Mul. de vitesse"
		value = cls.SPEED_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def explosion_radius(cls):
		text = "Rayon d'explosion"
		value = cls.CLASSIC_EXPLOSION_RADIUS[0]
		return ShopDescription(text, value)

	def effect_level(cls):
		text = f"Niveau de {cls.effect.name}"
		value = cls.EFFECT_LEVEL[0]+1
		return ShopDescription(text, value)

	def effect_duration(cls):
		text = "Durée"
		value = cls.CLASSIC_DURATION[0]
		return ShopDescription(text, value)
	
	def effect_damage_per_tick(cls):
		text = "Dégâts / tick"
		value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[0]]/cls.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[0]], 2)
		return ShopDescription(text, value)
	
	def slowness_factor(cls):
		text = "Facteur"
		value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[0]]
		return ShopDescription(text, value)
	
	def reload_speed(cls):
		text = "Durée action"
		value = cls.CLASSIC_RELOAD_SPEED[0]
		return ShopDescription(text, value)
	
	def earn_per_action(cls):
		text = "$ / action"
		value = cls.EARNS[0]
		return ShopDescription(text, value)
	
	def earn_per_tick(cls):
		text = "$ / tick"
		value = round(cls.EARNS[0]/cls.CLASSIC_RELOAD_SPEED[0],4)
		return ShopDescription(text, value)
