class Logs:
	GREY	= '\33[90m'
	RED	 = '\33[91m'
	GREEN   = '\33[92m'
	YELLOW  = '\33[93m'
	BLUE	= '\33[94m'
	VIOLET  = '\33[95m'
	BEIGE   = '\33[96m'
	WHITE   = '\33[97m'

	END	 = '\33[0m'

	def get_color(name):
		match name:
			case "game":
				return Logs.RED
			case "game_data":
				return Logs.VIOLET
			case "enemies":
				return Logs.YELLOW
			case "towers":
				return Logs.BLUE
			case "waves":
				return Logs.BEIGE
			case "setup_game_tools":
				return Logs.GREY
			case "game_menu":
				return Logs.GREEN
			case _:
				return Logs.WHITE
	
	def print(name, *args):
		color = Logs.get_color(name)
		print(f"{color}[{name}.py]{Logs.END} \t", end="")
		for arg in args:
			print(arg, end="")
		print()
		