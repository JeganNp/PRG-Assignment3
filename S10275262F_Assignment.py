''' Name : M Jegan
    Class : CICTP01
    StudentID : S10275262F
    Date : 10 August 2025
    Assignment : Sundrop Caves 

    Description:
    This program is a text-based mining and exploration game where the player must
    earn at least 500 GP to win. The player explores a mine, collects minerals, sells them,
    and can purchase upgrades (backpack, pickaxe, torch). The game includes saving/loading,
    a fog-of-war map system, portals, and a top score leaderboard.'''

''' - Reads the cave layout from Level1.txt
    - Saves/loads game state from saved_game.json
    - Stores top scores in top_scores.json
    '''

from random import randint 
import json 

#Game data
player  = {}   # All player state is stored in this dictionary
game_map = []  # Reads the Level1.txt
fog = []       # for the "?" and empty spaces after you mine finish

MAP_WIDTH = 0
MAP_HEIGHT = 0
TURNS_PER_DAY = 20
WIN_GP = 500
TORCH_PRICE = 50   

minerals = ['copper','silver','gold']
minerals_names = {"C" : "copper",'S' : 'silver' , 'G' : 'gold'}   # map tile -> mineral name
prices = {'copper' : (1,3), 'silver' : (5,8), 'gold' : (10,18)}   # This will make sure the amount of ore that you get is random.
pickaxe_price = [50, 150] # to upgrade pickaxe 


def show_intro():
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.\n")
    print("How quickly can you get the 500 GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")

show_intro()
def initialize_fog(height, width):  # Create a fog-of-war filled with '?'
    return [['?' for _ in range(width)] for _ in range(height)]

def vision_radius():                # Compute current vision radius 
    # 1 = normal 3x3, 2 = torch 5x5
    return 2 if player.get('torch') else 1

def clear_fog(fog, player, width, height):  # shows the space around the players position
    v = vision_radius()
    x, y = player['x'], player['y']
    for dy in range(-v, v + 1):
        for dx in range(-v, v + 1):
            nx = x + dx
            ny = y + dy
            if 0 <= ny < height and 0 <= nx < width:
                fog[ny][nx] = ''


def initialize_game():       # Loads the map from Level1.txt, create fog, and initialize the player dict.
    global game_map, fog, player, width, height
    # Load map as 2d List
    game_map = []
    with open("Level1.txt", "r") as f:
        for line in f:
            game_map.append(list(line.strip('\n')))
    height = len(game_map)
    width = len(game_map[0])

    fog = initialize_fog(height, width) 

    #player state
    player = {'name': '',
        'x': 0,
        'y': 0,
        'copper': 0,
        'silver': 0,
        'gold': 0,
        'GP': 0,
        'day': 1,
        'steps': 0,                 # steps taken today
        'total_steps' : 0,          # steps across all days (for leaderboard)
        'turns': TURNS_PER_DAY,
        'pickaxe': 1,
        'backpack': 10,
        'torch': False,}
    found_M = False
    for y in range(height):
        for x in range(width):
            if game_map[y][x] == 'M':
                player['x'] = x
                player['y'] = y
                player['spawn_mine_x'] = x
                player['spawn_mine_y'] = y
                player['portal_x'] = None
                player['portal_y'] = None
                found_M = True
                break
        if found_M:
            break
    clear_fog(fog, player, width, height)

initialize_game()    

def show_main_menu():
    """ Main menu loop: New game, Load game, View Top Scores, Quit.
    On 'n': starts the game, ask for name, then show town menu.
    """
    while True:
        print("\n--- Main Menu ----")
        print("(N)ew game")
        print("(L)oad saved game")
        print("View (T)op Scores")
        print("(Q)uit")
        print("------------------")
        choice = input("Your choice? ").lower()

        if choice == 'n':
            name = input("Greetings, miner! What is your name? ")
            initialize_game()
            player['name'] = name or "Anonymous"
            print(f"Pleased to meet you, {player['name']}. Welcome to Sundrop Town!")
            show_town_menu()

        elif choice == 'l':
            if load_game():
                show_town_menu()

        elif choice == 't':
             view_top_scores()
             input("Press Enter to return...")

        elif choice == 'q':
            print("Thanks for playing!")
            return  

        else:
            print("Invalid choice. Please try again.")
            continue

game_state = 'main'

def show_town_menu():
    """ Town hub loop: shop, info, map, enter mine, save, or quit to main menu.
    """
    while True:
        print(f"\nDAY {player['day']}")
        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        print("------------------------")
        choice = input("Your choice? ").lower()

        if choice == 'i':
            print("----- Player Information -----")
            print(f"Name: {player['name']}")
            print(f"GP: {player['GP']}")
            print("-" * 30)
            total_load = player['copper'] + player['silver'] + player['gold']
            print(f"Load: {total_load} / {player['backpack']}")
            print(f"Steps taken: {player['steps']}")
            print(f"Total steps: {player['total_steps']}")
            print("-" * 30)
            input("Press Enter to return...")
            continue

        elif choice == 'm':
            if 'x' not in player or not game_map:
                print("Map not initialized yet.")
            else:
                print_map(full=True)
            input("Press Enter to return...")
            continue

        elif choice == 'e':
            enter_mine()   # when it returns, we’re still in this loop
            continue

        elif choice == 'b':
            show_shop_menu()  
            continue

        elif choice == 'v':
            save_game()
            input("Saved. Press Enter to return...")
            continue

        elif choice == 'q':
            return   # go back to main menu cleanly

        else:
            print("Invalid choice. Please try again.")
            continue



def print_map(full=False):
    global game_map, fog, player, width, height

    if full:
        start_x, end_x = 0, width
        start_y, end_y = 0, height
    else:
        v = vision_radius()
        start_x = max(0, player['x'] - v)
        end_x   = min(width, player['x'] + v + 1)
        start_y = max(0, player['y'] - v)
        end_y   = min(height, player['y'] + v + 1)

    span = end_x - start_x
    print("+" + "-" * span + "+")
    for y in range(start_y, end_y):
        row_chars = []
        for x in range(start_x, end_x):
            if player['x'] == x and player['y'] == y:
                ch = 'M'
            elif fog[y][x] == '?':
                ch = '?'
            else:
                ch = game_map[y][x]  # keep whatever is on the map: ' ', 'C', 'S', 'G', 'P', 'T', etc.
            row_chars.append(ch)
        print("|" + "".join(row_chars) + "|")
    print("+" + "-" * span + "+")


def enter_mine():
    global game_map, fog, player, width, height
    """
    Enter the mine. Handles spawn logic, movement, mining, portals,
    auto-teleport on exhaustion/full backpack, and winning condition.
    """
    
    if player.get('portal_x') is not None and player.get('portal_y') is not None:
        px, py = player['portal_x'], player['portal_y']
        if 0 <= px < width and 0 <= py < height and game_map[py][px] == 'P':
            player['x'], player['y'] = px, py
            game_map[py][px] = ' '  
            player['portal_x'] = None
            player['portal_y'] = None
            clear_fog(fog, player, width, height)
    else:
        
        if 'spawn_mine_x' in player and 'spawn_mine_y' in player:
            player['x'], player['y'] = player['spawn_mine_x'], player['spawn_mine_y']
            clear_fog(fog, player, width, height)


    def teleport_to_town(reason="manual", place_portal=True):
    # Only drop/record a portal if requested
        if place_portal:
            game_map[player['y']][player['x']] = 'P'
            player['portal_x'] = player['x']
            player['portal_y'] = player['y']

        # Move to town 'T'
        found_town_portal = False
        for yy in range(height):
            for xx in range(width):
                if game_map[yy][xx] == 'T':
                    player['x'], player['y'] = xx, yy
                    found_town_portal = True
                    break
            if found_town_portal:
                break

        if not found_town_portal:
            print("ERROR: No town portal (T) found on the map!")
            return "error"

        # Sell all carried ores for randomized prices
        for mineral in ['copper', 'silver', 'gold']:
            amount = player[mineral]
            if amount > 0:
                lo, hi = prices[mineral]
                total_gp = sum(randint(lo, hi) for _ in range(amount))
                print(f"Sold {amount} {mineral} for {total_gp} GP.")
                player['GP'] += total_gp
                player[mineral] = 0
            else:
                print(f"You have no {mineral} to sell.")
        print(f"You now have {player['GP']} GP!")

        # Check win condition
        if player['GP'] >= WIN_GP:
            print("Congratulations! You've earned enough GP to retire!")
            print(f"You finished in {player['day']} days with {player['total_steps']} total steps "
                f"(today: {player['steps']}).")
            try:
                record_top_score()
                print("Top score saved!")
            except Exception as e:
                print("Failed to save top score:", e)
            show_main_menu()
            return "main"

        # End-of-day reset
        player['day'] += 1
        player['turns'] = TURNS_PER_DAY
        player['steps'] = 0
        return "town"



    def print_local_viewport():
        v = vision_radius()
        span = (2 * v) + 1
        print(f"\nDAY {player['day']}")
        print("+" + "-" * span + "+")
        for dy in range(-v, v + 1):
            row_chars = []
            for dx in range(-v, v + 1):
                nx = player['x'] + dx
                ny = player['y'] + dy
                if 0 <= nx < width and 0 <= ny < height:
                    ch = 'M' if (nx == player['x'] and ny == player['y']) else game_map[ny][nx]
                else:
                    ch = '#'
                row_chars.append(ch)
            print("|" + "".join(row_chars) + "|")
        print("+" + "-" * span + "+")
    # Which ores each pickaxe level can mine
    allowed = {
        1: ['copper'],
        2: ['copper', 'silver'],
        3: ['copper', 'silver', 'gold']}
    
    # ----- Mining/Movement loop -----
    while True:
        print_local_viewport()
        total_load = player['copper'] + player['silver'] + player['gold']
        print(f"Turns left: {player['turns']}   Load: {total_load} / {player['backpack']}   Steps: {player['steps']}")
        print("(WASD) to move")
        print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")
        action = input("Action? ").lower()

        # Non-movement actions
        if action == 'm':
            print_map(full=True)
            input("Press Enter to return to mining...")  
            continue
        elif action == 'i':
            print("----- Player Information -----")
            print(f"Name: {player['name']}")
            print(f"GP: {player['GP']}")
            total_load = player['copper'] + player['silver'] + player['gold']
            print(f"Load: {total_load} / {player['backpack']}")
            print(f"Steps taken: {player['steps']}")
            print("-" * 30)
            input("Press Enter to continue...")
            continue
        elif action == 'p':
            print("You used the portal to return to town.")
            teleport_to_town("manual")
            return
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

        # Keep moves inside the map
        if 0 <= new_x < width and 0 <= new_y < height:
            target = game_map[new_y][new_x]

            # Walls block
            if target == '#':
                print("You bumped into a wall!")
                continue

            # Step onto Town tile: return to town without dropping a portal
            if target == 'T':
                player['x'] = new_x
                player['y'] = new_y
                player['steps'] += 1
                player['total_steps'] += 1
                player['turns'] -= 1
                clear_fog(fog, player, width, height)
                teleport_to_town("tunnel", place_portal=False)
                return

            # Block stepping onto any mineral if backpack is full
            if target in minerals_names:
                total_load = player['copper'] + player['silver'] + player['gold']
                if total_load >= player['backpack']:
                    print("You can't carry any more, so you can't go that way.")
                    continue

            # Block ore you can't mine yet
            if target in minerals_names:
                mineral = minerals_names[target]
                if mineral not in allowed[player['pickaxe']]:
                    print(f"Your pickaxe can't mine {mineral} yet. The ore blocks your way.")
                    continue

            
            player['x'] = new_x
            player['y'] = new_y
            player['steps'] += 1
            player['total_steps'] += 1
            player['turns'] -= 1
            clear_fog(fog, player, width, height)

            # === Auto-teleport if turns run out ===
            if player['turns'] <= 0:
                print("You are exhausted. You place your portal stone and zap back to town.")
                teleport_to_town("exhausted")
                return


            # If we stepped onto mineable ore, do the mining logic
            if target in minerals_names:
                mineral = minerals_names[target]

                total_load = player['copper'] + player['silver'] + player['gold']
                if total_load < player['backpack']:
                    mining_ranges = {
                        'copper': (1, 5),
                        'silver': (1, 3),
                        'gold': (1, 2)
                    }
                    mined_amount = randint(*mining_ranges[mineral])
                    current_load = player['copper'] + player['silver'] + player['gold']
                    space_left = player['backpack'] - current_load
                    mined_amount = min(mined_amount, space_left)

                    if mined_amount > 0:
                        player[mineral] += mined_amount
                        game_map[new_y][new_x] = ' '  # ore removed -> now passable
                        print(f"You mined {mined_amount} {mineral}!")
                        print(f"Current load: {current_load + mined_amount}/{player['backpack']}")
                    else:
                        print("Your backpack is full! Can't carry more.")

                    # Auto-teleport if backpack is full after mining
                    total_load = player['copper'] + player['silver'] + player['gold']
                    if total_load >= player['backpack']:
                        print("Your backpack is full. You place your portal stone and zap back to town.")
                        teleport_to_town("full")
                        return


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
        print(f"(B)ackpack upgrade to carry {player['backpack'] + 2} items for {player['backpack'] * 2} GP")
        if player['pickaxe'] == 1:
            print("(P)ickaxe upgrade to Level 2 to mine silver ore for 50 GP")
        elif player['pickaxe'] == 2:
            print("(P)ickaxe upgrade to Level 3 to mine gold ore for 150 GP")
        else:
            print("Pickaxe is already max level.")
        print(f"(T)orch for brighter light radius for {TORCH_PRICE} GP" + (" (owned)" if player.get('torch') else ""))
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
            upgrade_cost = player['backpack'] * 2
            if player['GP'] >= upgrade_cost:
                player['backpack'] += 2
                player['GP'] -= upgrade_cost
                print(f"Congratulations! You can now carry {player['backpack']} items!")
            else:
                print("Not enough GP for the backpack upgrade.")
            
        elif choice == 't':
            if player.get('torch'):
                print("You already own a torch.")
            elif player['GP'] >= TORCH_PRICE:
                player['GP'] -= TORCH_PRICE
                player['torch'] = True
                print("You bought a torch! Your vision radius is bigger now.")
            else:
                print("Not enough GP for the torch.")
        elif choice == 'l':
            return
        else:
            print("Invalid choice. Please try again.")


def save_game():
    """
    Save the current game state to 'saved_game.json'.
    """
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
    """
    Load the game state from 'saved_game.json' if it exists.

    Returns:
        bool: True if load succeeded, else False.
    """
    global game_map, fog, player, width, height
    try:
        with open("saved_game.json", "r") as f:
            game_data = json.load(f)
            game_map = game_data["game_map"]
            fog = game_data["fog"]
            player = game_data["player"]
            # Prompt for name if missing
            if 'name' not in player or not player['name']:
                player['name'] = input("Enter your name: ") or "Anonymous"
            width = game_data["width"]
            height = game_data["height"]
            # Ensure new fields exist for older saves
            if 'torch' not in player: 
                player['torch'] = False
                
            # Ensure spawn_mine exists
            if 'spawn_mine_x' not in player or 'spawn_mine_y' not in player:
                for yy in range(height):
                    for xx in range(width):
                        if game_map[yy][xx] == 'M':
                            player['spawn_mine_x'] = xx
                            player['spawn_mine_y'] = yy

                            break
            if 'total_steps' not in player:     
                player['total_steps'] = 0

            # Rebuild portal coords if not stored
            if player.get('portal_x') is None or player.get('portal_y') is None:
                foundP = False
                for yy in range(height):
                    for xx in range(width):
                        if game_map[yy][xx] == 'P':
                            player['portal_x'] = xx
                            player['portal_y'] = yy
                            foundP = True
                            break
                    if foundP:
                        break
            # ----------------------------------------

            print("Game loaded successfully.")
            return True
    except FileNotFoundError:
        print("No saved game found.")
        return False


def record_top_score():
    """
    Append current run to the top scores file and keep only the best five.
    Ranking: fewest days -> fewest total steps -> highest GP.
    """
    score_entry = {"name" : player["name"],
                "days" : player["day"],
                "steps" : player["total_steps"],
                "GP" : player["GP"]} 
    try: 
        with open("top_scores.json", "r") as f:
            scores = json.load(f)
    except FileNotFoundError:
        scores = []

    scores.append(score_entry)
    scores.sort(key=lambda x: (x["days"], x["steps"], -x["GP"]))
    scores = scores[:5]

    with open("top_scores.json", "w") as f:
        json.dump(scores, f)

def view_top_scores():
    """
    Print the top 5 leaderboard from 'top_scores.json' if it exists.
    """
    print("\n--- Top 5 Scores ---")
    try:
        with open("top_scores.json", "r") as f:
            scores = json.load(f)
            for i, s in enumerate(scores, 1):
                print(f"{i}. {s['name']} - Days: {s['days']} | Steps: {s['steps']} | GP: {s['GP']}")
    except FileNotFoundError:
        print("No top scores yet!")

# Main game loop
if __name__ == "__main__":
    show_main_menu()

            





        