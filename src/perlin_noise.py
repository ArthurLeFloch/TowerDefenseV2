from noise import pnoise2
import numpy as np

def perlin_noise(shape=(200, 200),
				 scale=100, octaves=4,
				 persistence=0.5,
				 lacunarity=2.0,
				 seed=None):
	if not seed:
		seed = np.random.randint(0, 500)

	arr = np.zeros(shape)
	for i in range(shape[0]):
		for j in range(shape[1]):
			arr[i][j] = pnoise2(i / scale,
								j / scale,
								octaves=octaves,
								persistence=persistence,
								lacunarity=lacunarity,
								repeatx=1024,
								repeaty=1024,
								base=seed)
	max_arr = np.max(arr)
	min_arr = np.min(arr)
	def norm_me(x): return (x-min_arr)/(max_arr - min_arr)
	norm_me = np.vectorize(norm_me)
	arr = norm_me(arr)
	return arr
