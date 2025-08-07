# PRG-Assignment3
PRG-Assignment3
from random import randint 

#Game data
player  = {}
game_map = []
fog = []   

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper','silver','gold']
minerals_names = {"C" : "copper",'S' : 'silver' , 'G' : 'gold'}
prices = {'copper' : (1,3), 'silver' : (5,8), 'gold' : (10,18)}
pickaxe_price = [50, 150]


def show_intro():
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.\n")
    print("How quickly can you get the 500 GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")

show_intro()


def show_main_menu():
    print("\n--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(Q)uit")
    print("------------------")

# Run intro when the program starts
show_intro()

# Set the game state (controls which menu we're in)
game_state = 'main'

def show_town_menu(player):
    print(f"\nDAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------") 

def initialize_fog(height, width):
    return [['?' for _ in range(width)] for _ in range(height)]

def clear_fog(fog, player, width, height):
    x, y = player['x'], player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx = x + dx
            ny = y + dy
            if 0 <= ny < height and 0 <= nx < width:
                fog[ny][nx] = ''

def initialize_game():
    game_map = []
    with open("Level1.txt", "r") as f:
        for line in f:
            game_map.append(list(line.strip('\n')))
    height = len(game_map)
    width = len(game_map[0])

    fog = initialize_fog(height, width)

    player = {'name': '',
        'x': 0,
        'y': 0,
        'copper': 0,
        'silver': 0,
        'gold': 0,
        'GP': 0,
        'day': 1,
        'steps': 0,
        'turns': 20}
    for y in range(height):
        for x in range(width):
            if game_map[y][x] == 'M':
                player['x'] = x
                player['y'] = y
                break
    clear_fog(fog, player, width, height)
    return game_map, fog, player, width, height


# Main game loop
while True:
    if game_state == 'main':
        show_main_menu()
        choice = input("Your choice? ").lower()

        if choice == 'n':
            name = input("Greetings, miner! What is your name? ")
            print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
            game_map, fog, player, width, height = initialize_game()
            player['name'] = name
            game_state = 'town' 
        
        elif choice == 'l':
            print("Load game feature not yet implemented.")
        elif choice == 'q':
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")

    elif game_state == 'town':
            show_town_menu(player)
            choice = input("Your choice? ").lower()

            if choice == 'i':
                print("----- Player Info -----")
                print(f"Name: {player['name']}")
                print(f"GP: {player['GP']}")
                print(f"Steps: {player['steps']}")
                print(f"Load: {player['copper'] + player['silver'] + player['gold']} / 10")
                print(f"Copper: {player['copper']}  Silver: {player['silver']}  Gold: {player['gold']}")
                print(f"Position: ({player['x']}, {player['y']})")
            elif choice == 'm':
                # Check that the map has been initialized
                if 'x' not in player or game_map == []:
                    print("Map not initialized yet.")
                else:
                    print("+" + "---+" * width)
                    for y in range(height):
                        row = ""
                        for x in range(width):
                            if player['x'] == x and player['y'] == y:
                                row += "| M "
                            elif fog[y][x] == '?':
                                row += "| ? "
                            else:
                                row += f"| {game_map[y][x]} "
                        row += "|"
                        print(row)
                        print("+" + "---+" * width)