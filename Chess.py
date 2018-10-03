import pygame

# os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

game_exit = False

mouse_1 = False
mouse_1_states = []  # Tracks what state mouse_1 was in in the previous loop
should_promote = False
promotion_states = []  # Tracks which frame a pawn was placed in the last file
cell_gap_y = 40
cell_gap_x = cell_gap_y

sqrs_in_line = 8  # How many squares in a row or column

# Colours

off_white = (230, 230, 230)
white = (255, 255, 255)
black = (0, 0, 0)
grey = (60, 60, 60)
light_grey = (135, 135, 135)
red = (245, 0, 0)
green = (0, 215, 0)
blue = (0, 0, 245)
purple = (150, 0, 175)
pink = (245, 105, 180)
turquoise = (0, 206, 209)
ochre = (204, 119, 34)
brown = (155, 83, 19)
light_brown = (255, 218, 185)

display_width = 800
display_height = 600
resolution = (display_width, display_height)

Display = pygame.display.set_mode(resolution)

pygame.display.set_caption('Chess')

clock = pygame.time.Clock()

# Fonts
small_font_size = display_width // 25
med_font_size = display_width // 12
large_font_size = display_width // 5

small_font = pygame.font.SysFont('Roboto', small_font_size)
med_font = pygame.font.SysFont('Roboto', med_font_size)
large_font = pygame.font.SysFont('Roboto', large_font_size)

# Images
img_width = 68
mini_img_width = 51

white_dict = {'King': pygame.image.load('white king.png'),
              'Queen': pygame.image.load('white queen.png'),
              'Rook': pygame.image.load('white rook.png'),
              'Bishop': pygame.image.load('white bishop.png'),
              'Knight': pygame.image.load('white knight.png'),
              'Pawn': pygame.image.load('white pawn.png')}

black_dict = {'King': pygame.image.load('black king.png'),
              'Queen': pygame.image.load('black queen.png'),
              'Rook': pygame.image.load('black rook.png'),
              'Bishop': pygame.image.load('black bishop.png'),
              'Knight': pygame.image.load('black knight.png'),
              'Pawn': pygame.image.load('black pawn.png')}

white_pawn_mini_img = pygame.image.load('white pawn mini.png')
white_queen_mini_img = pygame.image.load('white queen mini.png')
white_rook_mini_img = pygame.image.load('white rook mini.png')
white_bishop_mini_img = pygame.image.load('white bishop mini.png')
white_knight_mini_img = pygame.image.load('white knight mini.png')

black_pawn_mini_img = pygame.image.load('black pawn mini.png')
black_queen_mini_img = pygame.image.load('black queen mini.png')
black_rook_mini_img = pygame.image.load('black rook mini.png')
black_bishop_mini_img = pygame.image.load('black bishop mini.png')
black_knight_mini_img = pygame.image.load('black knight mini.png')


loc_squares = {}
hover_loc = None
clicked_piece = None
clicked_cell = None

available_movement_wait = False  # This is to make the function available_movement wait a frame before activating


class Cell:
	def __init__(self,
	             colour=black,
	             top_left=((display_width / 4) + 15, 15),
	             width_height=(3 * display_width / 100, 3 * display_height / 100),
	             thickness=1,
	             highlight=False,
	             highlight_thickness=3):
		self.colour = colour
		self._x1 = top_left[0]
		self._y1 = top_left[1]
		self.width = width_height[0]
		self.height = width_height[1]
		self.x2 = self._x1 + self.width
		self.y2 = self._y1 + self.height
		self.thickness = thickness
		self.highlight = highlight
		self.was_highlighted = False  # Keeps track of the last highlighted cell
		self.high_thick = highlight_thickness
		self.available = False
		self.loc = None

	@property
	def x1(self):
		return self._x1

	@property
	def y1(self):
		return self._y1

	@x1.setter
	def x1(self, value):
		self._x1 = value
		self.x2 = value + self.width

	@y1.setter
	def y1(self, value):
		self._y1 = value
		self.y2 = value + self.height

	def draw_to_screen(self):
		if not self.highlight:
			Display.fill(black, rect=[self.x1,
			                          self.y1,
			                          self.width,
			                          self.height])

			Display.fill(self.colour, rect=[self.x1 + self.thickness,
			                                self.y1 + self.thickness,
			                                self.width - 2 * self.thickness,
			                                self.height - 2 * self.thickness])
		if self.highlight:
			Display.fill(green, rect=[self.x1,
			                          self.y1,
			                          self.width,
			                          self.height])

			Display.fill(self.colour, rect=[self.x1 + self.high_thick,
			                                self.y1 + self.high_thick,
			                                self.width - 2 * self.high_thick,
			                                self.height - 2 * self.high_thick])

		if self.available:

			a = self.width / 2.5

			Display.fill(blue, rect=[self.x1 + a,
			                         self.y1 + a,
			                         self.width - 2 * a,
			                         self.height - 2 * a])

	def __repr__(self):
		# return '(' + '(' + str(int(self.x1)) + ',' + str(int(self.y1)) + ')' + ','\
		#        + '(' + str(int(self.x2)) + ',' + str(int(self.y2)) + ')' + ')'
		return self.loc + '(' + str(int(self.x1 + self.width / 2)) + \
		       ',' + str(int(self.y1 + self.height / 2)) + ')'


class Piece:
	def __init__(self,
	             colour,
	             rank,
	             file_id,
	             center=(0, 0)):
		self.colour = colour
		if colour.lower() == 'black':
			self.rank = black_dict[rank]
		else:
			self.rank = white_dict[rank]
		self.rank_name = rank
		self.x = center[0]
		self.y = center[1]
		self.file_id = file_id

		name = self.rank_name
		file = ''
		if name.lower() == 'pawn':
			if file_id == 0:
				file = 'a'
			elif file_id == 1:
				file = 'b'
			elif file_id == 2:
				file = 'c'
			elif file_id == 3:
				file = 'd'
			elif file_id == 4:
				file = 'e'
			elif file_id == 5:
				file = 'f'
			elif file_id == 6:
				file = 'g'
			else:
				file = 'h'
		if name.lower() == 'bishop':
			if file_id == 0:
				file = 'c'
			else:
				file = 'f'
		if name.lower() == 'knight':
			name = 'night'
			if file_id == 0:
				file = 'b'
			else:
				file = 'g'
		if name.lower() == 'rook':
			if file_id == 0:
				file = 'a'
			else:
				file = 'h'
		if name.lower() == 'queen':
			file = ''
		if name.lower() == 'king':
			file = ''

		self.name = colour.lower()[0] + name[0].lower() + file

		self.file = file

		self.promoted_name = self.name

		self._loc = None  # Explained in def loc(self)

	@property
	# Initializing a location attribute that will be the piece's location
	# eg e4 or d6
	def loc(self):
		# _loc is assigned later so that when calling loc, you get
		# the location of the piece
		return self._loc

	@loc.setter
	def loc(self, dict_loc):
		"""

		:param dict_loc: tuple of the dictionary of the locations and
						the location to be used
		:return:
		"""
		# Top Left Corner (I think)
		self.x = dict_loc[0][dict_loc[1]][0]
		self.y = dict_loc[0][dict_loc[1]][1]
		self._loc = dict_loc[1]

	def promotion(self, name):
		if self.colour.lower() == 'black':
			self.rank = black_dict[name]
		else:
			self.rank = white_dict[name]

		file = self.file

		if name.lower() == 'knight':
			name = 'night'
		if name.lower() == 'queen':
			file = ''
		if name.lower() == 'king':
			file = ''

		self.promoted_name = self.colour.lower()[0] + name[0].lower() + file

	def demotion(self):
		if self.colour.lower() == 'black':
			self.rank = black_dict[self.rank_name]
		else:
			self.rank = white_dict[self.rank_name]

		self.promoted_name = self.name


	def draw(self):
		Display.blit(self.rank,
		             (self.x - img_width / 2,
		              self.y - img_width / 2))

	def follow(self):
		"""move the piece based on the mouse position"""
		pos = pygame.mouse.get_pos()
		self.x = pos[0]
		self.y = pos[1]
		self.draw()

	def __repr__(self):
		return self.colour + '_' + self.rank_name


class Mini:
	def __init__(self, colour, rank, img, order):
		self.colour = colour
		self.rank = rank
		self.img = img
		self.order = order - 1
		self.x = mini_img_width / 64 + self.order * mini_img_width
		self.y = display_height / 2 - mini_img_width / 2

	def draw(self):
		Display.blit(self.img, (self.x, self.y))


def board_coords(coords, just_coords=False):
	"""

	:param coords: List of centre coordinates of each square
	:param just_coords: whether to return just the coordinates or not
	:return: if just_coords: a dictionary with the centre coordinate attributed to its label on the board
			 if not just_coords: a list of every label on the board
	"""
	coord_list = []
	index_count = 0
	board_dict = {}
	for i in range(sqrs_in_line):
		non_str_num = i + 1
		num = str(non_str_num)
		letter_val = 97

		for v in range(sqrs_in_line):
			letter = chr(letter_val)
			key = letter + num

			coord_list.append(key)
			if not just_coords:
				board_dict[key] = coords[index_count]

			letter_val += 1
			index_count += 1

	board_dict['black king graveyard'] = (display_width / 8, img_width / 2)
	board_dict['black queen graveyard'] = (display_width / 8, (img_width / 4) + img_width)

	board_dict['black pawn graveyard'] = (img_width / 2, (img_width / 4) + 2 * img_width)
	board_dict['black rook graveyard'] = (display_width / 8 + img_width / 2, (img_width / 4) + 2 * img_width)

	board_dict['black bishop graveyard'] = (img_width / 2, (img_width / 4) + 3 * img_width)
	board_dict['black knight graveyard'] = (display_width / 8 + img_width / 2, (img_width / 4) + 3 * img_width)

	board_dict['white king graveyard'] = (display_width / 8, (display_height / 2) + img_width / 2)
	board_dict['white queen graveyard'] = (display_width / 8, (display_height / 2) + (img_width / 4) + img_width)

	board_dict['white pawn graveyard'] = (img_width / 2, (display_height / 2) + (img_width / 4) + 2 * img_width)
	board_dict['white rook graveyard'] = (display_width / 8 + img_width / 2,
	                                      (display_height / 2) + (img_width / 4) + 2 * img_width)

	board_dict['white bishop graveyard'] = (img_width / 2, (display_height / 2) + (img_width / 4) + 3 * img_width)
	board_dict['white knight graveyard'] = (display_width / 8 + img_width / 2,
	                                        (display_height / 2) + (img_width / 4) + 3 * img_width)

	board_dict['off screen'] = (display_width + img_width, display_height + img_width)

	if just_coords:
		return coord_list
	else:
		return board_dict


def just_board_coords():
	coord_list = []
	for i in range(sqrs_in_line):
		non_str_num = sqrs_in_line - i
		num = str(non_str_num)
		letter_val = 97

		for v in range(sqrs_in_line):
			letter = chr(letter_val)
			ans = letter + num

			coord_list.append(ans)
			letter_val += 1
	return coord_list


def generate_pieces(locations):
	for loc_key in locations:

		for piece in pieces_list:
			if loc_key == piece_loc[piece.name]:
				piece.loc = [locations, loc_key]
				piece.draw()


def generate_board():
	# Gap between edge of screen and the board:
	global cell_gap_y
	global cell_gap_x

	# Keeps track of which colour from colour list to use:
	colour_count = 0

	flip = False  # When generating the colour for the board, it flips the logic every row

	corner_rows = []
	corner_columns = []
	square_coords = []
	square_list = []

	total_width = (3 * display_width / 4) - (2 * cell_gap_x)
	total_height = display_height - (2 * cell_gap_y)  # This was display_width. Maybe change it back later

	square_width = total_width / sqrs_in_line
	square_height = total_height / sqrs_in_line

	counter = 0

	loc_list = board_coords(None, True)

	if square_width > square_height:
		cell_gap_x += (square_width - square_height)
		square_width = square_height
	else:
		cell_gap_y += (square_height - square_width)
		square_height = square_width
	for square_column in range(sqrs_in_line):
		corner_columns.append(square_column * square_height + cell_gap_y)
		for square_row in range(sqrs_in_line):
			x1 = square_row * square_width + cell_gap_x + display_width / 4
			corner_rows.append(x1)
			y1 = square_column * square_height + cell_gap_y
			square = cells[counter]
			square.x1 = x1
			square.y1 = y1
			square.width = square_width
			square.height = square_height
			square.loc = loc_list[counter]

			if colour_count % 2 == 1:
				if flip:
					colour = light_brown
				else:
					colour = brown
			else:
				if flip:
					colour = brown
				else:
					colour = light_brown

			square.colour = colour
			square_list.append(square)
			colour_count += 1
			if not colour_count % 8:
				flip = not flip

			centre_coordinate = [x1 + square_width / 2, y1 + square_height / 2]

			square_coords.append(centre_coordinate)

			counter += 1

	for square_index in range(len(square_list)):
		square_list[square_index].draw_to_screen()
	letter_ascii = 97
	for x in range(sqrs_in_line):
		letter = chr(letter_ascii)
		message_to_screen(letter,
		                  white,
		                  y_displace=cell_gap_y,
		                  x_displace=corner_rows[x] + square_width / 2,
		                  side='custom_bottom')
		message_to_screen(letter,
		                  white,
		                  y_displace=display_height - cell_gap_y,
		                  x_displace=corner_rows[x] + square_width / 2,
		                  side='custom_top')
		letter_ascii += 1
	num = 8
	for y in range(sqrs_in_line):
		message_to_screen(str(num),
		                  white,
		                  y_displace=corner_columns[y] + square_height / 2,
		                  x_displace=cell_gap_x + display_width / 4 - 5,
		                  side='custom_mid_right')
		message_to_screen(str(num),
		                  white,
		                  y_displace=corner_columns[y] + square_height / 2,
		                  x_displace=display_width - cell_gap_x + 5,
		                  side='custom_mid_left')
		num -= 1

	board_loc = board_coords(square_coords)

	generate_pieces(board_loc)

	return board_loc, square_list


def text_object(text, colour, size):
	if size == 'small':
		text_surface = small_font.render(text, True, colour)
	elif size == 'medium':
		text_surface = med_font.render(text, True, colour)
	else:
		text_surface = large_font.render(text, True, colour)
	return text_surface, text_surface.get_rect()


def message_to_screen(msg,
                      colour,
                      y_displace=0,
                      x_displace=0,
                      size='small',
                      side='center'):
	"""
	Each 'side' differs in their starting positions,
	point of the text box being controlled and
	in the direction of the displacements

	The name od the 'side' indicates the starting position as well as
	the point of the text box being controlled

	Center: Pygame directions
	Top: Pygame directions
	Bottom Left: Negative y
	Bottom Right: Negative y and Negative x
	:param msg:
	:param colour:
	:param y_displace:
	:param x_displace:
	:param size:
	:param side:
	:return:
	"""
	text_surf, text_rect = text_object(msg, colour, size)
	if side == 'center':
		text_rect.center = (display_width / 2) + x_displace, \
		                   (display_height / 2) + y_displace
	elif side == 'top':
		text_rect.midtop = (display_width / 2) + x_displace, y_displace
	elif side == 'bottom_left':
		text_rect.bottomleft = (x_displace,
		                        display_height - y_displace)
	elif side == 'bottom_right':
		text_rect.bottomright = (display_width - x_displace,
		                         display_height - y_displace)
	elif side == 'custom_center':
		text_rect.center = x_displace, y_displace
	elif side == 'custom_top':
		text_rect.midtop = x_displace, y_displace
	elif side == 'custom_bottom':
		text_rect.midbottom = x_displace, y_displace
	elif side == 'custom_bot_left':
		text_rect.bottomleft = x_displace, y_displace
	elif side == 'custom_bot_right':
		text_rect.bottomright = x_displace, y_displace
	elif side == 'custom_mid_right':
		text_rect.midright = x_displace, y_displace
	elif side == 'custom_mid_left':
		text_rect.midleft = x_displace, y_displace
	else:
		text_rect.center = (display_width / 2) + x_displace, \
		                   (display_height / 2) + y_displace
	Display.blit(text_surf, text_rect)


def check_hover_cell(square_list):
	pos = pygame.mouse.get_pos()
	for obj in square_list:
		if obj.x1 <= pos[0] < obj.x2 and obj.y1 <= pos[1] < obj.y2:
			return obj
	return None


def check_hover_piece():
	pos = pygame.mouse.get_pos()
	for obj in pieces_list:  # pieces_list is a list of all the piece class objects
		if obj.x - img_width / 2 <= pos[0] < obj.x + img_width / 2 and \
										obj.y - img_width / 2 <= pos[1] < obj.y + img_width / 2:
			return obj
	return None


def check_hover_mini(colour, promotion=True):
	pos = pygame.mouse.get_pos()
	for obj in mini_list:  # mini_list is a list of all the mini class objects
		if obj.x <= pos[0] < obj.x + mini_img_width and obj.y <= pos[1] < obj.y + mini_img_width and obj.colour == colour:
			if obj.rank != 'Pawn':
				if promotion:
					return obj
			elif obj.rank == 'Pawn':
				if not promotion:
					return obj
	return None


def mouse_on_cell(last_pos):
	mouse_pos = pygame.mouse.get_pos()
	for square in cells:
		if square.x1 < mouse_pos[0] < square.x2 and \
								square.y1 < mouse_pos[1] < square.y2:
			if not mouse_1:
				last_pos = square.loc

	return last_pos


def putting_in_graveyard(name):

	promoted_name = name

	if name[1] == 'p':
		for piece in pieces_list:
			if piece.name == name:
				promoted_name = piece.promoted_name

	if promoted_name[:2] == 'bk':
		piece_loc[name] = 'black king graveyard'
	elif promoted_name[:2] == 'bq':
		piece_loc[name] = 'black queen graveyard'
	elif promoted_name[:2] == 'bp':
		piece_loc[name] = 'black pawn graveyard'
	elif promoted_name[:2] == 'br':
		piece_loc[name] = 'black rook graveyard'
	elif promoted_name[:2] == 'bb':
		piece_loc[name] = 'black bishop graveyard'
	elif promoted_name[:2] == 'bn':
		piece_loc[name] = 'black knight graveyard'

	elif promoted_name[:2] == 'wk':
		piece_loc[name] = 'white king graveyard'
	elif promoted_name[:2] == 'wq':
		piece_loc[name] = 'white queen graveyard'
	elif promoted_name[:2] == 'wp':
		piece_loc[name] = 'white pawn graveyard'
	elif promoted_name[:2] == 'wr':
		piece_loc[name] = 'white rook graveyard'
	elif promoted_name[:2] == 'wb':
		piece_loc[name] = 'white bishop graveyard'
	elif promoted_name[:2] == 'wn':
		piece_loc[name] = 'white knight graveyard'


def dragging(hovered_piece, dragged_piece, last_pos, board_locs, square_list):
	global hover_loc
	global clicked_piece
	global clicked_cell

	if clicked_piece is not None:
		if clicked_piece.name != clicked_piece.promoted_name:
			demotion(clicked_piece, movement='clicked')

	if dragged_piece is not None:
		if dragged_piece.name != dragged_piece.promoted_name:
			demotion(dragged_piece, movement='dragged')

	# Checks if a specific piece is being clicked on
	if hovered_piece is not None and mouse_1:
		hover_loc = hovered_piece.loc
		if dragged_piece is None:
			# Sets the picked up piece to be referred to as dragged_piece
			dragged_piece = hovered_piece
		# Sends the piece back to where it came from if it was let go over an invalid area
		if hovered_piece == dragged_piece and last_pos != 'off screen':
			last_pos = piece_loc[dragged_piece.name]
	# Logic for when a piece is being held
	if dragged_piece is not None and mouse_1:
		# sets the location of a piece to an area off the board
		piece_loc[dragged_piece.name] = 'off screen'

		# Checks if the colour is black or white and sets the value to 0 or 1. Used for the line right after
		if dragged_piece.colour == 'black':
			a = 0
		else:
			a = 1

		# eg. pieces['pawns'][0][3].follow()
		pieces[dragged_piece.rank_name.lower() + 's'][a][dragged_piece.file_id].follow()

	# Checks if the piece is let go
	if dragged_piece is not None and not mouse_1:
		# Sets the temp_last_pos to the cell where the mouse is hovering
		temp_last_pos = mouse_on_cell(last_pos)

		for name in piece_loc:

			# Checks if another piece occupies the temp_last_pos square
			if piece_loc[name] == temp_last_pos:

				# If the piece is of the same colour, the dragged piece goes back to where it was before
				if name[0] == dragged_piece.name[0] or name[1] == 'k':
					temp_last_pos = last_pos
				# Otherwise, the piece that occupied the square previously is captured
				else:
					putting_in_graveyard(name)

		# Makes the piece stay at the temp_last_pos which is the cell where the mouse is hovering
		last_pos = temp_last_pos
		piece_loc[dragged_piece.name] = last_pos

		if True in mouse_1_states and not mouse_1_states[-1] \
				and hover_loc is not None:

			if clicked_piece is None:
				clicked_cell = check_hover_cell(square_list)
				if clicked_cell is not None:
					if hover_loc == clicked_cell.loc:
						clicked_cell.highlight = True
						clicked_piece = dragged_piece

		dragged_piece = None  # Clears the dragged piece variable

	if not mouse_1:

		if True in mouse_1_states and not mouse_1_states[-1]:
			target_cell = check_hover_cell(square_list)

			if clicked_cell is not None:
				if target_cell is not None and clicked_cell.was_highlighted:
					clicked_cell.was_highlighted = False

					should_move = True

					for name in piece_loc:
						if piece_loc[name] == target_cell.loc:
							# If the piece is of the same colour, the clicked piece goes back to where it was before
							if name[0] == clicked_piece.name[0] or name[1] == 'k':
								for piece in pieces_list:
									if piece.loc == 'off screen':
										should_move = False
										clicked_piece = piece
										dragged_piece = piece
										for cell in cells:
											if cell.loc == piece_loc[name]:
												cell.highlight = True
							# Otherwise, the piece that occupied the square previously is captured
							else:
								putting_in_graveyard(name)
					if clicked_piece is not None:

						if should_move:
							piece_loc[clicked_piece.name] = target_cell.loc

						if target_cell.loc in piece_loc.values():
							clicked_piece = None

	if mouse_1:
		for obj in square_list:
			if obj.highlight:
				obj.was_highlighted = True
				obj.highlight = False
				if check_hover_cell(square_list) is None:
					clicked_piece = None

	if True:
		# Counters for the graveyard
		b_king_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black king graveyard':
				b_king_count += 1

		if b_king_count != 0:
			message_to_screen('x' + str(b_king_count),
			                  black,
			                  x_displace=board_locs['black king graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black king graveyard'][1],
			                  side='custom_mid_left')

		b_queen_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black queen graveyard':
				b_queen_count += 1

		if b_queen_count != 0:
			message_to_screen('x' + str(b_queen_count),
			                  black,
			                  x_displace=board_locs['black queen graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black queen graveyard'][1],
			                  side='custom_mid_left')

		b_pawn_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black pawn graveyard':
				b_pawn_count += 1

		if b_pawn_count != 0:
			message_to_screen('x' + str(b_pawn_count),
			                  black,
			                  x_displace=board_locs['black pawn graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black pawn graveyard'][1],
			                  side='custom_mid_left')

		b_rook_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black rook graveyard':
				b_rook_count += 1

		if b_rook_count != 0:
			message_to_screen('x' + str(b_rook_count),
			                  black,
			                  x_displace=board_locs['black rook graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black rook graveyard'][1],
			                  side='custom_mid_left')

		b_bishop_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black bishop graveyard':
				b_bishop_count += 1

		if b_bishop_count != 0:
			message_to_screen('x' + str(b_bishop_count),
			                  black,
			                  x_displace=board_locs['black bishop graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black bishop graveyard'][1],
			                  side='custom_mid_left')

		b_knight_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'black knight graveyard':
				b_knight_count += 1

		if b_knight_count != 0:
			message_to_screen('x' + str(b_knight_count),
			                  black,
			                  x_displace=board_locs['black knight graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['black knight graveyard'][1],
			                  side='custom_mid_left')

		w_king_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white king graveyard':
				w_king_count += 1

		if w_king_count != 0:
			message_to_screen('x' + str(w_king_count),
			                  black,
			                  x_displace=board_locs['white king graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white king graveyard'][1],
			                  side='custom_mid_left')

		w_queen_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white queen graveyard':
				w_queen_count += 1

		if w_queen_count != 0:
			message_to_screen('x' + str(w_queen_count),
			                  black,
			                  x_displace=board_locs['white queen graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white queen graveyard'][1],
			                  side='custom_mid_left')

		w_pawn_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white pawn graveyard':
				w_pawn_count += 1

		if w_pawn_count != 0:
			message_to_screen('x' + str(w_pawn_count),
			                  black,
			                  x_displace=board_locs['white pawn graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white pawn graveyard'][1],
			                  side='custom_mid_left')

		w_rook_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white rook graveyard':
				w_rook_count += 1

		if w_rook_count != 0:
			message_to_screen('x' + str(w_rook_count),
			                  black,
			                  x_displace=board_locs['white rook graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white rook graveyard'][1],
			                  side='custom_mid_left')

		w_bishop_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white bishop graveyard':
				w_bishop_count += 1

		if w_bishop_count != 0:
			message_to_screen('x' + str(w_bishop_count),
			                  black,
			                  x_displace=board_locs['white bishop graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white bishop graveyard'][1],
			                  side='custom_mid_left')

		w_knight_count = 0
		for key in piece_loc:
			if piece_loc[key] == 'white knight graveyard':
				w_knight_count += 1

		if w_knight_count != 0:
			message_to_screen('x' + str(w_knight_count),
			                  black,
			                  x_displace=board_locs['white knight graveyard'][0] + img_width / 2,
			                  y_displace=board_locs['white knight graveyard'][1],
			                  side='custom_mid_left')

	return hovered_piece, dragged_piece, last_pos


def demotion(piece, movement):
	should_demote = False
	if piece.colour == 'white':
		white_pawn_mini.draw()
	else:
		black_pawn_mini.draw()

	if movement == 'clicked':
		if mouse_1:
			should_demote = bool(check_hover_mini(piece.colour, promotion=False))
	elif movement == 'dragged':
		if not mouse_1:
			should_demote = bool(check_hover_mini(piece.colour, promotion=False))

	if should_demote:
		piece.demotion()


def promotion_check():
	global mouse_1
	global promotion_states
	global should_promote
	global game_exit
	for piece in pieces_list:
		if piece.promoted_name[:2] == 'wp':
			if '8' in piece_loc[piece.promoted_name]:
				should_promote = True
				if True in promotion_states:
					done = False
					promote_to = 'Queen'
					while not done:

						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								done = True
								game_exit = True
							if event.type == pygame.KEYDOWN:
								if event.key == pygame.K_p:
									pass
							if event.type == pygame.MOUSEBUTTONDOWN:
								if event.button == 1:
									mouse_1 = True
							if event.type == pygame.MOUSEBUTTONUP:
								if event.button == 1:
									mouse_1 = False
						for mini in mini_list:
							if mini.colour == 'white' and mini.rank != 'Pawn':
								mini.draw()
								if mouse_1:
									clicked_mini = check_hover_mini('white')
									if clicked_mini is not None:
										done = True
										promote_to = clicked_mini.rank

						pygame.display.update()
						clock.tick(60)
					should_promote = False
					piece.promotion(promote_to)

		elif piece.promoted_name[:2] == 'bp':
			if '1' in piece_loc[piece.promoted_name]:
				should_promote = True
				if True in promotion_states:
					done = False
					promote_to = 'Queen'
					while not done:

						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								done = True
								game_exit = True
							if event.type == pygame.KEYDOWN:
								if event.key == pygame.K_p:
									pass
							if event.type == pygame.MOUSEBUTTONDOWN:
								if event.button == 1:
									mouse_1 = True
							if event.type == pygame.MOUSEBUTTONUP:
								if event.button == 1:
									mouse_1 = False
						for mini in mini_list:
							if mini.colour == 'black' and mini.rank != 'Pawn':
								mini.draw()
								if mouse_1:
									clicked_mini = check_hover_mini('black')
									if clicked_mini is not None:
										done = True
										promote_to = clicked_mini.rank

						pygame.display.update()
						clock.tick(60)
					should_promote = False
					piece.promotion(promote_to)


def available_movement(piece, mode):

	global dragged_piece_loc
	global available_movement_wait

	if piece.promoted_name[1] == 'r' or piece.promoted_name[1] == 'q':

		c = True

		if mode == 'dragged' and dragged_piece_loc:
			for i in range(len(dragged_piece_loc)):
				if dragged_piece_loc[i] != 'off screen':
					letter, number = dragged_piece_loc[i][0], dragged_piece_loc[i][1]
					dragged_piece_loc = dragged_piece_loc[i:i + 1]
					break

		else:
			letter, number = piece.loc[0], piece.loc[1]

		# if dragged_piece_loc:
		# 	a, b = dragged_piece_loc[0]
		#
		# 	if b.isdigit():
		# 		c = False
		if number.isdigit() and c:

			dragged_piece_loc.insert(0, piece.loc)

			numbers = list(range(1, 9))
			numbers.remove(int(number))

			letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
			letters.remove(letter)

			for n in numbers:
				test_loc = letter + str(n)

				for cell in cells:
					if cell.loc == test_loc:
						if available_movement_wait:
							cell.available = True
							available_movement_wait = False
						available_movement_wait = True

			for l in letters:
				test_loc = l + number

				for cell in cells:
					if cell.loc == test_loc:
						if available_movement_wait:
							cell.available = True
							available_movement_wait = False
						available_movement_wait = True
		# elif dragged_piece_loc:
		# 	if dragged_piece_loc[0] == 'off screen':
		# 		del dragged_piece_loc[0]


def game_loop():
	global mouse_1
	global mouse_1_states
	global loc_squares
	global piece_loc
	global should_promote
	global promotion_states
	global game_exit
	global clicked_piece
	global available_movement_wait

	game_exit = False

	mouse_1 = False

	dragged_piece = None

	last_pos = piece_loc['bpa']

	while not game_exit:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_exit = True
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					pass
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					mouse_1 = True
			if event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					mouse_1 = False

		mouse_1_states.insert(0, mouse_1)
		mouse_1_states = mouse_1_states[:15]

		promotion_states.insert(0, should_promote)
		promotion_states = promotion_states[:2]

		Display.fill(grey)

		Display.fill(ochre, rect=[0, 0, display_width / 4, display_height])

		height = img_width / 2

		Display.fill(grey, rect=[0,
		                          (display_height / 2) - height,
		                          display_width / 4,
		                          2 * height])

		# loc_squares is a dictionary of square
		# location names as the keys and the center coordinate of
		# the squares as the value eg 'a8': [272.5, 72.5]
		loc_squares, square_list = generate_board()

		hovered_piece = check_hover_piece()

		hovered_piece, dragged_piece, last_pos = dragging(hovered_piece, dragged_piece, last_pos, loc_squares,
		                                                  square_list)
		promotion_check()

		highlight = (o.highlight for o in cells)
		if True in highlight:
			if clicked_piece is not None:
				available_movement(clicked_piece, 'clicked')

		else:
			available_movement_wait = False
			for cell in cells:
				cell.available = False

		if dragged_piece is not None:
			available_movement(dragged_piece, 'dragged')

		pygame.display.update()
		clock.tick(60)

	pygame.quit()
	quit()


dragged_piece_loc = []

# Cells for the board

cells = []

for i in range(sqrs_in_line ** 2):
	cells.append(Cell())

# Index 0 is black, Index 1 is white
pieces = {'pawns': [[], []],
          'bishops': [[], []],
          'knights': [[], []],
          'rooks': [[], []],
          'queens': [[], []],
          'kings': [[], []]}

pieces_list = []

for i in range(8):
	pieces['pawns'][0].append(Piece('black', 'Pawn', i))
	pieces['pawns'][1].append(Piece('white', 'Pawn', i))

	pieces_list.append(pieces['pawns'][0][i])
	pieces_list.append(pieces['pawns'][1][i])

for v in range(2):
	pieces['bishops'][0].append(Piece('black', 'Bishop', v))
	pieces['bishops'][1].append(Piece('white', 'Bishop', v))
	pieces['knights'][0].append(Piece('black', 'Knight', v))
	pieces['knights'][1].append(Piece('white', 'Knight', v))
	pieces['rooks'][0].append(Piece('black', 'Rook', v))
	pieces['rooks'][1].append(Piece('white', 'Rook', v))

	pieces_list.append(pieces['bishops'][0][v])
	pieces_list.append(pieces['bishops'][1][v])
	pieces_list.append(pieces['knights'][0][v])
	pieces_list.append(pieces['knights'][1][v])
	pieces_list.append(pieces['rooks'][0][v])
	pieces_list.append(pieces['rooks'][1][v])

pieces['queens'][0].append(Piece('black', 'Queen', 0))
pieces['queens'][1].append(Piece('white', 'Queen', 0))
pieces['kings'][0].append(Piece('black', 'King', 0))
pieces['kings'][1].append(Piece('white', 'King', 0))

pieces_list.append(pieces['queens'][0][0])
pieces_list.append(pieces['queens'][1][0])
pieces_list.append(pieces['kings'][0][0])
pieces_list.append(pieces['kings'][1][0])

print(pieces)
print(pieces_list)

mini_list = list()

white_pawn_mini = Mini('white', 'Pawn', white_pawn_mini_img, 2.5)
mini_list.append(white_pawn_mini)
mini_list.append(Mini('white', 'Queen', white_queen_mini_img, 4))
mini_list.append(Mini('white', 'Rook', white_rook_mini_img, 3))
mini_list.append(Mini('white', 'Knight', white_knight_mini_img, 2))
mini_list.append(Mini('white', 'Bishop', white_bishop_mini_img, 1))

black_pawn_mini = Mini('black', 'Pawn', black_pawn_mini_img, 2.5)
mini_list.append(black_pawn_mini)
mini_list.append(Mini('black', 'Queen', black_queen_mini_img, 4))
mini_list.append(Mini('black', 'Rook', black_rook_mini_img, 3))
mini_list.append(Mini('black', 'Knight', black_knight_mini_img, 2))
mini_list.append(Mini('black', 'Bishop', black_bishop_mini_img, 1))


# The format of the keys is 1st letter: colour, 2nd letter: piece, 3rd letter: starting file
piece_loc = {'wpa': 'a2',
             'wpb': 'b2',
             'wpc': 'c2',
             'wpd': 'd2',
             'wpe': 'e2',
             'wpf': 'f2',
             'wpg': 'g2',
             'wph': 'h2',
             'wbc': 'c1',
             'wbf': 'f1',
             'wnb': 'b1',
             'wng': 'g1',
             'wra': 'a1',
             'wrh': 'h1',
             'wk': 'e1',
             'wq': 'd1',
             'bpa': 'a7',
             'bpb': 'b7',
             'bpc': 'c7',
             'bpd': 'd7',
             'bpe': 'e7',
             'bpf': 'f7',
             'bpg': 'g7',
             'bph': 'h7',
             'bbc': 'c8',
             'bbf': 'f8',
             'bnb': 'b8',
             'bng': 'g8',
             'bra': 'a8',
             'brh': 'h8',
             'bk': 'e8',
             'bq': 'd8'}  # put the piece locations in here
#  and generate them according to this dictionary, change as needed

game_loop()
