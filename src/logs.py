class Logs:
	GREY	= '\33[1;90m'
	RED	 = '\33[1;91m'
	GREEN   = '\33[1;92m'
	YELLOW  = '\33[1;93m'
	BLUE	= '\33[1;94m'
	VIOLET  = '\33[1;95m'
	BEIGE   = '\33[1;96m'
	WHITE   = '\33[1;97m'

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
			case "game_tools":
				return Logs.GREY
			case "game_menu":
				return Logs.GREEN
			case _:
				return Logs.WHITE
	
	def print(name, *args):
		color = Logs.get_color(name)
		print(f"{color}[{name}.py]{Logs.END}", end="")
		print("\r\t\t-> ", end="")
		for arg in args:
			print(arg, end="")
		print()
		