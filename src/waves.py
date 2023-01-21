from random import randint as rdi

from enemies import KingOfKnights, Knight, Goblin, Dragon, Healer, HealZone, Giant
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
    
    def generate(wave,lvl,difficulty):
        tmp = int(Knight.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*Knight.DEFAULT_HEALTH[0]/3)
        Knight.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(Goblin.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*Goblin.DEFAULT_HEALTH[0]/3)
        Goblin.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(Dragon.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*Dragon.DEFAULT_HEALTH[0]/3)
        Dragon.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(KingOfKnights.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*KingOfKnights.DEFAULT_HEALTH[0]/3)
        KingOfKnights.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(Giant.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*Giant.DEFAULT_HEALTH[0]/3)
        Giant.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(Healer.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*Healer.DEFAULT_HEALTH[0]/3)
        Healer.MAX_HEALTH = [tmp,2*tmp]
        tmp = int(HealZone.DEFAULT_HEALTH[0]+(lvl-1)*difficulty*HealZone.DEFAULT_HEALTH[0]/3)
        HealZone.MAX_HEALTH = [tmp,2*tmp]

        tmp = (lvl+5)//5
        
        k = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
        g=d=0
        if tmp > 1:
            g = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
        if tmp > 2:
            d = int(5*rdi(1,1 + (lvl%5))*tmp*difficulty)
        
        for _ in range(k):
            wave.append([Knight,0])
        for _ in range(g):
            wave.append([Goblin,0])
        for _ in range(d):
            wave.append([Dragon,0])
        if lvl%10==5:
            for _ in range(tmp-1):
                wave.insert(rdi(0,len(wave)-1),[KingOfKnights,0])
        elif lvl%10==0:
            for _ in range(tmp-1):
                wave.insert(rdi(0,len(wave)-1),[Giant,0])
        
        printf(f'Knight : {Knight.MAX_HEALTH}, Goblin : {Goblin.MAX_HEALTH}, Dragon : {Dragon.MAX_HEALTH}, King of Knights : {KingOfKnights.MAX_HEALTH}, Giant : {Giant.MAX_HEALTH}, Wave length : {len(wave)}')


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    max_wave = 1000
    #test Knights
    results = []
    Wave.setup([])
    for w in range(max_wave):
        current_wave = Wave().wave
        s=0
        for x in current_wave:
            if x[0] == Knight:
                s+=1
        results.append(s)
    x = [k for k in range(max_wave)]
    plt.plot(x, results)
    plt.title("Nombre de 'Knights' par vagues")
    plt.grid()
    plt.show()

    Wave.currentLevel = 0
