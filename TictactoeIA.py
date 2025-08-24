import math

def initialize_board():
	return [[" " for _ in range(3)] for _ in range(3)]

def copy_board(board):
	return [row[:] for row in board]

def print_board(board):
	print()
	for i, row in enumerate(board):
		print(" {} | {} | {} ".format(row[0], row[1], row[2]))
		if i < 2:
			print("-" * 12)
	print()

def legal_moves(board):
	return [(i,j) for i in range(3) for j in range(3) if board[i][j] == " "]

def apply_move(board, move, player):
	new_board = copy_board(board)
	new_board[move[0]][move[1]] = player
	return new_board

def switch_player(to_move):
	return "O" if to_move == "X" else "X"
	
def winner(board):
	for player in ["X", "O"]:
		for i in range(3):
			if board[i][0] == player and board[i][1] == player and board[i][2] == player:
				return player
			if board[0][i] == player and board[1][i] == player and board[2][i] == player:
				return player
		if board[0][0] == player and board[1][1] == player and board[2][2] == player:
				return player
		if board[0][2] == player and board[1][1] == player and board[2][0] == player:
				return player
	return None
	
def full_board(board):
	return all(board[i][j] != " " for i in range(3) for j in range(3))

def is_terminal(board):
	return full_board(board) or (winner(board) is not None)

def utility(board):
	player = winner(board)
	if player == "X":
		return 1
	elif player == "O":
		return -1
	else:
		return 0
	
def rotate90(board):
    return [list(row) for row in zip(*board[::-1])]

def reflect_h(board):
    return [list(reversed(row)) for row in board]

def all_symmetries(board):
    b0 = [row[:] for row in board]
    b1 = rotate90(b0)
    b2 = rotate90(b1)
    b3 = rotate90(b2)
    m0 = reflect_h(b0)
    m1 = rotate90(m0)
    m2 = rotate90(m1)
    m3 = rotate90(m2)
    return [b0, b1, b2, b3, m0, m1, m2, m3]

def min_board(board):
	return min(tuple(cell for row in b for cell in row) for b in all_symmetries(board))

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

posible_boards = {}
stats = {"nodes": 0, "coincidences": 0, "prunes": 0}

def reset_stats():
	stats["nodes"] = 0
	stats["coincidences"] = 0
	stats["prunes"] = 0

def alpha_beta(board, to_move, alpha = -math.inf, beta = math.inf):
	stats["nodes"] += 1
	
	if is_terminal(board):
		return utility(board), None
	
	current_key = (min_board(board), to_move)	
	moves = order_moves(board)
	best_move = 0

	if to_move == "X":
		value = -math.inf
	
		for i, move in enumerate(moves):
			child = apply_move(board, move, "X")
			child_key = (min_board(child), switch_player(to_move))

			if child_key in posible_boards:
				stats["coincidences"] += 1
				child_value = posible_boards[child_key]
			else:
				child_value, _ = alpha_beta(child, switch_player(to_move), alpha, beta)
				posible_boards[child_key] = child_value

			if child_value > value:
				value = child_value
				best_move = move
			alpha = max(alpha, value)
			if alpha >= beta:
				stats["prunes"] += len(moves) - (i + 1)
				break
	else:
		value = math.inf
	
		for i, move in enumerate(moves):
			child = apply_move(board, move, "O")
			child_key = (min_board(child), switch_player(to_move))

			if child_key in posible_boards:
				stats["coincidences"] += 1
				child_value = posible_boards[child_key]
			else:
				child_value, _ = alpha_beta(child, switch_player(to_move), alpha, beta)
				posible_boards[child_key] = child_value

			if child_value < value:
				value = child_value
				best_move = move
			beta = min(beta, value)
			if alpha >= beta:
				stats["prunes"] += len(moves) - (i + 1)
				break

	posible_boards[current_key] = value
	return value, best_move

def ai_best_move(board, to_move):
	reset_stats()
	value, move = alpha_beta(board, to_move)
	return value, move

def ask_human():
	while True:
		player = input("Como quieres jugar? (X o O): ").strip().upper()
		if player in ("X", "O"): return player 
		print("ERROR!!! Ingresa un jugador valido\n")

def human_move(board):
	moves = legal_moves(board)
	row = int(input(f"En que fila quieres jugar? (0-2): "))
	while not 0 <= row <= 2:
		row = int(input("ERROR!!! Ingresa una fila dentro de los limites (0-2): "))
	column = int(input(f"En que columna quieres jugar? (0-2): "))
	while not 0 <= column <= 2:
		column = int(input("ERROR!!! Ingresa una columna dentro de los limites (0-2): "))
	return (row, column)

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
			value, move = ai_best_move(board, to_move)
			board = apply_move(board, move, to_move)
			print(f"La IA juega {move}. Valor con respecto a X: {value}")
			print(f"Nodos revisados: {stats['nodes']} | Coincidencias Simetricas: {stats['coincidences']} | Podas: {stats['prunes']}")
			print_board(board)
			if is_terminal(board):
				break
			to_move = switch_player(to_move)

	w = winner(board)
	if w is None: print("Empate -_-")
	else: print(f"Ha ganado {w}!!!")

main()