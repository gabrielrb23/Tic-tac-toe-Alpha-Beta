def initialize_board():
	board = []
	for i in range(3):
		row = []
		for j in range(3):
			row.append(" ")
		board.append(row)
	return board

def print_board(board):
	print()
	for i, row in enumerate(board):
		print(" | ".join(row))
		if i<2: 
			print("-" * 9)
	print()

def make_move(board, player, row, col):
	if board[row][col] == " ":
		board[row][col] = player
		return True
	else:
		print("No se puede realizar ese movimiento\n")
		return False
	
def victory(board, player):
	for i in range(3):
		if board[i][0] == player and board[i][1] == player and board[i][2] == player:
			return True
		if board[0][i] == player and board[1][i] == player and board[2][i] == player:
			return True
	if board[0][0] == player and board[1][1] == player and board[2][2] == player:
		return True
	if board[0][2] == player and board[1][1] == player and board[2][0] == player:
		return True
	
def game_over(board):
	for i in range(3):
		for j in range(3):
			if board[i][j] == " ":
				return False
	return True


player = input("Jugador 1, como quieres jugar? (X o O): ")

#if player == "X":
#	computer = "O"
#else:
#	computer = "X"

board = initialize_board()
print_board(board)
winner = False

while not game_over(board) and not winner:
	row = int(input(f"Jugador {player}, en que fila quieres jugar? (0-2): "))
	while not 0 <= row <= 2:
		row = int(input("ERROR!!! Ingresa una fila dentro de los limites (0-2): "))
	column = int(input(f"Jugador {player}, en que columna quieres jugar? (0-2): "))
	while not 0 <= column <= 2:
		column = int(input("ERROR!!! Ingresa una columna dentro de los limites (0-2): "))

	if make_move(board, player, row, column):
		print_board(board)
		if victory(board, player):
			print(f"Felicidades jugador {player}!!! Has ganado.")
			winner = True
		player = "X" if player == "O" else "O"

if not winner: print("No hay ganador :(")