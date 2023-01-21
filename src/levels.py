class Level:
    level = 0
    xp = 0

    def __init__(self, lvl=1):
        self.level = lvl
        self.xp = 0
    
    def needed_xp(self):
        """
        Returns needed xp for next level
        """
        return 10*self.level**1.5

    def try_leveling_up(self):
        """
        Returns False if leveling up failed, else True.
        """
        needed = self.needed_xp()
        if(self.xp >= needed):
            self.xp -= needed
            self.level += 1
            return True
        return False
