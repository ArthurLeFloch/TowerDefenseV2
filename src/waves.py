from random import randint as rdi

from enemies import Enemy, Knight, Goblin, Dragon, KingOfKnights, Giant, Healer, HealZone
from logs import Logs

def printf(args):
	Logs.print('waves',args)

class Wave:
	currentLevel = 0
	
	def __init__(self, difficulty=1):
		Wave.currentLevel += 1
		self.lvl = Wave.currentLevel
		self.difficulty = difficulty
		self.wave = []
		Wave.generate(self.wave, self.lvl, difficulty)
		self.length = len(self.wave)

	def generate(wave, lvl, difficulty):
		Enemy.update_health(lvl, difficulty)

		tmp = (lvl+5)//5
		
		k = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
		g=d=0
		if tmp > 1:
			g = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
		if tmp > 2:
			d = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
		
		for _ in range(k):
			wave.append([Knight, 0])
		for _ in range(g):
			wave.append([Goblin, 0])
		for _ in range(d):
			wave.append([Dragon, 0])
		
		if lvl%10==5:
			for _ in range(tmp-1):
				wave.insert(rdi(0, len(wave)-1), [KingOfKnights, 0])
		elif lvl%10==0:
			for _ in range(tmp-1):
				wave.insert(rdi(0, len(wave)-1), [Giant, 0])
		
		if lvl > 10 and rdi(0, 3) == 0:
			for _ in range(rdi(1, 3)):
				wave.insert(rdi(0, len(wave)-1), [Healer, 0])
		
		Enemy.print_health_update()
		printf(f"New wave length : \t{len(wave)}")


if __name__ == '__main__':
	import matplotlib.pyplot as plt
	max_wave = 1000
	#test Knights
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
	plt.title("Nombre de 'Healer' par vagues")
	plt.grid()
	plt.show()

	Wave.currentLevel = 0
