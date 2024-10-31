import curses
import random
import time
import math

HIGH_SCORES_FILE = "high_scores.txt"

# Function to load high scores from a file
def load_high_scores():
    try:
        with open(HIGH_SCORES_FILE, "r") as file:
            high_scores = []
            for line in file.readlines():
                parts = line.strip().split(" ", 2)
                if len(parts) == 3:
                    score, name, level = parts
                    try:
                        high_scores.append((int(score), name, int(level)))
                    except ValueError:
                        continue
            return high_scores
    except FileNotFoundError:
        return []

# Function to save high scores to a file
def save_high_scores(high_scores):
    with open(HIGH_SCORES_FILE, "w") as file:
        for score, name, level in high_scores:
            file.write(f"{score} {name} {level}\n")

# Function to update the high score list with a new score
def update_high_scores(new_score, name, level):
    high_scores = load_high_scores()
    if len(high_scores) < 10 or new_score > high_scores[-1][0]:
        high_scores.append((new_score, name, level))
        high_scores = sorted(high_scores, key=lambda x: x[0], reverse=True)[:10]
        save_high_scores(high_scores)

def display_high_scores(stdscr):
    high_scores = load_high_scores()
    sh, sw = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(sh // 2 - 7, sw // 2 - 30, " _                   _           ____                      _ ")
    stdscr.addstr(sh // 2 - 6, sw // 2 - 30, "| |    ___  __ _  __| | ___ _ __| __ )  ___   __ _ _ __ __| |")
    stdscr.addstr(sh // 2 - 5, sw // 2 - 30, "| |   / _ \/ _` |/ _` |/ _ \ '__|  _ \ / _ \ / _` | '__/ _` |")
    stdscr.addstr(sh // 2 - 4, sw // 2 - 30, "| |__|  __/ (_| | (_| |  __/ |  | |_) | (_) | (_| | | | (_| |")
    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, "|_____\___|\__,_|\__,_|\___|_|  |____/ \___/ \__,_|_|  \__,_|")
    stdscr.addstr(sh // 2, sw // 2 - 10, "Top 10 High Scores")

    for i, (score, name, level) in enumerate(high_scores):
        stdscr.addstr(sh // 2 + i + 1, sw // 2 - 10, f"{i + 1}. {name} - {score} (Level {level})")

    stdscr.addstr(sh // 2 + 13, sw // 2 - 10, "Press Enter to return to the main menu")
    stdscr.refresh()

    # Wait for "Enter" to return to the main menu
    while True:
        key = stdscr.getch()
        if key == ord("\n") or key == curses.KEY_ENTER:
            break

def draw_structure(stdscr, x, y):
    structure = [
        "  /\  ",
        " /  \\",
        "/____\\",
        "| [] |",
        "|____|"
    ]
    for i, line in enumerate(structure):
        stdscr.addstr(y + i, x, line)

def draw_grass(stdscr, x, y):
    grass_type = random.choice([
        ('⠀⠀⣴⣄⠀⢰⡏⣸⠀⣴⠏', '⠀⢠⣿⠙⣦⡟⢠⣿⣿⢏⡀'),
        ('⠀⠀⠀⠀⣿⣇⠀⠀⢠⣧⠀⠀⢀⣀', '⠰⣶⣀⠀⠀⣿⢿⡄⣸⡿⣿⣤⡶⣿⠏'),
        ('⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣇⠀⣀⠀⠀⢀⣴⡶⣩⠿⠋⠁', '⠀⠀⠠⢤⣤⣄⡀⠀⢀⡿⣿⣼⣻⢁⣴⠟⢥⣿⠟⠁⠀⠀'),
        ('⠀⠀  ⠀⣰⠇       ', '⣄⠀⢠⣾⡏⢀⣠⣾⠆')
    ])
    for i, line in enumerate(grass_type):
        stdscr.addstr(y - 1 + i, x, line)

def draw_mountains(stdscr, x, y):
    mountain = [
        "    .                  .-.    .  _   *     _   .",
        "           *          /   \     ((       _/ \       *    .",
        "         _    .   .--'/\_ \     `      /    \  *    ___",
        "     *  / \_    _/ ^      ' __        /\/\  /\  __/   \ *",
        "       /    \  /    .'   _/  /  \  *' /    \/  \/ .`'\_/\   .",
        "  .   /\/\  /\/ :' __  ^/  ^/    `--./.'  ^  `-.\ _    _:\ _",
        "     /    \/  \  _/  \-' __/.' ^ _   \_   .'\   _/ \ .  __/",
        "   /\  .-   `. \/     \ / -.   _/ \ -. `_/   \ /    `._/  ^  ",
        "  /  `-.__ ^   / .-'.--'    . /    `--./ .-'  `-.  `-. `.  -  `.",
        "@/        `.  / /      `-.   /  .-'   / .   .'   \    \  \  .-  \%"
    ]
    for i, line in enumerate(mountain):
        if 0 <= y + i < stdscr.getmaxyx()[0]:  # Ensure within screen bounds
            try:
                stdscr.addstr(y + i, int(x), line)
            except curses.error:
                pass

def game_loop(stdscr, lives, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier):
    # Setup screen
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Non-blocking input

    # Get screen dimensions
    sh, sw = stdscr.getmaxyx()  # Screen height and width
    w = curses.newwin(sh, sw, 0, 0)  # Create a new window for the game

    # Player starting position and state
    player_x = sw // 6
    player_y = sh - 4  # Start player on the ground level
    player_width = 3  # Width of the player character
    player_height = 3  # Height of the player character
    velocity = 0  # Upward velocity for jumping
    is_jumping = False

    # Obstacles
    obstacles = []
    obstacle_gap = 30  # Increase gap for larger obstacles

    base_obstacle_speed = 2  # Base speed for consistent gameplay
    obstacle_speed = base_obstacle_speed * obstacle_speed_multiplier

    # Grass structures
    grass_structures = []

    # Additional structures
    structures = []

    # Stars
    stars = []
    star_speed = 0.5  # Star scroll speed, slower for parallax effect
    max_stars = 90  # Maximum number of stars on screen at a time

    # Mountains
    mountains = []
    mountain_speed = 0.8  # Mountain scroll speed, slightly faster than stars
    mountain_y = sh - 10  # Position of the mountains vertically at ground level

    # Create initial stars
    for _ in range(max_stars):
        star_x = random.randint(0, sw - 1)
        star_y = random.randint(0, sh - 1)
        stars.append([star_x, star_y])

    # Create initial mountains (only on levels divisible by 3)
    if level_number % 3 == 0:
        for i in range(0, sw, 40):
            mountains.append([i, mountain_y])

    # Movement controls
    move_left = False
    move_right = False
    hold_position = False

    # Game loop timing control
    last_update_time = time.time()

    # Initial render before entering main loop
    w.clear()
    w.border(0)

    # Render initial stars
    for star in stars:
        if 0 <= int(star[0]) < sw and 0 <= int(star[1]) < sh:
            try:
                w.addstr(int(star[1]), int(star[0]), "*")
            except curses.error:
                pass

    # Render initial grass structures
    for grass in grass_structures:
        if 0 <= grass[0] < sw:
            for i, line in enumerate(grass[3]):
                try:
                    w.addstr(grass[1] - 1 + i, grass[0], line)
                except curses.error:
                    pass

    # Render initial player position
    try:
        w.addstr(int(player_y), player_x, " 0 ")
        w.addstr(int(player_y) + 1, player_x, "/|\\")
        w.addstr(int(player_y) + 2, player_x, "/| ")
    except curses.error:
        pass

    w.refresh()

    # Game loop
    while True:
        # Capture input without halting game loop
        key = w.getch()

        # Key press logic for setting movement direction
        if key in [ord(" "), ord("w")]:  # Space bar or "W" to jump
            if not is_jumping:  # Only allow jumping if on the ground
                velocity = -2  # Initial jump velocity
                is_jumping = True
        elif key == ord("a"):  # "A" key for moving left
            move_left = True
            move_right = False
            hold_position = False
        elif key == ord("d"):  # "D" key for moving right
            move_right = True
            move_left = False
            hold_position = False
        elif key in [ord("s"), curses.KEY_DOWN]:  # "S" key or down arrow to hold position
            hold_position = True
            move_left = move_right = False
        elif key == -1:  # No input
            move_left = move_right = hold_position = False

        # Time-based game loop update
        current_time = time.time()
        if current_time - last_update_time > 0.05:  # Update every 50 ms
            # Apply gravity to the player at all times
            velocity += 0.2  # Gravity effect
            player_y += velocity

            # Ensure player stays within vertical bounds
            if player_y > sh - player_height - 1:  # Ground level for the player
                player_y = sh - player_height - 1
                velocity = 0
                is_jumping = False
            elif player_y < 0:  # Prevent player from going above the screen
                player_y = 0
                velocity = 0

            # Apply horizontal movement
            if move_left:
                player_x -= 1
                if player_x < 0:  # Lose a life if player moves off the left side
                    return True, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier  # Lose a life without resetting score
            elif move_right:
                player_x = min(sw - player_width, player_x + 1)  # Ensure player stays in bounds

            # Auto-scroll obstacles
            if len(obstacles) == 0 or (obstacles[-1][0] < sw - random.randint(obstacle_gap // 2, obstacle_gap * 1.5) and random.random() < 0.7):
                # Randomized gap between obstacles using random.randint
                # More frequent spawning (70% chance)
                spawn_count = random.randint(1, math.ceil(obstacle_count_multiplier) + 1)  # Randomly decide how many obstacles to spawn
                for _ in range(spawn_count):
                    obstacle_y = random.randint(2, sh - 5)  # Random vertical position, avoiding edges
                    rand_value = random.random()
                    if rand_value < 0.5:
                        new_obstacle = [sw - 1, obstacle_y, '2x2']  # Add 2x2 obstacle at rightmost edge
                    elif rand_value < 0.8:
                        new_obstacle = [sw - 1, obstacle_y, '5x3']  # Add 5x3 obstacle at rightmost edge
                    else:
                        new_obstacle = [sw - 1, obstacle_y, 'new']  # Add new obstacle at rightmost edge

                    # Ensure obstacle does not spawn within 5 characters of any other obstacle or 2 characters of a structure
                    if (not any(abs(new_obstacle[0] - structure[0]) < 2 for structure in structures) and
                        not any(abs(new_obstacle[0] - obs[0]) < 5 for obs in obstacles)):
                        obstacles.append(new_obstacle)

            # Generate structures (only on levels 2 and after)
            if level_number >= 2:
                structure_spawn_chance = 0.01 if level_number == 2 else min(0.01 + 0.05 * (level_number - 3), 1.0)
                if len(structures) == 0 or (structures[-1][0] < sw - 40 and random.random() < structure_spawn_chance):
                    structures.append([sw, sh - 6])  # Spawn offscreen to the right

            # Generate grass structures (simplified for troubleshooting)
            if len(grass_structures) == 0 or grass_structures[-1][0] < sw - (obstacle_gap * 0.25):
                if random.random() < 0.6:  # 60% chance to add a grass structure
                    grass_y = sh - 1  # Grass is pinned to the ground
                    grass_height = 2
                    grass_type = random.choice([
                        ('⠀⠀⣴⣄⠀⢰⡏⣸⠀⣴⠏', '⠀⢠⣿⠙⣦⡟⢠⣿⣿⢏⡀'),
                        ('⠀⠀⠀⠀⣿⣇⠀⠀⢠⣧⠀⠀⢀⣀', '⠰⣶⣀⠀⠀⣿⢿⡄⣸⡿⣿⣤⡶⣿⠏'),
                        ('⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣇⠀⣀⠀⠀⢀⣴⡶⣩⠿⠋⠁', '⠀⠀⠠⢤⣤⣄⡀⠀⢀⡿⣿⣼⣻⢁⣴⠟⢥⣿⠟⠁⠀⠀'),
                        ('⠀⠀  ⠀⣰⠇       ', '⣄⠀⢠⣾⡏⢀⣠⣾⠆')
                    ])
                    grass_structures.append([sw - 6, grass_y, grass_height, grass_type])

            # Move stars leftward
            new_stars = []
            for star in stars:
                star[0] -= star_speed  # Move star left by star_speed
                if 0 <= star[0] < sw and 0 <= star[1] < sh:  # Ensure star fits on screen
                    new_stars.append(star)
                else:
                    # Star has moved off-screen, respawn on the right edge
                    new_stars.append([sw - 1, random.randint(0, sh - 1)])

            # Occasionally add a new star to maintain density
            if len(new_stars) < max_stars:
                new_stars.append([sw - 1, random.randint(0, sh - 1)])

            stars = new_stars

            # Move mountains leftward (only if level is divisible by 3)
            if level_number % 3 == 0:
                new_mountains = []
                for mountain in mountains:
                    mountain[0] -= mountain_speed  # Move mountain left by mountain_speed
                    if mountain[0] > -40:  # Ensure mountain fits on screen
                        new_mountains.append(mountain)
                    else:
                        # Mountain has moved off-screen, respawn on the right edge
                        new_mountains.append([sw - 1, mountain_y])
                mountains = new_mountains

            # Move obstacles, structures, and grass leftward and check for collisions
            new_obstacles = []
            new_grass_structures = []
            new_structures = []

            for obs in obstacles:
                obs[0] -= int(obstacle_speed)  # Ensure obstacle position is always an integer

                # Check for collisions with the obstacle
                obs_width, obs_height = (5, 3) if obs[2] == '5x3' else (2, 2)
                if ((player_x < obs[0] + obs_width and player_x + player_width > obs[0]) and
                    (player_y < obs[1] + obs_height and player_y + player_height > obs[1])):
                    return True, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier  # Lose a life upon collision

                if obs[0] > 0:
                    new_obstacles.append(obs)

            for structure in structures:
                structure[0] -= int(obstacle_speed)

                # Check for collisions with the structure
                structure_width = 6  # Width of the structure
                structure_height = 5  # Height of the structure
                if ((player_x < structure[0] + structure_width and player_x + player_width > structure[0]) and
                    (player_y + player_height > structure[1] and player_y < structure[1] + structure_height)):
                    # Collision from the left or right of the structure
                    if player_x + player_width > structure[0] and player_x < structure[0] + structure_width // 2:  # Collision from the left
                        player_x = structure[0] - player_width
                        move_right = False  # Prevent moving right through the structure
                    elif player_x < structure[0] + structure_width and player_x > structure[0] + structure_width // 2:  # Collision from the right
                        player_x = structure[0] + structure_width
                        move_left = False  # Prevent moving left through the structure
                    velocity = 0  # Stop vertical movement
                    is_jumping = False

                # Stop vertical movement if on top of the structure
                if (player_y + player_height == structure[1] and
                    player_x + player_width > structure[0] and player_x < structure[0] + structure_width):
                    player_y = structure[1] - player_height
                    velocity = 0
                    is_jumping = False

                if structure[0] > 0:
                    new_structures.append(structure)

            for grass in grass_structures:
                grass[0] -= int(obstacle_speed)
                if grass[0] > 0:
                    new_grass_structures.append(grass)

            obstacles = new_obstacles
            structures = new_structures
            grass_structures = new_grass_structures

            # Rendering
            w.clear()
            w.border(0)

            # Render stars
            for star in stars:
                if 0 <= int(star[0]) < sw and 0 <= int(star[1]) < sh:  # Ensure star fits on screen
                    try:
                        w.addstr(int(star[1]), int(star[0]), "*")
                    except curses.error:
                        pass

            # Render mountains (only if level is divisible by 3)
            if level_number % 3 == 0:
                for mountain in mountains:
                    draw_mountains(w, mountain[0], mountain[1])

            # Render grass structures (before obstacles and player)
            for grass in grass_structures:
                if 0 <= grass[0] < sw:
                    for i, line in enumerate(grass[3]):
                        try:
                            w.addstr(grass[1] - 1 + i, grass[0], line)
                        except curses.error:
                            pass

            # Render structures
            for structure in structures:
                draw_structure(w, structure[0], structure[1])

            # Render obstacles
            for obs in obstacles:
                if obs[2] == '5x3':
                    if 0 <= obs[1] < sh - 3:  # Ensure obstacle fits on screen
                        try:
                            w.addstr(obs[1], int(obs[0]), "./-\\. ")
                            w.addstr(obs[1] + 1, int(obs[0]), "< 8 >")
                            w.addstr(obs[1] + 2, int(obs[0]), "^\-/^")
                        except curses.error:
                            pass
                elif obs[2] == '2x2':
                    if 0 <= obs[1] < sh - 1:  # Ensure obstacle fits on screen
                        try:
                            w.addstr(obs[1], int(obs[0]), "\\/")
                            w.addstr(obs[1] + 1, int(obs[0]), "/\\")
                        except curses.error:
                            pass
                elif obs[2] == 'new':
                    pass

            # Render player (after obstacles and grass to be in front)
            if 0 <= player_y < sh - player_height:
                try:
                    w.addstr(int(player_y), player_x, " 0 ")
                    w.addstr(int(player_y) + 1, player_x, "/|\\")
                    w.addstr(int(player_y) + 2, player_x, "/| ")
                except curses.error:
                    pass

            # Update and render score
            score += 1
            try:
                w.addstr(0, sw // 2 - 5, f"Score: {score}")
                # Update and render high score
                if score > high_score:
                    high_score = score
                w.addstr(0, sw - 20, f"High Score: {high_score}")
                # Display level number
                w.addstr(0, 2, f"Level: {level_number}")
                # Display extra lives remaining (hearts)
                extra_lives_display = " ".join(["<3"] * (lives - 1))
                w.addstr(1, sw // 2 - 10, f"Extra lives: {extra_lives_display}")
            except curses.error:
                pass


            # Refresh screen
            w.refresh()

            # Update the last update time
            last_update_time = current_time

            # Check for level-up
            if score % 500 == 0 and score != 0:
                obstacle_speed_multiplier *= 1.2  # Increase obstacle speed by 20%
                obstacle_count_multiplier *= 1.3  # Increase obstacle count by 30%
                level_number += 1  # Increase level number
                # Display Level Up screen
                w.clear()
                try:
                    w.addstr(sh // 2 - 5, sw // 2 - 30, " _   _ _              _   _                   __              ")
                    w.addstr(sh // 2 - 4, sw // 2 - 30, "| \ | (_) ___ ___    | |_(_)_ __ ___   ___   / _| ___  _ __   ")
                    w.addstr(sh // 2 - 3, sw // 2 - 30, "|  \| | |/ __/ _ \   | __| | '_ ` _ \ / _ \ | |_ / _ \| '__|  ")
                    w.addstr(sh // 2 - 2, sw // 2 - 30, "| |\  | | (_|  __/_  | |_| | | | | | |  __/ |  _| (_) | |     ")
                    w.addstr(sh // 2 - 1, sw // 2 - 30, "|_| \_|_|\___\___( )  \__|_|_| |_| |_|\___| |_|  \___/|_|     ")
                    w.addstr(sh // 2, sw // 2 - 30, "  __ _ _ __   ___|/ |_| |__   ___ _ __    ___  _ __   ___     ")
                    w.addstr(sh // 2 + 1, sw // 2 - 30, " / _` | '_ \ / _ \| __| '_ \ / _ \ '__|  / _ \| '_ \ / _ \    ")
                    w.addstr(sh // 2 + 2, sw // 2 - 30, "| (_| | | | | (_) | |_| | | |  __/ |    | (_) | | | |  __/_ _ ")
                    w.addstr(sh // 2 + 3, sw // 2 - 30, " \__,_|_| |_|\___/ \__|_| |_|\___|_|     \___/|_| |_|\___(_|_)")
                    w.addstr(sh // 2 + 5, sw // 2 - 10, f"Level {level_number} - Press Enter to continue")
                    w.refresh()
                except curses.error:
                    pass
                while True:
                    key = w.getch()
                    if key == ord("\n") or key == curses.KEY_ENTER:
                        break




def main(stdscr):
    sh, sw = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(sh // 2 - 7, sw // 2 - 25, "                               _         ")
    stdscr.addstr(sh // 2 - 6, sw // 2 - 25, "  ___  _ __   ___   _ __ _   _| | ___    ")
    stdscr.addstr(sh // 2 - 5, sw // 2 - 25, " / _ \| '_ \ / _ \ | '__| | | | |/ _ \   ")
    stdscr.addstr(sh // 2 - 4, sw // 2 - 25, "| (_) | | | |  __/ | |  | |_| | |  __/_  ")
    stdscr.addstr(sh // 2 - 3, sw // 2 - 25, " \___/|_| |_|\___| |_|   \__,_|_|\___(_) ")
    stdscr.addstr(sh // 2 - 2, sw // 2 - 25, "     _             _     ____ ___ _____  ")
    stdscr.addstr(sh // 2 - 1, sw // 2 - 25, "  __| | ___  _ __ | |_  |  _ \_ _| ____| ")
    stdscr.addstr(sh // 2, sw // 2 - 25, " / _` |/ _ \| '_ \| __| | | | | ||  _|   ")
    stdscr.addstr(sh // 2 + 1, sw // 2 - 25, "| (_| | (_) | | | | |_  | |_| | || |___  ")
    stdscr.addstr(sh // 2 + 2, sw // 2 - 25, " \__,_|\___/|_| |_|\__| |____/___|_____| ")

    # Add a box with game controls on the title screen
    controls_start_y = sh // 2 - 5
    controls_start_x = sw // 2 + 20
    stdscr.addstr(controls_start_y, controls_start_x, "+------------------+")
    stdscr.addstr(controls_start_y + 1, controls_start_x, "|  Game Controls   |")
    stdscr.addstr(controls_start_y + 2, controls_start_x, "|------------------|")
    stdscr.addstr(controls_start_y + 3, controls_start_x, "| SPACE or W: Jump |")
    stdscr.addstr(controls_start_y + 4, controls_start_x, "| A: Move Left     |")
    stdscr.addstr(controls_start_y + 5, controls_start_x, "| D: Move Right    |")
    stdscr.addstr(controls_start_y + 6, controls_start_x, "| S: Hold Position |")
    stdscr.addstr(controls_start_y + 7, controls_start_x, "+------------------+")

    stdscr.addstr(sh // 2 + 4, sw // 2 - 10, "Press Enter to start")
    stdscr.refresh()

    # Wait for "Enter" to start the game
    while True:
        key = stdscr.getch()
        if key == ord("\n") or key == curses.KEY_ENTER:
            break

    high_score = 0  # Track high score across games

    while True:
        lives = 4  # Start with 4 lives, including the current life
        score = 0  # Reset score when starting a new game
        obstacle_speed_multiplier = 1.0  # Start with base obstacle speed
        level_number = 1  # Start at level 1
        obstacle_count_multiplier = 1.0  # Start with base obstacle count

        while lives > 0:
            lost_life, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier = game_loop(
                stdscr, lives, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier)

            if lost_life:
                lives -= 1
                if lives == 1:
                    # Display "Second-to-Last Life" screen
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 5, sw // 2 - 30, " _        _    ____ _____   _     ___ _____ _____ _ ")
                    stdscr.addstr(sh // 2 - 4, sw // 2 - 30, "| |      / \  / ___|_   _| | |   |_ _|  ___| ____| |")
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, "| |     / _ \ \___ \ | |   | |    | || |_  |  _| | |")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "| |___ / ___ \ ___) || |   | |___ | ||  _| | |___|_|")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "|_____/_/   \_\____/ |_|   |_____|___|_|   |_____(_)")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 10, "Press Enter to continue")
                    stdscr.refresh()

                    # Wait for "Enter" to continue
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break
                elif lives > 1:
                    # Display regular "Life Lost" screen if more than one life remains
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, " _____ _           _     _                _        ")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "|_   _| |__   __ _| |_  | |__  _   _ _ __| |_      ")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "  | | | '_ \\ / _` | __| | '_ \\| | | | '__| __|     ")
                    stdscr.addstr(sh // 2, sw // 2 - 30, "  | | | | | | (_| | |_  | | | | |_| | |  | |_ _ _   ")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 30, " _|_| |_| |_|\\__,_|\\__| |_| |_|\\__,_|_|  \\__(_|_)  ")
                    stdscr.addstr(sh // 2 + 2, sw // 2 - 30, "|_ _| | | ___  ___| |_    __ _  | (_)/ _| ___       ")
                    stdscr.addstr(sh // 2 + 3, sw // 2 - 30, " | |  | |/ _ \\/ __| __|  / _` | | | | |_ / _ \\      ")
                    stdscr.addstr(sh // 2 + 4, sw // 2 - 30, " | |  | | (_) \\__ \\ |_  | (_| | | | |  _|  __/     ")
                    stdscr.addstr(sh // 2 + 5, sw // 2 - 30, "|___| |_|\\___/|___/\\__|  \\__,_| |_|_|_|  \\___|      ")
                    stdscr.addstr(sh // 2 + 6, sw // 2 - 10, f"Lives remaining: {lives}")
                    stdscr.addstr(sh // 2 + 8, sw // 2 - 10, "Press Enter to continue")
                    stdscr.refresh()


                    # Wait for "Enter" to continue with one less life
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break

                if lives == 0:
                    # Show Game Over screen if no lives remain
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 7, sw // 2 - 30, "     _     _ _             _                _                            ")
                    stdscr.addstr(sh // 2 - 6, sw // 2 - 30, " ___| |__ (_) |_        __| | ___  __ _  __| |                           ")
                    stdscr.addstr(sh // 2 - 5, sw // 2 - 30, "/ __| '_ \| | __|      / _` |/ _ \/ _` |/ _` |                           ")
                    stdscr.addstr(sh // 2 - 4, sw // 2 - 30, "\__ \ | | | | |_ _ _  | (_| |  __/ (_| | (_| |                           ")
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, "|___/_| |_|_|\__(_|_)  \__,_|\___|\__,_|\__,_|                           ")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "       _                    _      ___   _      _         _              ")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "  __ _| |_ __ ___  __ _  __| |_   |__ \ | | ___| |_ ___  | |_ _ __ _   _ ")
                    stdscr.addstr(sh // 2, sw // 2 - 30, " / _` | | '__/ _ \/ _` |/ _` | | | |/ / | |/ _ \ __/ __| | __| '__| | | |")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 30, "| (_| | | | |  __/ (_| | (_| | |_| |_|  | |  __/ |_\__ \ | |_| |  | |_| |")
                    stdscr.addstr(sh // 2 + 2, sw // 2 - 30, " \__,_|_|_|  \___|\__,_|\__,_|\__, (_)  |_|\___|\__|___/  \__|_|   \__, |")
                    stdscr.addstr(sh // 2 + 3, sw // 2 - 30, "                              |___/                                |___/ ")
                    stdscr.addstr(sh // 2 + 5, sw // 2 - 10, f"Final Score: {score}")
                    stdscr.addstr(sh // 2 + 6, sw // 2 - 10, f"Personal High Score: {high_score}")

                    # Check if score qualifies for top 10
                    high_scores = load_high_scores()
                    if len(high_scores) < 10 or score > high_scores[-1][0]:
                        stdscr.addstr(sh // 2 + 8, sw // 2 - 10, "New High Score! Enter your name: ")
                        stdscr.refresh()

                        curses.echo()  # Enable echoing of characters to capture name
                        # Show an underline where the user can type their name
                        name_win = curses.newwin(1, 20, sh // 2 + 9, sw // 2 - 10)
                        name_win.attron(curses.A_UNDERLINE)
                        name_win.refresh()
                        name = name_win.getstr().decode("utf-8").strip()
                        curses.noecho()  # Disable echoing again

                        update_high_scores(score, name, level_number)


                    stdscr.addstr(sh // 2 + 11, sw // 2 - 10, "Press Enter to view High Scores")
                    stdscr.refresh()

                    # Wait for "Enter" to continue
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break

                    # Display the high score board
                    display_high_scores(stdscr)
                    break


def main(stdscr):
    sh, sw = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.addstr(sh // 2 - 7, sw // 2 - 25, "                               _         ")
    stdscr.addstr(sh // 2 - 6, sw // 2 - 25, "  ___  _ __   ___   _ __ _   _| | ___    ")
    stdscr.addstr(sh // 2 - 5, sw // 2 - 25, " / _ \| '_ \ / _ \ | '__| | | | |/ _ \   ")
    stdscr.addstr(sh // 2 - 4, sw // 2 - 25, "| (_) | | | |  __/ | |  | |_| | |  __/_  ")
    stdscr.addstr(sh // 2 - 3, sw // 2 - 25, " \___/|_| |_|\___| |_|   \__,_|_|\___(_) ")
    stdscr.addstr(sh // 2 - 2, sw // 2 - 25, "     _             _     ____ ___ _____  ")
    stdscr.addstr(sh // 2 - 1, sw // 2 - 25, "  __| | ___  _ __ | |_  |  _ \_ _| ____| ")
    stdscr.addstr(sh // 2, sw // 2 - 25, " / _` |/ _ \| '_ \| __| | | | | ||  _|   ")
    stdscr.addstr(sh // 2 + 1, sw // 2 - 25, "| (_| | (_) | | | | |_  | |_| | || |___  ")
    stdscr.addstr(sh // 2 + 2, sw // 2 - 25, " \__,_|\___/|_| |_|\__| |____/___|_____| ")

    # Add a box with game controls on the title screen
    controls_start_y = sh // 2 - 5
    controls_start_x = sw // 2 + 20
    stdscr.addstr(controls_start_y, controls_start_x, "+------------------+")
    stdscr.addstr(controls_start_y + 1, controls_start_x, "|  Game Controls   |")
    stdscr.addstr(controls_start_y + 2, controls_start_x, "|------------------|")
    stdscr.addstr(controls_start_y + 3, controls_start_x, "| SPACE or W: Jump |")
    stdscr.addstr(controls_start_y + 4, controls_start_x, "| A: Move Left     |")
    stdscr.addstr(controls_start_y + 5, controls_start_x, "| D: Move Right    |")
    stdscr.addstr(controls_start_y + 6, controls_start_x, "| S: Hold Position |")
    stdscr.addstr(controls_start_y + 7, controls_start_x, "+------------------+")

    stdscr.addstr(sh // 2 + 4, sw // 2 - 10, "Press Enter to start")
    stdscr.refresh()

    # Wait for "Enter" to start the game
    while True:
        key = stdscr.getch()
        if key == ord("\n") or key == curses.KEY_ENTER:
            break

    high_score = 0  # Track high score across games

    while True:
        lives = 4  # Start with 4 lives, including the current life
        score = 0  # Reset score when starting a new game
        obstacle_speed_multiplier = 1.0  # Start with base obstacle speed
        level_number = 1  # Start at level 1
        obstacle_count_multiplier = 1.0  # Start with base obstacle count

        while lives > 0:
            lost_life, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier = game_loop(
                stdscr, lives, score, obstacle_speed_multiplier, high_score, level_number, obstacle_count_multiplier)

            if lost_life:
                lives -= 1
                if lives == 1:
                    # Display "Second-to-Last Life" screen
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 5, sw // 2 - 30, " _        _    ____ _____   _     ___ _____ _____ _ ")
                    stdscr.addstr(sh // 2 - 4, sw // 2 - 30, "| |      / \  / ___|_   _| | |   |_ _|  ___| ____| |")
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, "| |     / _ \ \___ \ | |   | |    | || |_  |  _| | |")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "| |___ / ___ \ ___) || |   | |___ | ||  _| | |___|_|")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "|_____/_/   \_\____/ |_|   |_____|___|_|   |_____(_)")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 10, "Press Enter to continue")
                    stdscr.refresh()

                    # Wait for "Enter" to continue
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break
                elif lives > 1:
                    # Display regular "Life Lost" screen if more than one life remains
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, " _____ _           _     _                _        ")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "|_   _| |__   __ _| |_  | |__  _   _ _ __| |_      ")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "  | | | '_ \\ / _` | __| | '_ \\| | | | '__| __|     ")
                    stdscr.addstr(sh // 2, sw // 2 - 30, "  | | | | | | (_| | |_  | | | | |_| | |  | |_ _ _   ")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 30, " _|_| |_| |_|\\__,_|\\__| |_| |_|\\__,_|_|  \\__(_|_)  ")
                    stdscr.addstr(sh // 2 + 2, sw // 2 - 30, "|_ _| | | ___  ___| |_    __ _  | (_)/ _| ___       ")
                    stdscr.addstr(sh // 2 + 3, sw // 2 - 30, " | |  | |/ _ \\/ __| __|  / _` | | | | |_ / _ \\      ")
                    stdscr.addstr(sh // 2 + 4, sw // 2 - 30, " | |  | | (_) \\__ \\ |_  | (_| | | | |  _|  __/     ")
                    stdscr.addstr(sh // 2 + 5, sw // 2 - 30, "  |___| |_|\\___/|___/\\__|  \\__,_| |_|_|_|  \\___|      ")
                    stdscr.addstr(sh // 2 + 6, sw // 2 - 10, f"Lives remaining: {lives}")
                    stdscr.addstr(sh // 2 + 8, sw // 2 - 10, "Press Enter to continue")
                    stdscr.refresh()


                    # Wait for "Enter" to continue with one less life
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break

                if lives == 0:
                    # Show Game Over screen if no lives remain
                    stdscr.clear()
                    stdscr.addstr(sh // 2 - 7, sw // 2 - 30, "     _     _ _             _                _                            ")
                    stdscr.addstr(sh // 2 - 6, sw // 2 - 30, " ___| |__ (_) |_        __| | ___  __ _  __| |                           ")
                    stdscr.addstr(sh // 2 - 5, sw // 2 - 30, "/ __| '_ \| | __|      / _` |/ _ \/ _` |/ _` |                           ")
                    stdscr.addstr(sh // 2 - 4, sw // 2 - 30, "\__ \ | | | | |_ _ _  | (_| |  __/ (_| | (_| |                           ")
                    stdscr.addstr(sh // 2 - 3, sw // 2 - 30, "|___/_| |_|_|\__(_|_)  \__,_|\___|\__,_|\__,_|                           ")
                    stdscr.addstr(sh // 2 - 2, sw // 2 - 30, "       _                    _      ___   _      _         _              ")
                    stdscr.addstr(sh // 2 - 1, sw // 2 - 30, "  __ _| |_ __ ___  __ _  __| |_   |__ \ | | ___| |_ ___  | |_ _ __ _   _ ")
                    stdscr.addstr(sh // 2, sw // 2 - 30, " / _` | | '__/ _ \/ _` |/ _` | | | |/ / | |/ _ \ __/ __| | __| '__| | | |")
                    stdscr.addstr(sh // 2 + 1, sw // 2 - 30, "| (_| | | | |  __/ (_| | (_| | |_| |_|  | |  __/ |_\__ \ | |_| |  | |_| |")
                    stdscr.addstr(sh // 2 + 2, sw // 2 - 30, " \__,_|_|_|  \___|\__,_|\__,_|\__, (_)  |_|\___|\__|___/  \__|_|   \__, |")
                    stdscr.addstr(sh // 2 + 3, sw // 2 - 30, "                              |___/                                |___/ ")
                    stdscr.addstr(sh // 2 + 5, sw // 2 - 10, f"Final Score: {score}")
                    stdscr.addstr(sh // 2 + 6, sw // 2 - 10, f"Personal High Score: {high_score}")

                    # Check if score qualifies for top 10
                    high_scores = load_high_scores()
                    if len(high_scores) < 10 or score > high_scores[-1][0]:
                        stdscr.addstr(sh // 2 + 8, sw // 2 - 10, "New High Score! Enter your name: ")
                        stdscr.refresh()

                        curses.echo()  # Enable echoing of characters to capture name
                        # Show an underline where the user can type their name
                        name_win = curses.newwin(1, 20, sh // 2 + 9, sw // 2 - 10)
                        name_win.attron(curses.A_UNDERLINE)
                        name_win.refresh()
                        name = name_win.getstr().decode("utf-8").strip()
                        curses.noecho()  # Disable echoing again

                        update_high_scores(score, name, level_number)


                    stdscr.addstr(sh // 2 + 11, sw // 2 - 10, "Press Enter to view High Scores")
                    stdscr.refresh()

                    # Wait for "Enter" to continue
                    while True:
                        key = stdscr.getch()
                        if key == ord("\n") or key == curses.KEY_ENTER:
                            break

                    # Display the high score board
                    display_high_scores(stdscr)
                    break

curses.wrapper(main)


