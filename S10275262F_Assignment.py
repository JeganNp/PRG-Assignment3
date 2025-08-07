from random import randint 
import json 

#Game data
player  = {}
game_map = []
fog = []   

MAP_WIDTH = 0
MAP_HEIGHT = 0
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

def print_map(full=False):
    global game_map, fog, player, width, height

    if full:
        start_x, end_x = 0, width
        start_y, end_y = 0, height
    else:
        vision = 1
        start_x = max(0, player['x'] - vision)
        end_x = min(width, player['x'] + vision + 1)
        start_y = max(0, player['y'] - vision)
        end_y = min(height, player['y'] + vision + 1)

    print("+" + "-" * ((end_x - start_x) * 2 - 1) + "+")
    for y in range(start_y, end_y):
        row = "|"
        for x in range(start_x, end_x):
            if player['x'] == x and player['y'] == y:
                row += "M"
            elif fog[y][x] == '?':
                row += "?"
            else:
                row += game_map[y][x]
            row += ""
        print(row.rstrip() + "|")
    print("+" + "-" * ((end_x - start_x) * 2 - 1) + "+")

def initialize_game(): 
    global game_map, fog, player, width, height
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
        'turns': 20,
        'pickaxe': 1,
        'backpack': 10}
    for y in range(height):
        for x in range(width):
            if game_map[y][x] == 'M':
                player['x'] = x
                player['y'] = y
                break
    clear_fog(fog, player, width, height)
    

def enter_mine():
    global game_map, fog, player, width, height

    def print_local_viewport():
        print(f"\nDAY {player['day']}")
        print("+" + "-" * 5 + "+")  # 3 cells = 5 dashes including spaces
        for dy in range(-1, 2):
            row = "|"
            for dx in range(-1, 2):
                nx = player['x'] + dx
                ny = player['y'] + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if nx == player['x'] and ny == player['y']:
                        row += "M"
                    else:
                        row += f"{game_map[ny][nx]}"
                else:
                    row += "#"  # outside bounds
            print(row + "|")
        print("+" + "-" * 5 + "+")

    while True:
        print_local_viewport()
        print(f"Turns left: {player['turns']}   Load: {player['copper'] + player['silver'] + player['gold']} / 10   Steps: {player['steps']}")
        print("(WASD) to move")
        print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")
        action = input("Action? ").lower()

        if action == 'm':
            print_map(full=True)
            input("Press Enter to return to mining...")  # optional pause
            continue
        elif action == 'i':
            print("----- Player Information -----")
            print(f"Name: {player['name']}")
            print(f"GP: {player['GP']}")
            total_load = player['copper'] + player['silver'] + player['gold']
            print(f"Load: {total_load} / 10")
            print(f"Steps taken: {player['steps']}")
            print("-" * 30)
            input("Press Enter to continue...")
            continue
        elif action == 'p':
            print("You used the portal to return to town.")
            show_shop_menu()
            player['day'] += 1
            break
        elif action == 'q':
            print("Returning to main menu...")
            break
        elif action not in ['w', 'a', 's', 'd']:
            print("Invalid action.")
            continue

        # Movement logic
        dx, dy = 0, 0
        if action == 'w':
            dy = -1
        elif action == 's':
            dy = 1
        elif action == 'a':
            dx = -1
        elif action == 'd':
            dx = 1

        new_x = player['x'] + dx
        new_y = player['y'] + dy

        if 0 <= new_x < width and 0 <= new_y < height:
            if game_map[new_y][new_x] == '#':
                print("You bumped into a wall!")
            else:
                player['x'] = new_x
                player['y'] = new_y
                player['steps'] += 1
                player['turns'] -= 1
                clear_fog(fog, player, width, height)

                 # --- Check for automatic teleport back to town ---
                if player['turns'] <= 0:
                    print("You are exhausted.")
                    print("You place your portal stone here and zap back to town.")
                    show_shop_menu()
                    player['day'] += 1
                    player['turns'] = TURNS_PER_DAY
                    break

                tile = game_map[new_y][new_x]
                if tile in minerals_names:
                    mineral = minerals_names[tile]
                    allowed = {
                    1: ['copper'],
                    2: ['copper', 'silver'],
                    3: ['copper', 'silver', 'gold']}
                    if mineral not in allowed[player['pickaxe']]:
                        print(f"Your pickaxe can't mine {mineral}. Upgrade it first!")
                        continue

                    total_load = player['copper'] + player['silver'] + player['gold']
                    if total_load < 10:
                        # Define mining range per mineral
                        mining_ranges = {
                            'copper': (1, 5),
                            'silver': (1, 3),
                            'gold': (1, 2)}

                        mined_amount = randint(*mining_ranges[mineral])
                        current_load = player['copper'] + player['silver'] + player['gold']
                        space_left = 10 - current_load
                        mined_amount = min(mined_amount, space_left)

                        if mined_amount > 0:
                            player[mineral] += mined_amount
                            game_map[new_y][new_x] = '.'  # replace with dirt
                            print(f"You mined {mined_amount} {mineral}!")
                            print(f"Current load: {current_load + mined_amount}/10")
                        else:
                            print("Your backpack is full! Can't carry more.")

                        total_load = player['copper'] + player['silver'] + player['gold']
                        if total_load >= 10:
                            print("Your backpack is full. Returning to town to unload...")
                            print("You can't carry any more, so you can't go that way.")
                            print("You place your portal stone here and zap back to town.")
                            show_shop_menu()
                            player['day'] += 1
                            player['turns'] = TURNS_PER_DAY
                            break


def show_shop_menu():
    global player
    # Sell minerals first
    print("\n--- Selling Minerals ---")
    for mineral in ['copper', 'silver', 'gold']:
        amount = player[mineral]
        if amount > 0:
            min_price, max_price = prices[mineral]
            total_gp = 0
            for _ in range(amount):
                total_gp += randint(min_price, max_price)
            print(f"Sold {amount} {mineral} for {total_gp} GP.")
            player['GP'] += total_gp
            player[mineral] = 0
        else:
            print(f"You have no {mineral} to sell.")
    print(f"You now have {player['GP']} GP!")

    # Now show the shop upgrade menu
    while True:
        print("\n--------------------- Shop Menu ---------------------")
        if player['pickaxe'] == 1:
            print("(P)ickaxe upgrade to Level 2 to mine silver ore for 50 GP")
        elif player['pickaxe'] == 2:
            print("(P)ickaxe upgrade to Level 3 to mine gold ore for 150 GP")
        else:
            print("Pickaxe is already max level.")

        if player['backpack'] == 10:
            print("(B)ackpack upgrade to carry 12 items for 20 GP")
        else:
            print("Backpack is already upgraded.")

        print("(L)eave shop")
        print("-----------------------------------------------------")
        print(f"GP: {player['GP']}")
        choice = input("Your choice? ").lower()

        if choice == 'p':
            if player['pickaxe'] == 1 and player['GP'] >= 50:
                player['pickaxe'] = 2
                player['GP'] -= 50
                print("Congratulations! You can now mine silver!")
            elif player['pickaxe'] == 2 and player['GP'] >= 150:
                player['pickaxe'] = 3
                player['GP'] -= 150
                print("Congratulations! You can now mine gold!")
            else:
                print("Not enough GP or already max level.")
        elif choice == 'b':
            if player['backpack'] == 10 and player['GP'] >= 20:
                player['backpack'] = 12
                player['GP'] -= 20
                print("Backpack upgraded! You can now carry 12 items.")
            else:
                print("Not enough GP or backpack already upgraded.")
        elif choice == 'l':
            break
        else:
            print("Invalid choice. Please try again.")


def save_game():
    global game_map, fog, player, width, height
    game_data = {"player": player,
        "game_map": game_map,
        "fog": fog,
        "width": width,
        "height": height}
    with open("saved_game.json", "w") as f:
        json.dump(game_data, f)
    print("Game saved successfully.")

def load_game():
    global game_map, fog, player, width, height
    try:
        with open("saved_game.json", "r") as f:
            game_data = json.load(f)
        game_map = game_data["game_map"]
        fog = game_data["fog"]
        player = game_data["player"]
        width = game_data["width"]
        height = game_data["height"]
        print("Game loaded successfully.")
        return True
    except FileNotFoundError:
        print("No saved game found.")
        return False

# Main game loop
while True:
    if game_state == 'main':
        show_main_menu()
        choice = input("Your choice? ").lower()

        if choice == 'n':
            name = input("Greetings, miner! What is your name? ")
            print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
            initialize_game()
            player['name'] = name
            game_state = 'town' 
        
        elif choice == 'l':
            if load_game():
                game_state = 'town'

        elif choice == 'q':
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")

    elif game_state == 'town':
            show_town_menu(player)
            choice = input("Your choice? ").lower()

            if choice == 'i':
                print("----- Player Information -----")
                print(f"Name: {player['name']}")
                print(f"GP: {player['GP']}")
                #print(f"portal position: ( ({player['x']}, {player['y']})")
                #print(f"Pickaxe level: 1 (copper)")
                print("-" * 30)
                total_load = player['copper'] + player['silver'] + player['gold']
                print(f"Load: {total_load} / 10")
                print("-" * 30)
                print(f"GP: {player['GP']}")
                print(f"Steps taken: {player['steps']}")
                print("-" * 30)
                input("Press Enter to return to the menu...")
            elif choice == 'm':
                # Check that the map has been initialized
                if 'x' not in player or game_map == []:
                    print("Map not initialized yet.")
                else:
                    print_map(full=True)
            elif choice == 'e':
                enter_mine()
            elif choice == 'b':
                show_shop_menu()
            elif choice == 'v':
                save_game()
            else:
                print("Invalid choice. Please try again.")

            





        