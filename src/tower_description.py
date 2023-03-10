class TowerDescription:
	LEVEL = None
	RANGE = None
	DAMAGE = None
	DPS = None
	MUL_DAMAGE = None
	MUL_RANGE = None
	MUL_SPEED = None
	EXPL_RANGE = None
	EFFECT_LEVEL = None
	EFFECT_DURATION = None
	MUL_SLOWNESS = None
	EFFECT_DPS = None
	RELOAD_SPEED = None
	EARN_PER_ACTION = None
	EARN_PER_SEC = None
	GOLD_TOUCH = None

	def __init__(self, text, value):
		self.text = text + " : "
		self.value = str(value).replace('.', ',')
	
	def setup_language(tr):
		TowerDescription.LEVEL = tr.tower_desc_level
		TowerDescription.RANGE = tr.tower_desc_range
		TowerDescription.DAMAGE = tr.tower_desc_damage
		TowerDescription.DPS = tr.tower_desc_dps
		TowerDescription.MUL_DAMAGE = tr.tower_desc_mul_damage
		TowerDescription.MUL_RANGE = tr.tower_desc_mul_range
		TowerDescription.MUL_SPEED = tr.tower_desc_mul_speed
		TowerDescription.EXPL_RANGE = tr.tower_desc_expl_range
		TowerDescription.EFFECT_LEVEL = tr.tower_desc_effect_level
		TowerDescription.EFFECT_DURATION = tr.tower_desc_effect_duration
		TowerDescription.MUL_SLOWNESS = tr.tower_desc_mul_slowness
		TowerDescription.EFFECT_DPS = tr.tower_desc_effect_dps
		TowerDescription.RELOAD_SPEED = tr.tower_desc_reload_speed
		TowerDescription.EARN_PER_ACTION = tr.tower_desc_earn_per_action
		TowerDescription.EARN_PER_SEC = tr.tower_desc_earn_per_sec
		TowerDescription.GOLD_TOUCH = tr.tower_desc_gold_touch

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
		text = TowerDescription.LEVEL

		if upgrade:
			value = instance.lvl+1
			new_value = instance.lvl+1+1
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = instance.lvl+1
			return InstanceDescription(text, value)

	def range(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.RANGE

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
		text = TowerDescription.DAMAGE

		if upgrade and cls.CLASSIC_DAMAGE[instance.lvl] != cls.CLASSIC_DAMAGE[instance.lvl+1]:
			value = cls.CLASSIC_DAMAGE[instance.lvl]
			new_value = cls.CLASSIC_DAMAGE[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = round(instance.damage)
			is_boosted = (instance.damage_multiplier != 1)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def damage_per_sec(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.DPS

		if upgrade and cls.CLASSIC_DAMAGE[instance.lvl] < cls.CLASSIC_DAMAGE[instance.lvl+1]:
			value = round(cls.CLASSIC_DAMAGE[instance.lvl]/cls.CLASSIC_RELOAD_SPEED[instance.lvl])
			new_value = round(cls.CLASSIC_DAMAGE[instance.lvl+1]/cls.CLASSIC_RELOAD_SPEED[instance.lvl+1])
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = (instance.damage_multiplier != 1 or instance.speed_multiplier != 1)
			value = round(instance.damage*instance.speed_multiplier/cls.CLASSIC_RELOAD_SPEED[instance.lvl])
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def damage_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.MUL_DAMAGE

		if upgrade and cls.DAMAGE_MULTIPLIER[instance.lvl] != cls.DAMAGE_MULTIPLIER[instance.lvl+1]:
			value = cls.DAMAGE_MULTIPLIER[instance.lvl]
			new_value = cls.DAMAGE_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.DAMAGE_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def range_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.MUL_RANGE

		if upgrade and cls.RANGE_MULTIPLIER[instance.lvl] != cls.RANGE_MULTIPLIER[instance.lvl+1]:
			value = cls.RANGE_MULTIPLIER[instance.lvl]
			new_value = cls.RANGE_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.RANGE_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def speed_multiplier(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.MUL_SPEED

		if upgrade and cls.SPEED_MULTIPLIER[instance.lvl] != cls.SPEED_MULTIPLIER[instance.lvl+1]:
			value = cls.SPEED_MULTIPLIER[instance.lvl]
			new_value = cls.SPEED_MULTIPLIER[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.SPEED_MULTIPLIER[instance.lvl]
			return InstanceDescription(text, value)
	
	def explosion_radius(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EXPL_RANGE

		if upgrade and cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl] != cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl+1]:
			value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl]
			new_value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.CLASSIC_EXPLOSION_RADIUS[instance.lvl]
			return InstanceDescription(text, value)

	def effect_level(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EFFECT_LEVEL.format(effect_name=cls.effect.name)

		if upgrade and cls.EFFECT_LEVEL[instance.lvl] != cls.EFFECT_LEVEL[instance.lvl+1]:
			value = cls.EFFECT_LEVEL[instance.lvl]+1
			new_value = cls.EFFECT_LEVEL[instance.lvl+1]+1
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.EFFECT_LEVEL[instance.lvl]+1
			return InstanceDescription(text, value)

	def effect_duration(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EFFECT_DURATION

		if upgrade and cls.CLASSIC_DURATION[instance.lvl] != cls.CLASSIC_DURATION[instance.lvl+1]:
			value = cls.CLASSIC_DURATION[instance.lvl]
			new_value = cls.CLASSIC_DURATION[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.CLASSIC_DURATION[instance.lvl]
			return InstanceDescription(text, value)
	
	def slowness_factor(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.MUL_SLOWNESS

		if upgrade and cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]] != cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl+1]]:
			value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]]
			new_value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl+1]]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[instance.lvl]]
			return InstanceDescription(text, value)
	
	def effect_damage_per_sec(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EFFECT_DPS

		if upgrade and cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]] != cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl+1]]:
			value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl]])
			new_value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl+1]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl+1]])
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[instance.lvl]]/cls.effect.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[instance.lvl]])
			return InstanceDescription(text, value)
	
	def reload_speed(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.RELOAD_SPEED

		if upgrade and cls.CLASSIC_RELOAD_SPEED[instance.lvl] != cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]:
			value = cls.CLASSIC_RELOAD_SPEED[instance.lvl]
			new_value = cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = instance.speed_multiplier != 1
			value = round(cls.CLASSIC_RELOAD_SPEED[instance.lvl]/instance.speed_multiplier, 2)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def earn_per_action(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EARN_PER_ACTION

		if upgrade and cls.EARNS[instance.lvl] != cls.EARNS[instance.lvl+1]:
			value = cls.EARNS[instance.lvl]
			new_value = cls.EARNS[instance.lvl+1]
			return InstanceDescription(text, value, new_value=new_value)
		else:
			value = cls.EARNS[instance.lvl]
			return InstanceDescription(text, value)
	
	def earn_per_sec(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.EARN_PER_SEC

		if upgrade and (cls.EARNS[instance.lvl] != cls.EARNS[instance.lvl+1] or cls.CLASSIC_RELOAD_SPEED[instance.lvl] != cls.CLASSIC_RELOAD_SPEED[instance.lvl+1]):
			value = round(cls.EARNS[instance.lvl]/cls.CLASSIC_RELOAD_SPEED[instance.lvl], 2)
			new_value = round(cls.EARNS[instance.lvl+1]/cls.CLASSIC_RELOAD_SPEED[instance.lvl+1], 2)
			return InstanceDescription(text, value, new_value=new_value)
		else:
			is_boosted = instance.speed_multiplier != 1
			value = round(cls.EARNS[instance.lvl]*instance.speed_multiplier/cls.CLASSIC_RELOAD_SPEED[instance.lvl], 2)
			return InstanceDescription(text, value, is_boosted=is_boosted)
	
	def gold_touch(instance, upgrade=False):
		cls = instance.__class__
		text = TowerDescription.GOLD_TOUCH

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
		text = TowerDescription.RANGE
		value = cls.CLASSIC_RANGE[0]
		return ShopDescription(text, value)
	
	def damage(cls):
		text = TowerDescription.DAMAGE
		value = cls.CLASSIC_DAMAGE[0]
		return ShopDescription(text, value)
	
	def damage_per_sec(cls):
		text = TowerDescription.DPS
		value = round(cls.CLASSIC_DAMAGE[0]/cls.CLASSIC_RELOAD_SPEED[0])
		return ShopDescription(text, value)
	
	def damage_multiplier(cls):
		text = TowerDescription.MUL_DAMAGE
		value = cls.DAMAGE_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def range_multiplier(cls):
		text = TowerDescription.MUL_RANGE
		value = cls.RANGE_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def speed_multiplier(cls):
		text = TowerDescription.MUL_SPEED
		value = cls.SPEED_MULTIPLIER[0]
		return ShopDescription(text, value)
	
	def explosion_radius(cls):
		text = TowerDescription.EXPL_RANGE
		value = cls.CLASSIC_EXPLOSION_RADIUS[0]
		return ShopDescription(text, value)

	def effect_level(cls):
		text = TowerDescription.EFFECT_LEVEL.format(effect_name=cls.effect.name)
		value = cls.EFFECT_LEVEL[0]+1
		return ShopDescription(text, value)

	def effect_duration(cls):
		text = TowerDescription.EFFECT_DURATION
		value = cls.CLASSIC_DURATION[0]
		return ShopDescription(text, value)
	
	def effect_damage_per_sec(cls):
		text = TowerDescription.EFFECT_DPS
		value = round(cls.effect.DAMAGES[cls.EFFECT_LEVEL[0]]/cls.CLASSIC_RELOAD_SPEED[cls.EFFECT_LEVEL[0]])
		return ShopDescription(text, value)
	
	def slowness_factor(cls):
		text = TowerDescription.MUL_SLOWNESS
		value = cls.effect.SLOWING_RATE[cls.EFFECT_LEVEL[0]]
		return ShopDescription(text, value)
	
	def reload_speed(cls):
		text = TowerDescription.RELOAD_SPEED
		value = cls.CLASSIC_RELOAD_SPEED[0]
		return ShopDescription(text, value)
	
	def earn_per_action(cls):
		text = TowerDescription.EARN_PER_ACTION
		value = cls.EARNS[0]
		return ShopDescription(text, value)
	
	def earn_per_sec(cls):
		text = TowerDescription.EARN_PER_SEC
		value = round(cls.EARNS[0]/cls.CLASSIC_RELOAD_SPEED[0], 2)
		return ShopDescription(text, value)
