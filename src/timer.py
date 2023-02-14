import time

class Timer:

	speed = 1

	last_pause = None

	list = []

	def __init__(self, duration):
		self.duration = duration
		self.started = time.time()
		Timer.list.append(self)
	
	def __bool__(self):
		return self.has_elapsed
	
	def reset(self):
		self.started = time.time()
	
	def change_duration(self, duration):
		self.duration = duration
		self.started = time.time()
	
	def delete(self):
		Timer.list.remove(self)
	
	@property
	def has_elapsed(self):
		return (time.time() - self.started) >= (self.duration / Timer.speed)
	
	@classmethod
	def pause(cls):
		cls.last_pause = time.time()
	
	@classmethod
	def resume(cls):
		offset = time.time() - cls.last_pause
		for t in cls.list:
			t.started += offset
		cls.last_pause = None
	