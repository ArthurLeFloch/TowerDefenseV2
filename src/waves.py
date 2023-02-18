from random import randint as rdi

from enemies import Enemy, Knight, Goblin, Dragon, KingOfKnights, Giant, Healer, HealZone
from logs import Logs
from timer import Timer

def printf(args):
	Logs.print('waves',args)

class Wave:
	currentLevel = 0

	DEFAULT_WAIT_DURATION = 5.0
	DEFAULT_WAIT_BETWEEN_WAVES = True
	DEFAULT_AUTO_PAUSE = False
	DEFAULT_TIME_BETWEEN_ENEMIES = 1.0
	DEFAULT_HEALTH_FACTOR = 0.3
	DEFAULT_SPAWNING_FACTOR = 1.0
	DEFAULT_CORRUPTED_CHANCE = 0

	wait_duration = 5.0
	wait_between_waves = True
	auto_pause = False
	time_between_enemies = 1.0
	health_factor = 0.3
	spawning_factor = 1.0
	corrupted_chance = 0
	
	def __init__(self):
		Wave.currentLevel += 1
		self.lvl = Wave.currentLevel
		self.wave = []
		Wave.generate(self.wave, self.lvl)
		self.length = len(self.wave)
		self.is_loaded = Timer(Wave.time_between_enemies)
	
	def setup_const():
		Wave.wait_duration = Wave.DEFAULT_WAIT_DURATION
		Wave.wait_between_waves = Wave.DEFAULT_WAIT_BETWEEN_WAVES
		Wave.auto_pause = Wave.DEFAULT_AUTO_PAUSE
		Wave.time_between_enemies = Wave.DEFAULT_TIME_BETWEEN_ENEMIES
		Wave.health_factor = Wave.DEFAULT_HEALTH_FACTOR
		Wave.spawning_factor = Wave.DEFAULT_SPAWNING_FACTOR
		Wave.corrupted_chance = Wave.DEFAULT_CORRUPTED_CHANCE
	
	def rdc():
		val = rdi(0, 100)
		return (val <= Wave.corrupted_chance)

	def generate(wave, lvl):
		Enemy.update_health(lvl, Wave.health_factor)
		spawning_factor = Wave.spawning_factor

		tmp = (lvl+5)//5
		
		k = 1 + int(5*rdi(1,1 + (lvl%5))*tmp*spawning_factor)
		g=d=0
		if tmp > 1:
			g = 1 + int(5*rdi(1,1 + (lvl%5))*tmp*spawning_factor)
		if tmp > 2:
			d = 1 + int(5*rdi(1,1 + (lvl%5))*tmp*spawning_factor)
		
		for _ in range(k):
			wave.append([Knight, Wave.rdc()])
		for _ in range(g):
			wave.append([Goblin, Wave.rdc()])
		for _ in range(d):
			wave.append([Dragon, Wave.rdc()])
		
		if lvl%10==5:
			for _ in range(tmp-1):
				wave.insert(rdi(0, len(wave)-1), [KingOfKnights, Wave.rdc()])
		elif lvl%10==0:
			for _ in range(tmp-1):
				wave.insert(rdi(0, len(wave)-1), [Giant, Wave.rdc()])
		
		if lvl > 10 and rdi(0, 3) == 0:
			for _ in range(rdi(1, 3)):
				wave.insert(rdi(0, len(wave)-1), [Healer, Wave.rdc()])
		
		Enemy.print_health_update()
		printf(f"New wave length : \t{len(wave)}")


if __name__ == '__main__':
	import matplotlib.pyplot as plt
	max_wave = 1000
	results = []
	for w in range(max_wave):
		current_wave = Wave().wave
		s=0
		for x in current_wave:
			if x[0] == Healer:
				s+=1
		results.append(s)
	x = [k for k in range(max_wave)]
	plt.plot(x, results)
	plt.title("'Healer' count per wave")
	plt.grid()
	plt.show()

	Wave.currentLevel = 0
