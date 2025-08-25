import math

# Creates an empty list of lists
def initialize_board():
	return [[" " for _ in range(3)] for _ in range(3)]

# Copies the board
def copy_board(board):
	return [row[:] for row in board]

# Prints the board
def print_board(board):
	print()
	for i, row in enumerate(board):
		print(" {} | {} | {} ".format(row[0], row[1], row[2]))
		if i < 2:
			print("-" * 12)
	print()

# Returns a list of empty positions on the board
def legal_moves(board):
	return [(i,j) for i in range(3) for j in range(3) if board[i][j] == " "]

# Returns the board with the move applied
def apply_move(board, move, player):
	new_board = copy_board(board)
	new_board[move[0]][move[1]] = player
	return new_board

# Switches the player
def switch_player(to_move):
	return "O" if to_move == "X" else "X"

# Returns the winner
def winner(board):
	for player in ["X", "O"]:
		for i in range(3):
			if board[i][0] == player and board[i][1] == player and board[i][2] == player:	# Rows
				return player
			if board[0][i] == player and board[1][i] == player and board[2][i] == player:	# Columns
				return player
		if board[0][0] == player and board[1][1] == player and board[2][2] == player:		# Diagonal 1
				return player
		if board[0][2] == player and board[1][1] == player and board[2][0] == player:		# Diagonal 2
				return player
	return None

# Returns whether the board is full
def full_board(board):
	return all(board[i][j] != " " for i in range(3) for j in range(3))

# Returns whether the board has a winner or is full
def is_terminal(board):
	return full_board(board) or (winner(board) is not None)

# Returns the board utility; positive favors player X, negative favors player O
def utility(board):
	player = winner(board)
	if player == "X":
		return 1
	elif player == "O":
		return -1
	else:
		return 0

# Returns the board rotated 90 degrees clockwise
def rotate90(board):
    return [list(row) for row in zip(*board[::-1])]		# reverses the rows -> transposes the board

# Returns the board reflected horizontally
def reflect_h(board):
	return [row[::-1] for row in board]					# reverses the columns

# Returns a list with all symmetric boards
def all_symmetries(board):
    b0 = [row[:] for row in board]		# create a copy
    b1 = rotate90(b0)					# 90° rotation
    b2 = rotate90(b1)					# 180° rotation
    b3 = rotate90(b2)					# 270° rotation
    m0 = reflect_h(b0)					# horizontal reflection
    m1 = rotate90(m0)					# 90° rotation of the reflection
    m2 = rotate90(m1)					# 180° rotation of the reflection
    m3 = rotate90(m2)					# 270° rotation of the reflection
    return [b0, b1, b2, b3, m0, m1, m2, m3]

# Returns the lexicographically smallest board
def min_board(board):
	return min(tuple(cell for row in b for cell in row) for b in all_symmetries(board)) 	# flattens the boards -> chooses the minimum

# Prioritizes moves: center, then corners, then edges
def order_moves(board):
	moves = legal_moves(board)
	corners = [(0,0), (0,2), (2,0), (2,2)]
	edges = [(0,1), (1,0), (1,2),(2,1)]

	seq = []
	if (1,1) in moves:
		seq.append((1,1))
	seq += [m for m in moves if m in corners]
	seq += [m for m in moves if m in edges]

	return seq

# Stores all possible boards
posible_boards = {}										# Key: (board, player), value: utility, distance to terminal board
stats = {"nodes": 0, "coincidences": 0, "prunes": 0}	# Statistics

# Resets statistics
def reset_stats():
	stats["nodes"] = 0
	stats["coincidences"] = 0
	stats["prunes"] = 0

# Returns whether the candidate move is better than the current best move
def better_for_max(cand, best):
	(b_value, b_move, b_distance) = best
	(c_value, c_move, c_distance) = cand

	if b_value != c_value:				# They are different
		return c_value>b_value			# If the candidate value is larger, the candidate is better
	if c_value > 0:						# X can win
		return c_distance<b_distance	# Candidate distance is smaller -> we want it sooner
	if c_value < 0:						# O can win
		return c_distance>b_distance	# Candidate distance is larger -> we want it later
	return c_distance>b_distance		# Draw -> we prefer it later

def better_for_min(cand, best):
	(b_value, b_move, b_distance) = best
	(c_value, c_move, c_distance) = cand

	if b_value != c_value:				# They are different
		return c_value<b_value			# If the candidate value is smaller, the candidate is better
	if c_value > 0:						# X can win
		return c_distance>b_distance	# Candidate distance is larger -> we want it later
	if c_value < 0:						# O can win
		return c_distance<b_distance	# Candidate distance is smaller -> we want it sooner
	return c_distance<b_distance		# Draw -> we prefer it sooner

# Returns the best move and its utility
def alpha_beta(board, to_move, alpha = -math.inf, beta = math.inf):
	stats["nodes"] += 1						# Visited nodes
	
	if is_terminal(board):
		return utility(board), None, 0
	
	key_here = (min_board(board), to_move)	# Key of the current board
	moves = order_moves(board)				# Possible moves

	if to_move == "X":																						# Maximizer
		best = (-math.inf, None, math.inf)																	# Initial best move (any move is better)
		for i, move in enumerate(moves):
			child = apply_move(board, move, "X")															# Plays the move and gets the child board
			child_key = (min_board(child), switch_player(to_move))											# Key of the child board (lexicographically minimized)

			if child_key in posible_boards:																	# If the child board was already evaluated
				stats["coincidences"] += 1																	# Symmetric matches
				child_value, child_distance = posible_boards[child_key]										# Utility of the child board
			else:
				child_value, _, child_distance = alpha_beta(child, switch_player(to_move), alpha, beta)		# Computes the child's utility
				posible_boards[child_key] = (child_value, child_distance)

			cand = (child_value, move, child_distance + 1)
			if better_for_max(cand, best):																	# If the child move is better than the current best, update it
				best = cand

			alpha = max(alpha, best[0])																		# Update alpha
			if alpha >= beta:
				stats["prunes"] += len(moves) - (i + 1)														# Count prunings
				break
	else:																									# Minimizer
		best = (math.inf, None, math.inf)																	# Initial best move (any move is better)
		for i, move in enumerate(moves):
			child = apply_move(board, move, "O")															# Plays the move and gets the child board
			child_key = (min_board(child), switch_player(to_move))											# Key of the child board

			if child_key in posible_boards:																	# If the child board was already evaluated
				stats["coincidences"] += 1																	# Symmetric matches
				child_value, child_distance = posible_boards[child_key]										# Utility of the child board
			else:
				child_value, _, child_distance = alpha_beta(child, switch_player(to_move), alpha, beta)		# Computes the child's utility
				posible_boards[child_key] = child_value, child_distance

			cand = (child_value, move, child_distance + 1)
			if better_for_min(cand, best):																	# If the child move is better than the current best, update it
				best = cand

			beta = min(beta, best[0])																		# Update beta
			if alpha >= beta:
				stats["prunes"] += len(moves) - (i + 1)														# Count prunings
				break

	posible_boards[key_here] = (best[0], best[2])															# Store the utility and distance of the current board
	return best[0], best[1], best[2]																		# Return the best move

# Returns the AI's best move
def ai_best_move(board, to_move):
	reset_stats()											# Reset statistics
	value, move, distance = alpha_beta(board, to_move)
	return value, move, distance

# Asks the player which side they want
def ask_human():
	while True:
		player = input("Como quieres jugar? (X o O): ").strip().upper()
		if player in ("X", "O"): return player 
		print("ERROR!!! Ingresa un jugador valido\n")

# Asks the player which position to play
def human_move(board):
	moves = legal_moves(board)
	while True:
		row = int(input(f"En que fila quieres jugar? (0-2): "))
		while not 0 <= row <= 2:
			row = int(input("ERROR!!! Ingresa una fila dentro de los limites (0-2): "))
		column = int(input(f"En que columna quieres jugar? (0-2): "))
		while not 0 <= column <= 2:
			column = int(input("ERROR!!! Ingresa una columna dentro de los limites (0-2): "))
		if (row, column) in moves:	
			return (row, column)
		print("ERROR!!! No puedes realizar ese movimiento\n")

# Main function
def main():
	player = ask_human()
	ia = switch_player(player)
	print(f"La IA jugara como {ia}")
	board = initialize_board()
	print_board(board)

	to_move = "X"
	while not is_terminal(board):
		if player == to_move:		
			move = human_move(board)
			board = apply_move(board, move, to_move)
			print_board(board)
			if is_terminal(board):
				break
			to_move = switch_player(to_move)
		else:
			value, move, distance = ai_best_move(board, to_move)
			board = apply_move(board, move, to_move)
			print(f"La IA juega {move}. Valor con respecto a X: {value} | Distancia hasta final: {distance}")
			print(f"Nodos revisados: {stats['nodes']} | Coincidencias Simetricas: {stats['coincidences']} | Podas: {stats['prunes']}")
			print_board(board)
			if is_terminal(board):
				break
			to_move = switch_player(to_move)

	w = winner(board)
	if w is None: print("Empate...")
	else: print(f"Ha ganado {w}!!!")

main()