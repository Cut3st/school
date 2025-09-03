
#Function 1: Initialize an empty board
def init_board():
    board = [[0 for _ in range(board_size)] for _ in range(board_size)]
    for row in board:
        print(" ".join(str(cell) for cell in row))

# Function 2: Get starting position for a ship
def get_ship_position(ship_name):
## TODO: Prompt the user for coordinates in "row,col" format
## Convert to tuple of integers and return
    for ship in ships:
        while True:
            coord = input(f"Please enter start_position of {ship} (row,col): ")
            try:
                row_str, col_str = coord.split(",")
                row = int(row_str)
                col = int(col_str)
                break
            except:
                print("Invalid Input! Try again in proper format (e.g 2,3)")
# Function 3: Place ship on the boarda
def place_ship(board, start_pos, length, symbol):
## TODO: Place the ship horizontally from start_pos for 'length' cells
    pass
    
# Function 4: Display the board
def display_board(board):
## TODO: Print each row of the board
    pass
# Function 5: Check attack validity
def check_attack(board, row, col):
## TODO: Return True if coordinates are within range, else False
    pass
board_size = 10
ships = {
    "Carrier": {"length": 5, "symbol": "C"},
    "Submarine": {"length": 3, "symbol": "S"}
    }
def main():
    game_board = init_board()
    positions = {}
    for ship_name, details in ships.items():
        start_pos = get_ship_position(ship_name)
        positions[ship_name] = start_pos
        place_ship(game_board, start_pos, details["length"], details["symbol"])
    # display_board(game_board)
# Example attack check
    # attack_row = int(input("Enter attack row (0-9): "))
    # attack_col = int(input("Enter attack column (0-9): "))
    # print("Valid attack?", check_attack(game_board, attack_row, attack_col))

if __name__ == "__main__":
    main()