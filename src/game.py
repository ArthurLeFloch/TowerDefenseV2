import json
import sys
import time

from random import randint as rdi
import numpy as np
import contextlib
with contextlib.redirect_stdout(None):
	import pygame
from pygame.locals import *
import pygame.freetype

from buttons import Button, ImageButton
from enemies import Dragon, Enemy, Goblin, Healer, HealZone, KingOfKnights, Knight, Giant
from game_data import Game
from towers import Tower
from timer import Timer
from translation import Translation
from logs import Logs
from game_menu import Menu

def printf(args):
	Logs.print('game', args)

START = time.time()

tr = Translation('EN')
Tower.setup_language(tr)
Menu.setup_language(tr)
Button.setup_language(tr)

# region SCREEN & FONTS SETUP
pygame.init()

if len(sys.argv) >= 3:
	printf("Setup configuration detected")
	WIDTH, HEIGHT = int(sys.argv[1]), int(sys.argv[2])
else:
	printf("No setup configuration, setting up window to fullscreen")
	WIDTH, HEIGHT = 0, 0

if WIDTH + HEIGHT == 0:
	flags = FULLSCREEN | DOUBLEBUF
else:
	flags = DOUBLEBUF
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), flags, 16)
WIDTH, HEIGHT = SCREEN.get_size()

Menu.LIFEMAX = 20
Game.LIFEMAX = 20

FPS = 0
clock = pygame.time.Clock()
pygame.display.set_caption(tr.title)
icon = pygame.image.load('images/others/icon.ico')
pygame.display.set_icon(icon)

game = None
current_menu = "menu"

lifebar_total = Menu.LIFE_WIDTH + 2 * Menu.LIFE_PADDING
right_void = 8
to_right = WIDTH-Menu.SHOP_WIDTH-lifebar_total-right_void
Menu.SHOP_POS = (to_right + right_void, None)

GAME_SCREEN = pygame.Surface((to_right, HEIGHT))

FONT = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", 24)
BOLD = pygame.freetype.Font("fonts/MonoglycerideBold.ttf", 27)
GAMEFONT = pygame.freetype.Font("fonts/MonoglycerideBold.ttf", 19)
GAMEFONT2 = pygame.freetype.Font("fonts/MonoglycerideDemiBold.ttf", 18)

Menu.BOLD = BOLD
Menu.FONT = GAMEFONT
Tower.FONT = GAMEFONT2
Tower.PRICE_FONT = FONT
Button.FONT = GAMEFONT
Button.BOLD_FONT = FONT

WHITE = (255, 255, 255)
# endregion

def get_image(size, place):
	tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
	tmp.set_colorkey(WHITE)
	return tmp

def glow(img):
	surface = pygame.Surface(
		(img.get_width() + 2, img.get_height() + 2), pygame.SRCALPHA)
	mask = pygame.mask.from_surface(img)
	mask_surf = mask.to_surface()
	mask_surf.set_colorkey((0, 0, 0))
	surface.blit(mask_surf, (0, 1))
	surface.blit(mask_surf, (2, 1))
	surface.blit(mask_surf, (1, 0))
	surface.blit(mask_surf, (1, 2))
	surface.blit(img, (1, 1))
	return surface

def is_on_rect(pos, rect):
	# Rect : top left x,y and width, height
	x, y = pos
	b1 = rect[0][0] <= x <= rect[0][0]+rect[1]
	b2 = rect[0][1] <= y <= rect[0][1]+rect[2]
	return b1 and b2

#region game VARIABLES
settings = {'tilesize': 14, 'settings': 0, 'dev': False, 'playing': True,
			'fpsmax': 0, 'wave_enabled': True, 'speed': 1, 'color_theme': 0}
colors = {'background': (10, 14, 18),
		  'settings': (100, 100, 100),
		  'life_ok': (30, 150, 40),
		  'life_dead': (60, 0, 10),
		  'xp_ok': (114, 22, 224),
		  'xp_dead': (55, 30, 100),
		  'critic': (255, 40, 80),
		  'game': [{'center': (18, 22, 27),
					'border': (42, 47, 51),
					'Ocenter': (14, 18, 23),
					'Oborder': (21, 24, 26),
					'path': (10, 20, 50),
					'start': (0, 38, 125),
					'end': (125, 10, 20),
					'Pcenter': (73, 102, 123),
					'Pborder': (50, 70, 80)},
				   {'center': (18, 22, 27),
					'border': (42, 47, 51),
					'Ocenter': (14, 18, 23),
					'Oborder': (21, 24, 26),
					'path': (40, 0, 10),
					'start': (100, 70, 0),
					'end': (20, 20, 60),
					'Pcenter': (106, 152, 163),
					'Pborder': (100, 70, 80)}]}


title_width = int(2*WIDTH/(92*5)) * 92
title_height = int(20.*title_width/92.)
title_pos = (WIDTH/2 - title_width/2, 40)
title = glow(get_image((title_width, title_height), 'images/others/title.png'))

Button("new_map", (WIDTH/2 - 150, HEIGHT/2), (300, 50), tr.new_map, font_type=2)
Button("browse_maps", (WIDTH/2 - 150, HEIGHT/2 + 100), (300, 50), tr.browse_maps, font_type=2) # ? Share maps ?
Button("settings", (WIDTH/2 - 150, HEIGHT/2 + 200), (300, 50), tr.settings, font_type=2)

tile_size = 28
size = int(to_right/tile_size), int(HEIGHT/tile_size)
n, m = size

shop_data = {'item_count': 0, 'items_per_tab': 0,
			 'first_item': 0, 'max_tab': 0}

selected_tower = None
selected_stats = 0
drag_n_dropping = None

zone_selection = None

Tower.setup_tower_shop_images(Menu.SHOP_IMAGE_SIZE)

Game.menu = Menu((Menu.SHOP_POS[0], 0), (WIDTH-Menu.SHOP_POS[0], HEIGHT))
#endregion

#region RIGHT MENU

to_change_speed_height = 10 + 230 + 5

to_shop_height = to_change_speed_height + 42 + 5

shop_height = HEIGHT-to_shop_height-8

time_stamp = time.time()

# endregion

def new_game(width, height, start_count):
	global game, selected_tower
	
	game = Game((width, height), start_count)
	if game.tile_size != tile_size:
		game.set_tile_images(settings['color_theme'], tile_size)
	game.tile_size = tile_size
	game._xoffset = int(.5*(to_right/tile_size - n)*tile_size)
	game._yoffset = int(.5*(HEIGHT/tile_size - m)*tile_size)
	Enemy.setup(game)
	Tower.setup(game)

	remove_info_bubble()
	selected_tower = None
	game.update_left()
	Button.delete('upgrade', 'delete', 'boost1', 'boost2', 'stats', 'bstats')


def show_debug_menu():
	"""
	display settings on SCREEN
	"""
	def display_stats(texts_list, values_list):
		for k in range(len(texts_list)):
			text = texts_list[k] + " : "
			value = str(values_list[k])
			
			rendered_text = GAMEFONT.render(text, colors['settings'])
			text_width = rendered_text[0].get_width()
			rect = (20, 20 + display_stats.offset, *rendered_text[0].get_size())
			new_rects.append(rect)
			SCREEN.blit(rendered_text[0], (rect[0], rect[1]))
			
			rendered_value = GAMEFONT.render(value, WHITE)
			rect = (20 + text_width, 20 + display_stats.offset, *rendered_value[0].get_size())
			new_rects.append(rect)
			SCREEN.blit(rendered_value[0], (rect[0], rect[1]))
			display_stats.offset += 25
			
	def display_keys(texts_list, keys_list):
		for k in range(len(texts_list)):
			text = f" : {texts_list[k]}"
			key = f"[{keys_list[k]}]"
			
			rendered_text = GAMEFONT.render(key, WHITE)
			text_width = rendered_text[0].get_width()
			rect = (20, 20 + display_keys.offset, *rendered_text[0].get_size())
			new_rects.append(rect)
			SCREEN.blit(rendered_text[0], (rect[0], rect[1]))
			
			rendered_key = GAMEFONT.render(text, colors['settings'])
			rect = (20 + text_width, 20 + display_keys.offset, *rendered_key[0].get_size())
			new_rects.append(rect)
			SCREEN.blit(rendered_key[0], (rect[0], rect[1]))
			display_keys.offset += 25
	
	display_stats.offset = 0
	display_keys.offset = 25
	if settings['settings'] > 0:
		display_stats(["fps"], [int(clock.get_fps())])

	if settings['settings'] == 2:
		c = "Max" if FPS == 0 else FPS
		texts = []
		values = []
		
		texts.append("-> fps cap"); values.append(c)
		texts.append("time played"); values.append(int(time.time()-time_stamp))
		texts.append("speed"); values.append(settings["speed"])
		if settings['dev']:
			texts.append("(dev.) dimension"); values.append(game.size)
			texts.append("(dev.) paths lengths"); values.append(game.lengths)
			texts.append("(dev.) wave number"); values.append(game.wave_count)
			texts.append("(dev.) wave enabled"); values.append(settings['wave_enabled'])
			texts.append("(dev.) enemies left"); values.append(game.wave.length)
			texts.append("(dev.) active timers"); values.append(len(Timer.list))
		texts.append("towers count"); values.append(Tower.amount)
		texts.append("enemies count"); values.append(Enemy.amount)
		texts.append("-> corrupted"); values.append(Enemy.corrupted)
		display_stats(texts, values)

	if settings['settings'] == 3:
		texts = []
		keys = []
		
		texts.append("modify fps"); keys.append("f")
		texts.append("modify speed"); keys.append("s")
		texts.append("quit game"); keys.append("ESC")
		texts.append("settings view"); keys.append("LSHIFT / LCTRL")
		texts.append("toggle color theme"); keys.append("t")
		if settings['dev']:
			texts.append("(dev.) toggle mode"); keys.append("d")
			texts.append("(dev.) update graphics"); keys.append("j")
			texts.append("(dev.) save map"); keys.append("m")
			texts.append("(dev.) generate different map"); keys.append("n")
		texts.append("generate new map"); keys.append("SPACE")
		if settings['dev']:
			texts.append("(dev.) fill tiles"); keys.append("e")
			texts.append("(dev.) toggle wave mode"); keys.append("w")
			texts.append("(dev.) next wave"); keys.append("x")
			texts.append("(dev.) add knight"); keys.append("k")
			texts.append("(dev.) add goblin"); keys.append("g")
			texts.append("(dev.) add dragon"); keys.append("v")
			texts.append("(dev.) add king of knights"); keys.append("o")
			texts.append("(dev.) add giant"); keys.append("y")
			texts.append("(dev.) add healer"); keys.append("h")
			texts.append("(dev.) save tower info"); keys.append("i")
			texts.append("(dev.) give coins"); keys.append("c")
			texts.append("(dev.) give extra life"); keys.append("l")
		display_keys(texts, keys)
	
	if settings['dev']:
		rendered_text = FONT.render(tr.dev_mode, WHITE)
		rect = (20, HEIGHT-40, *rendered_text[0].get_size())
		new_rects.append(rect)
		SCREEN.blit(rendered_text[0], (rect[0], rect[1]))

def update_upgrade_menu(pressed, clicked_up):
	global selected_stats, selected_tower
	tower, cls = selected_tower
	Button.update(SCREEN, x, y, pressed, clicked_up)
	
	if tower.is_choosing_boost: # * Pass split level ?
		if Button.confirmed('boost1'):
			tower.chosen_boost = 1
		elif Button.confirmed('boost2'):
			tower.chosen_boost = 2
		if tower.chosen_boost != 0:
			Button.delete('boost1', 'boost2')
			formatted_cost = tr.money_format.format(money=cls.COST[tower.lvl+1])
			text = tr.tower_upgrade.format(cost=formatted_cost)
			is_locked = (game.coins < cls.COST[tower.lvl+1])
			if game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1]:
				is_locked = True
				text = tr.tower_required_level.format(level=cls.ALLOWED_LEVEL[tower.lvl+1])
			Button('upgrade', *Menu.RECT_UPGRADE, text, locked=is_locked)

			Button('delete', *Menu.RECT_DELETE, tr.tower_delete.format(refund=tower.deletion_refund), need_confirmation=True)
			Button('stats', *Menu.RECT_STATS, tr.classic_panel, locked = not selected_stats)
			Button('bstats', *Menu.RECT_BSTATS, tr.boost_panel, locked = selected_stats)

	elif tower.lvl < cls.MAX_LEVEL and Button.clicked('upgrade'): # * Pass level ?
		printf(f"{cls.__name__} upgraded")
		if game.coins >= cls.COST[tower.lvl+1]:
			tower.level_up()
			game.update_left()
			if tower.is_choosing_boost: # * Next level = choose boost
				Button('boost1', *Menu.RECT_BOOST1, tr.boost_select, need_confirmation=True)
				Button('boost2', *Menu.RECT_BOOST2, tr.boost_select, need_confirmation=True)
				Button.delete('upgrade', 'delete', 'stats', 'bstats')
			else: # * Next level = classic upgrade
				if tower.lvl < cls.MAX_LEVEL:
					is_locked = (game.coins < cls.COST[tower.lvl+1] or game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1])
					formatted_cost = tr.money_format.format(money=cls.COST[tower.lvl+1])
					text = tr.tower_upgrade.format(cost=formatted_cost)
					if game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1]:
						is_locked = True
						text = tr.tower_required_level.format(level=cls.ALLOWED_LEVEL[tower.lvl+1])
					Button.dict['upgrade'].set_text(text)
					Button.set_lock('upgrade', is_locked)
				else:
					Button.delete('upgrade')
				formatted_cost = tr.money_format.format(money=tower.deletion_refund)
				Button.dict['delete'].set_text(tr.tower_delete.format(refund=formatted_cost))
			add_coins(-cls.COST[tower.lvl])

	elif Button.confirmed('delete'):
		printf(f"{cls.__name__} deleted")
		success = game.set_tile(1, *tower.pos[0], width=cls.SIZE)
		if success:
			game.update_left()
		add_coins(tower.deletion_refund)
		Tower.remove(*tower.pos[0])
		selected_tower = None
		Button.delete('upgrade', 'delete', 'stats', 'bstats')

	elif Button.clicked('stats'):
		printf("Switched view to classic stats")
		Button.lock('stats')
		if tower.chosen_boost:
			Button.unlock('bstats')
		selected_stats = 0
	
	elif Button.clicked('bstats'):
		printf("Switched view to boost stats")
		Button.unlock('stats')
		Button.lock('bstats')
		selected_stats = 1

def setup_upgrade_buttons(selected_tower):
	tower, cls = selected_tower
	global selected_stats
	selected_stats = 0
	Button.delete('upgrade', 'delete', 'boost1', 'boost2', 'stats', 'bstats')
	if tower.is_choosing_boost:
		Button('boost1', *Menu.RECT_BOOST1, tr.boost_select, need_confirmation=True)
		Button('boost2', *Menu.RECT_BOOST2, tr.boost_select, need_confirmation=True)
	else:
		Button('stats', *Menu.RECT_STATS, tr.classic_panel, locked = True)
		Button('bstats', *Menu.RECT_BSTATS, tr.boost_panel, locked = (tower.chosen_boost == 0))

		if tower.lvl < cls.MAX_LEVEL:
			is_locked = (game.coins < cls.COST[tower.lvl+1] or game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1])
			formatted_cost = tr.money_format.format(money=cls.COST[tower.lvl+1])
			text = tr.tower_upgrade.format(cost=formatted_cost)
			if game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1]:
				text = tr.tower_required_level.format(level=cls.ALLOWED_LEVEL[tower.lvl+1])
			Button('upgrade', *Menu.RECT_UPGRADE, text, locked=is_locked)
		
		formatted_cost = tr.money_format.format(money=tower.deletion_refund)
		Button('delete', *Menu.RECT_DELETE, tr.tower_delete.format(refund=formatted_cost), need_confirmation=True)

def show_selected_tower(xi, yi, pressed, clicked_up):
	tower, cls = selected_tower

	if tower.is_choosing_boost:
		game.menu.update_description_boosts(SCREEN, cls.shop_image, cls.desc_boost1, cls.desc_boost2)
	else:
		if Button.exists('upgrade') and game.lvl.level >= cls.ALLOWED_LEVEL[tower.lvl+1]:
			formatted_cost = tr.money_format.format(money=cls.COST[tower.lvl+1])
			text = tr.tower_upgrade.format(cost=formatted_cost)
			Button.dict['upgrade'].set_text(text)
			is_locked = (cls.COST[tower.lvl + 1] > game.coins)
			Button.set_lock('upgrade', is_locked)

		hovered = Button.ex_and_hovered('upgrade')
		is_boost_preview = (tower.lvl == cls.SPLIT_LEVEL-1 and hovered)
		can_afford = (tower.lvl == cls.MAX_LEVEL or (cls.COST[tower.lvl + 1] <= game.coins and game.lvl.level >= cls.ALLOWED_LEVEL[tower.lvl+1]))
		desc = tower.description_texts(hovered, selected_stats)
		game.menu.update_upgrade_texts(SCREEN, cls.shop_image, desc, can_afford, is_boost_preview)
		
	Button.update(SCREEN, xi, yi, pressed, clicked_up)

def nav_game_to_menu():
	global current_menu
	current_menu = "menu"
	settings['playing'] = True
	ImageButton.delete_all()
	Button.delete_all()
	Button("new_map", (WIDTH/2 - 150, HEIGHT/2), (300, 50), tr.new_map, font_type=2)
	Button("browse_maps", (WIDTH/2 - 150, HEIGHT/2 + 100), (300, 50), tr.browse_maps, font_type=2)
	Button("settings", (WIDTH/2 - 150, HEIGHT/2 + 200), (300, 50), tr.settings, font_type=2)

def nav_menu_to_game():
	global current_menu
	current_menu = "game"

	ImageButton('speed_up', "images/others/speed_up.png", *Menu.RECT_SPEED_UP)
	ImageButton('speed_down', "images/others/speed_down.png", *Menu.RECT_SPEED_DOWN)
	ImageButton('play_pause', "images/others/pause.ppm", *Menu.RECT_WAVE_PAUSE)

	ImageButton.unlock('speed_up')
	ImageButton.unlock('speed_down')
	if settings['speed'] == 1:
		ImageButton.lock('speed_down')
	if settings['speed'] == 5:
		ImageButton.lock('speed_up')
	Button.delete("new_map", "browse_maps", "settings")

def add_coins(value):
	game.add_coins(value)
	if selected_tower and Button.exists('upgrade'):
		tower, cls = selected_tower
		is_locked = (game.coins < cls.COST[tower.lvl+1] or game.lvl.level < cls.ALLOWED_LEVEL[tower.lvl+1])
		Button.set_lock('upgrade', is_locked)

def change_speed(speed):
	if speed != settings['speed']:
		printf(f"Changed speed to {speed}")
	settings['speed'] = speed
	ImageButton.unlock('speed_up')
	ImageButton.unlock('speed_down')
	if settings['speed'] == 1:
		ImageButton.lock('speed_down')
	if settings['speed'] == 5:
		ImageButton.lock('speed_up')
	game.set_speed(settings['speed'])

def setup_info_bubble(text, value, pos):
	global info_bubble, info_rect
	
	rendered_text = GAMEFONT.render(text, WHITE)
	text_width = rendered_text[0].get_width()
	text_height = rendered_text[0].get_height()

	rendered_value = GAMEFONT.render(tr.money_format.format(money=value), colors['life_ok'])
	rendered_value2 = GAMEFONT.render(tr.money_format.format(money=value), colors['critic'])
	value_width = rendered_value[0].get_width()
	value_height = rendered_value[0].get_height()

	width = text_width + value_width
	tot_width = 120 + width
	image = pygame.Surface((tot_width, 60), pygame.SRCALPHA)
	
	pygame.draw.rect(image, (0, 0, 0), (0, 0, tot_width, 60), border_radius=10)
	pygame.draw.rect(image, (15, 21, 27), (4, 4, tot_width-8, 60-8), border_radius=10)

	image.blit(rendered_text[0], (60, 30-text_height/2))
	
	new_x = pos[0] - tot_width/2
	if pos[0] - tot_width/2 < 0:
		new_x = 20
	elif pos[0] + tot_width/2 > to_right:
		new_x = to_right - tot_width - 20

	new_y = pos[1] - 60 - tile_size
	if new_y < 0:
		new_y = pos[1] + game._yoffset + tile_size

	pos = (new_x, new_y)

	image2 = image.copy()
	image.blit(rendered_value[0], (60+text_width, 30-value_height/2))
	image2.blit(rendered_value2[0], (60+text_width, 30-value_height/2))
	info_bubble = ((image, image2), pos)

	info_rect = (pos, *image.get_size())

def remove_info_bubble():
	global info_rect, info_bubble
	info_bubble = None
	info_rect = None

	game.selection_type = None
	game.selected_tiles = []
	game.update_left()

	ImageButton.delete('confirm', 'cancel')

info_bubble = None
info_rect = None

last_rects, new_rects = [], []

printf('Initialization time : ' + str(time.time()-START))

prev_xc, prev_yc = 0, 0

execute = True
was_possible = None

current_click_state = False
last_click_state = False
clicked_up = False

while execute:
	SCREEN.fill(colors['background'])

	eventL = pygame.event.get()
	listev = eventL.copy()
	
	x, y = pygame.mouse.get_pos()

	pressed_keys = pygame.key.get_pressed()
	pressed_mouse_keys = pygame.mouse.get_pressed()
	current_click_state = pressed_mouse_keys[0]
	if not current_click_state and last_click_state:
		clicked_up = True
	else:
		clicked_up = False
		
	if current_menu == "menu":
		SCREEN.blit(title, title_pos)
		
		if Button.clicked('new_map'):
			SCREEN.fill(colors['background'])
			pygame.display.update()
			new_game(n, m, rdi(1,3))
			nav_menu_to_game()
		elif Button.clicked('browse_maps'):
			pass
		elif Button.clicked('settings'):
			pass
		
		for event in listev:
			if event.type == QUIT:
				execute = False
			
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					execute = False
					
		Button.update(SCREEN, x, y, current_click_state, clicked_up)
		
	elif current_menu == "game":
		xc, yc = int((x-game._xoffset)/tile_size), int((y-game._yoffset)/tile_size)		

		if settings['wave_enabled'] and settings['playing']:
			game.update_enemy_spawn()
		
		if not (drag_n_dropping or info_bubble):
			game.update_selection(xc, yc, pressed=pressed_mouse_keys[0])

		for event in listev:
			if event.type == QUIT:
				execute = False

			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if x < to_right:
						if info_bubble and not is_on_rect((x, y), info_rect):
							remove_info_bubble()
						elif not info_bubble:
							game.init_selection(xc, yc)
						selected_tower = Tower.get(xc, yc)
						if selected_tower:
							printf("Selected tower")
							remove_info_bubble()
							setup_upgrade_buttons(selected_tower)
					elif x > Menu.SHOP_POS[0]:
						remove_info_bubble()
						if not selected_tower:
							if drag_n_dropping:
								drag_n_dropping = None
								game.potential_path = []
								game.update_left()
							else:
								drag_n_dropping = game.menu.shop_select_tower(x, y)
								if drag_n_dropping:
									remove_info_bubble()
									printf("Start dragging tower")
				elif event.button == 4:
					if x > Menu.SHOP_POS[0]:
						game.menu.shop_navigate(-1)
				elif event.button == 5:
					if x > Menu.SHOP_POS[0]:
						game.menu.shop_navigate(+1)
			if event.type == MOUSEBUTTONUP:
				if event.button == 1:
					if game.selected_tiles != [] and not info_bubble:
						text = tr.unlock_for
						cost = game.selection_tile_cost()
						if game.selection_type == 'tree':
							text = tr.delete_for
							cost = game.selection_tree_cost()
						nx, ny = game.selected_tiles[-1]
						info_x = nx*tile_size + game._xoffset + tile_size / 2
						info_y = ny*tile_size + game._yoffset + tile_size / 2
						setup_info_bubble(text, cost, (info_x, info_y))
					elif drag_n_dropping:
						if x < to_right:
							valid_placement = game.try_place(drag_n_dropping, xc, yc)
							if valid_placement:
								game.potential_path = []
								game.update_left()
								add_coins(-drag_n_dropping.COST[0])
						drag_n_dropping = None
						remove_info_bubble()
					elif selected_tower:
						update_upgrade_menu(current_click_state, clicked_up)
						remove_info_bubble()

			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					nav_game_to_menu()
				
				if event.key == K_LSHIFT:
					settings['settings'] = (settings['settings'] + 1)%4

				if event.key == K_LCTRL:
					if pressed_keys[K_s]:
						printf("Saving map")
						game.save()
					else:
						settings['settings'] = (settings['settings'] - 1)%4

				if event.key == K_d:
					settings['dev'] = not settings['dev']
					if settings['dev']:
						printf("Switched to DEV. mode")
					else:
						printf("Switched back to user mode")

				if event.key == K_SPACE:
					new_game(n, m, start_count = rdi(1, 3))

				if event.key == K_n and settings['dev']:
					tile_size = rdi(8, 40)
					game.set_tile_images(settings['color_theme'], tile_size)
					n, m = int(to_right/tile_size), int(HEIGHT/tile_size)
					size = n, m

					new_game(n, m, start_count = rdi(1, 3))

				if event.key == K_z and settings['dev']:
					game.gain_xp(999999)

				if event.key == K_o and settings['dev']:
					KingOfKnights()

				if event.key == K_k and settings['dev']:
					Knight()

				if event.key == K_g and settings['dev']:
					Goblin()

				if event.key == K_v and settings['dev']:
					Dragon()

				if event.key == K_h and settings['dev']:
					Healer()
				
				if event.key == K_y and settings['dev']:
					Giant()

				if event.key == K_i and settings['dev']:
					printf("Saving selected tower data")
					if selected_tower:
						with open("debug_data/tower_data.json", 'w') as f:
							jsonStr = json.dumps(selected_tower[0].__dict__, indent=4)
							f.write(jsonStr)
						printf("Generated data file")

				if event.key == K_x and settings['dev']:
					game.new_wave()

				if event.key == K_t:
					settings['color_theme'] = 1 - settings['color_theme']
					printf("Changing color theme")
					game.set_tile_images(settings['color_theme'], tile_size)
					game.update_left()

				if event.key == K_w and settings['dev']:
					settings['wave_enabled'] = not settings['wave_enabled']

				if event.key == K_c and settings['dev']:
					printf("Added coins")
					add_coins(500000)
				
				if event.key == K_l and settings['dev']:
					game.get_damage(-1)

				if event.key == K_f:
					printf(f"FPS cap toggled from {FPS if FPS != 0 else 'MAX'} to {FPS+30 if FPS+30<=300 else 'MAX'}")
					FPS += 30
					if FPS > 300:
						FPS = 0

				if event.key == K_m and settings['dev']:
					np.savetxt('debug_data/starting_map.csv', game.array.transpose(), fmt="%d")

				if event.key == K_j and settings['dev']:
					game.update_left()
					game.set_tile_images(settings['color_theme'], tile_size)

				if event.key == K_e and settings['dev']:
					printf("Filling tiles")
					game.fill_all()
					game.update_left()

		# ? Change GAME_SCREEN image to correspond with new array (instead of updating everything every frame)
		show_range = (drag_n_dropping == None and game.selected_tiles == [])
		selected = (selected_tower[0].pos[0] if selected_tower else None)
		game.update_screen(SCREEN, GAME_SCREEN, (xc, yc), show_range, selected, settings['playing'])

		Enemy.update(SCREEN, game.wave, settings['playing'])
		game.menu.update(SCREEN)

		if selected_tower:
			show_selected_tower(x, y, current_click_state, clicked_up)
		else:
			game.menu.update_shop(SCREEN)

		if drag_n_dropping:
			cls = drag_n_dropping
			if xc != prev_xc or yc != prev_yc:
				new_path = game.is_placement_valid(cls, xc, yc)
				was_possible = (new_path != None)
				if was_possible:
					potential_path = []
					for path in new_path:
						potential_path += path
				else:
					potential_path = []
				game.potential_path = potential_path
				game.update_left()
			if was_possible or (xc + cls.SIZE <= n and yc + cls.SIZE <= m and xc >= 0 and yc >= 0):
				Tower.display_possible_place(SCREEN, xc, yc, cls, was_possible)
			new_rects.append((x, y, *cls.image.get_size()))
			SCREEN.blit(cls.image, (x, y))
		else:
			was_possible = None
			game.potential_path = []

		show_debug_menu()

		if game.selected_tiles and info_bubble and current_menu == 'game':
			cost = 0
			images, pos = info_bubble

			if game.selection_type == 'tree':
				cost = game.selection_tree_cost()
			elif game.selection_type == 'tile':
				cost = game.selection_tile_cost()
			new_rects.append((*pos, *images[game.coins < cost].get_size()))
			SCREEN.blit(images[game.coins < cost], pos)

			if not ImageButton.exists('confirm'):
				info_x, info_y = info_bubble[1]
				ImageButton('confirm', 'images/others/confirm.png', (info_x + 10, info_y + 10), size=(40, 40))
				ImageButton('cancel', 'images/others/delete.png', (info_x + info_bubble[0][0].get_width() - 50, info_y + 10), size=(40, 40))
			
			if ImageButton.ex_and_clicked('cancel'):
				remove_info_bubble()
			
			if ImageButton.exists('confirm'):
				ImageButton.set_lock('confirm', (game.coins < cost))
			
			if ImageButton.ex_and_clicked('confirm'):
				if game.selection_type == 'tree':
					cost = game.selection_tree_cost()
					if cost <= game.coins:
						game.delete_selected_trees()
						add_coins(-cost)
				elif game.selection_type == 'tile':
					cost = game.selection_tile_cost()
					if cost <= game.coins:
						game.add_selected_tiles()
						add_coins(-cost)
				remove_info_bubble()

		if Enemy.last_earned != 0:
			add_coins(Enemy.last_earned)
		
		game.gain_xp(Enemy.last_killed)

		if Enemy.last_lost_life != 0:
			game.get_damage(Enemy.last_lost_life)

		Enemy.last_earned = 0
		Enemy.last_killed = 0
		Enemy.last_lost_life = 0

		if ImageButton.ex_and_clicked('speed_up'):
			if settings['speed'] < 5:
				change_speed(settings['speed']+1)
			if settings["speed"] == 5:
				ImageButton.lock('speed_up')
			ImageButton.unlock('speed_down')
		
		if ImageButton.ex_and_clicked('speed_down'):
			if settings['speed'] > 1:
				change_speed(settings['speed']-1)
			if settings["speed"] == 1:
				ImageButton.lock('speed_down')
			ImageButton.unlock('speed_up')
		
		if ImageButton.ex_and_clicked('play_pause'):
			settings['playing'] = not settings['playing']
			if settings['playing']:
				Timer.resume()
				ImageButton.set_button_image('play_pause', "images/others/pause.ppm")
			else:
				Timer.pause()
				ImageButton.set_button_image('play_pause', "images/others/play.ppm")

		prev_xc, prev_yc = xc, yc

		game.update_level()

		ImageButton.update(SCREEN, x, y, current_click_state, clicked_up)

		if game.need_tile_update:
			pygame.display.update()
		else:
			new_rects.append((*game.menu.pos, *game.menu.size))
			list = last_rects + new_rects
			list += Button.last_rects + Button.new_rects
			list += ImageButton.last_rects + ImageButton.new_rects
			list += Enemy.last_rects + Enemy.new_rects
			list += Tower.last_rects + Tower.new_rects
			pygame.display.update(list)

			last_rects = new_rects.copy()
			new_rects = []

	last_click_state = current_click_state
	if current_menu != 'game':
		pygame.display.update()
	clock.tick(FPS)

pygame.quit()
sys.exit()
