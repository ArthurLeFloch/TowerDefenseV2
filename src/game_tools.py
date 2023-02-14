import numpy as np
import time
from random import randint as rdi
from collections import deque

from perlin_noise import perlin_noise
from logs import Logs

def printf(args):
	Logs.print('game_tools',args)

def adj(size,i,j):
	n,m = size
	l=[]
	if j+1<m: l.append((i,j+1))
	if i>0: l.append((i-1,j))
	if j>0: l.append((i,j-1))
	if i+1<n: l.append((i+1,j))
	return l

def are_starts_espaced(starts, tol=2):
	for s1 in starts:
		for s2 in starts:
			if s1 != s2:
				if abs(s2[0]-s1[0]) <= tol or abs(s2[1]-s1[1]) <= tol:
					return False
	return True

def are_starts_end_valid(starts, end, x, y):
	result = are_starts_espaced(starts)
	i = 0
	while result and i != len(starts):
		result = abs(starts[i][0] - end[0]) + abs(starts[i][1]-end[1])>(x+y)/4
		i = i+1
	return result

def are_lengths_valid(paths, x, y):
	result = True
	i = 0
	while result and i != len(paths):
		result = len(paths[i]) > (x+y)/4
		i = i+1
	return result

def set_starts_end(x, y, start_count):
	starts = [(rdi(0,x-1),rdi(0,y-1)) for _ in range(start_count)]
	end = rdi(0,x-1), rdi(0,y-1)
	while not are_starts_end_valid(starts, end, x, y):
		starts = [(rdi(0,x-1),rdi(0,y-1)) for _ in range(start_count)]
		end = rdi(0,x-1), rdi(0,y-1)
	return starts, end

def goback(arr, prec, start, end):
	i, j = end
	l = [end]
	while (i, j) != start:
		i, j = prec[i, j]
		if (i, j) == (-1, -1):
			raise KeyError
		arr[i, j] = 2
		l.append((i, j))
	arr[start] = 3
	arr[end] = 4
	return l[::-1]

def get_path_from_start(x, y, game, start, end):
	pile = []
	prev = -np.ones((x, y, 2))
	done = np.zeros((x, y))
	
	i,j = start

	pile.append((i,j))
	done[i, j] = 1
	prev[i, j] = [-1, -1]

	dist = 0
	while len(pile) != 0:
		dist += 1
		i, j = pile.pop(0)
		adjacents = adj((x, y), i, j)
		for (l, m) in adjacents:
			if game[l, m] in [1, 2, 3, 4] and not done[l, m]:
				pile.append((l, m))
				done[l, m] = 1
				prev[l, m] = [i, j]
	return goback(game, prev.astype(int), start, end)

def adapt_perlin(x, y, randomized, mini):
	game = np.ones((x,y))
	if randomized:
		per = perlin_noise((x,y),20,8)
		for i in range(x):
			for j in range(y):
				if per[i][j] < mini:
					game[i,j] = 0
	return game_of_life(game, x, y)

def neighbors(game, size, tile):
	i, j = tile
	n, m = size
	l = []
	if j+1<m and not game[i,j+1] in [0, 5]: l.append((i,j+1))
	if i>0 and not game[i-1,j] in [0, 5]: l.append((i-1,j))
	if j>0 and not game[i,j-1] in [0, 5]: l.append((i,j-1))
	if i+1<n and not game[i+1,j] in [0, 5]: l.append((i+1,j))
	return l


def findpath(game, size, starts, end):
	prev = [[(-1, -1) for _ in range(size[1])] for _ in range(size[0])]
	stack = deque([end])
	while len(stack) > 0:
		tile = stack.popleft()
		for i, j in neighbors(game, size, tile):
			if prev[i][j] == (-1, -1):
				stack.append((i, j))
				prev[i][j] = tile
	paths = []
	for start in starts:
		result = []
		i, j = start
		while (i, j) != end:
			result.append((i, j))
			i, j = prev[i][j]
			if (i, j) == (-1, -1):
				raise KeyError
			game[i, j] = 2
		result.append(end)
		paths.append(result)
	
	for start in starts:
		game[start] = 3
	game[end] = 4

	return paths

def generate(x, y, start_count, minimum=0.55, empty_forest=False):
	printf("Generating map")
	t = time.time()

	starts, end = set_starts_end(x, y, start_count)
	tries = 0
	paths = []
	randomized = (minimum != 0)

	game = adapt_perlin(x, y, randomized, minimum)
		
	while True:
		gcopy = game.copy()
		starts, end = set_starts_end(x, y, start_count)
		
		try:
			paths = findpath(gcopy, (x, y), starts, end)
		except KeyError:
			tries += 1
			if tries % 10 == 0:
				printf(f'Findpath try n°{tries} failed, trying findpath on new map')
				game = adapt_perlin(x, y, randomized, minimum)
		else:
			if are_lengths_valid(paths, x, y):
				game = gcopy.copy()
				break
			else:
				tries += 1
	forests = generate_forest(game, x, y, empty_forest)
	printf(f"Execution time : {time.time()-t}")
	return game, paths, starts, end, forests


def game_of_life(game, n, m):
	def neighbours_count(array, i, j):
		count = 0
		for x in range(max(0, i-1), min(n, i+2)):
			for y in range(max(0, j-1), min(m, j+2)):
				if (x, y) != (i, j) and array[x, y] != 0:
					count += 1
		if i == 0 or j == 0 or i == n-1 or j == m-1:
			count += 1
		return count
	
	result = game.copy()
	new_result = game.copy()
	for _ in range(5):
		result = new_result.copy()
		for x in range(n):
			for y in range(m):
				if neighbours_count(result, x, y) >= 3:
					new_result[x, y] = 1
				else:
					new_result[x, y] = 0
	return new_result

def generate_forest(game, x, y, empty_forest=False):
	forests = np.zeros((x,y))
	if not empty_forest:
		printf("Generating forests")
		per = perlin_noise((x,y))
		for i in range(x):
			for j in range(y):
				val = per[i, j]
				if game[i][j] in [1, 2]:
					new_value = 0
					if val >= 0.93:
						new_value = 1
					elif 0.63 <= val <= 0.70:
						new_value = 2
					elif 0.30 <= val <= 0.37:
						new_value = 3
					elif 0 <= val <= 0.07:
						new_value = 4

					if rdi(0,5) in [0, 2, 5]:
						forests[i, j] = new_value
	return forests


if __name__ == "__main__":
	"""game, paths, starts, end = generate(200, 200, 2)
	np.savetxt('debug_data/map_now.csv', game, fmt="%d")"""
	generate_forest(50, 50)
