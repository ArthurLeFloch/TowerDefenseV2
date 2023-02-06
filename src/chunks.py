class Chunk:
	game = None
	dimensions = None
	SIZE = 3
	subclasses = []
	
	def __init__(self, x, y, content = []):
		self.x = x
		self.y = y
		self.content = {}
		for cls in Chunk.subclasses:
			self.content[cls.__name__] = []

	def setup_array(n, m):
		Chunk.game = []
		for i in range(int(n/Chunk.SIZE) + 1):
			Chunk.game.append([])
			for j in range(int(m/Chunk.SIZE) + 1):
				Chunk.game[-1].append(Chunk(i, j))
		Chunk.dimensions = (int(n/Chunk.SIZE) + 1, int(m/Chunk.SIZE) + 1)
	
	def setup(cls_enemies):
		Chunk.subclasses = cls_enemies
		
	def get_range_chunk(x, y, radius, tile_size):
		x_min_chunk, y_min_chunk = int((x-radius)/(Chunk.SIZE * tile_size)), int((y-radius)/(Chunk.SIZE * tile_size))
		x_max_chunk, y_max_chunk = int((x+radius)/(Chunk.SIZE * tile_size)), int((y+radius)/(Chunk.SIZE * tile_size))
		x_min_chunk, y_min_chunk = max(0, x_min_chunk), max(0, y_min_chunk)
		x_max_chunk, y_max_chunk = min(Chunk.dimensions[0]-1, x_max_chunk), min(Chunk.dimensions[1]-1, y_max_chunk)
		result = []
		for xc in range(x_min_chunk, x_max_chunk+1):
			for yc in range(y_min_chunk, y_max_chunk+1):
				result.append((xc,yc))
		return result
	
	def coords_to_chunk(x, y, xoffset, yoffset, tile_size):
		return int((x - xoffset) / (Chunk.SIZE * tile_size)), int((y - yoffset) / (Chunk.SIZE * tile_size))
			