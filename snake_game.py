import random
import time # Keep for now, might remove if curses timeout is sufficient
import curses

class SnakeGame:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height

        # Initialize snake
        self.snake_pos = [[width // 2, height // 2]] # List of [x,y] coordinates
        self.direction = 'RIGHT' # Initial direction: 'UP', 'DOWN', 'LEFT', 'RIGHT'

        # Initialize food
        self.food_pos = [] # Will be set by _place_food()
        self._place_food() # Set initial food position

        # Game state
        self.score = 0
        self.game_over = False

        # Conceptual board, primarily for boundary checks.
        # No explicit 2D list for the board state for now to keep it lightweight.
        # Collision detection will be based on coordinates.

    def _place_food(self):
        """
        Places food at a random position on the board, not occupied by the snake.
        """
        while True:
            x = random.randrange(0, self.width)
            y = random.randrange(0, self.height)
            if [x, y] not in self.snake_pos:
                self.food_pos = [x, y]
                break

    def _move(self):
        """
        Moves the snake based on the current direction.
        """
        current_head = self.snake_pos[0]
        new_head = list(current_head) # Create a copy

        if self.direction == 'UP':
            new_head[1] -= 1
        elif self.direction == 'DOWN':
            new_head[1] += 1
        elif self.direction == 'LEFT':
            new_head[0] -= 1
        elif self.direction == 'RIGHT':
            new_head[0] += 1
        
        self.snake_pos.insert(0, new_head)
        # Tail removal is now handled in update() based on food consumption

    def change_direction(self, new_direction):
        """
        Changes the snake's direction, preventing immediate reversal.
        """
        if new_direction == 'UP' and self.direction != 'DOWN':
            self.direction = new_direction
        elif new_direction == 'DOWN' and self.direction != 'UP':
            self.direction = new_direction
        elif new_direction == 'LEFT' and self.direction != 'RIGHT':
            self.direction = new_direction
        elif new_direction == 'RIGHT' and self.direction != 'LEFT':
            self.direction = new_direction

    def update(self):
        """
        Updates the game state by one step.
        Moves snake, checks for collisions, food consumption, and updates score.
        """
        if self.game_over:
            return

        # 1. Move the snake
        self._move() # This adds a new head

        head = self.snake_pos[0]

        # 2. Check for collisions
        # Wall collision
        if not (0 <= head[0] < self.width and 0 <= head[1] < self.height):
            self.game_over = True
            return # Stop further processing if game over

        # Self-collision
        if head in self.snake_pos[1:]:
            self.game_over = True
            return # Stop further processing if game over

        # 3. Check for food consumption (only if not game over)
        if head == self.food_pos:
            self.score += 1
            self._place_food() # Generate new food
            # Snake grows, so we don't pop the tail
        else:
            self.snake_pos.pop() # Remove tail if no food eaten

    def get_state(self):
        """
        Returns a dictionary representing the current game state.
        """
        return {
            'snake_body': list(self.snake_pos), # Ensure a copy is returned
            'food_pos': list(self.food_pos),   # Ensure a copy is returned
            'score': self.score,
            'game_over': self.game_over,
            'direction': self.direction,
            'head_pos': list(self.snake_pos[0]) if self.snake_pos else [] # Ensure a copy
        }

    def reset(self):
        """
        Resets the game to its initial state.
        """
        self.snake_pos = [[self.width // 2, self.height // 2]]
        self.direction = 'RIGHT'
        self._place_food() # Place new food
        self.score = 0
        self.game_over = False
        # The width and height remain unchanged

    def render(self):
        """
        Renders the game (e.g., to console using curses or prints).
        Optional, primarily for debugging/demonstration.
        Placeholder for now.
        """
        # Example: Print simple text representation or use curses
        pass

    def get_random_action(self):
        """
        Determines a random valid action for the snake, avoiding immediate reversal.
        """
        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        if self.direction == 'UP' and 'DOWN' in possible_actions:
            possible_actions.remove('DOWN')
        elif self.direction == 'DOWN' and 'UP' in possible_actions:
            possible_actions.remove('UP')
        elif self.direction == 'LEFT' and 'RIGHT' in possible_actions:
            possible_actions.remove('RIGHT')
        elif self.direction == 'RIGHT' and 'LEFT' in possible_actions:
            possible_actions.remove('LEFT')
        
        if not possible_actions:
            # This case should ideally not be reached if there's space to move.
            # If it is, it means the only way is to reverse, which change_direction will block.
            # Returning current direction is a safe fallback. Or pick any from the original 4.
            return self.direction 
            
        return random.choice(possible_actions)

def main_loop(stdscr):
    # curses setup
    stdscr.nodelay(True)  # Non-blocking getch
    stdscr.timeout(100)   # Timeout for getch() in milliseconds (100ms = 10fps)

    # Game dimensions (can be adjusted)
    # For curses, it's often better to get dimensions from stdscr.getmaxyx()
    # but for now, we'll use fixed, ensuring they fit typical terminals.
    game_width = 20 
    game_height = 15 
    
    # Ensure game dimensions are smaller than screen to avoid errors
    # screen_height, screen_width = stdscr.getmaxyx()
    # if game_width >= screen_width or game_height >= screen_height:
    #     # Handle error or adjust game size
    #     pass


    game = SnakeGame(width=game_width, height=game_height)

    while not game.game_over:
        key = stdscr.getch() # Get character, returns curses.ERR if timeout

        if key == curses.KEY_UP:
            game.change_direction('UP')
        elif key == curses.KEY_DOWN:
            game.change_direction('DOWN')
        elif key == curses.KEY_LEFT:
            game.change_direction('LEFT')
        elif key == curses.KEY_RIGHT:
            game.change_direction('RIGHT')
        elif key == ord('q') or key == ord('Q'): # Optional: Quit key
            break
        
        game.update()

        # Basic rendering for now (will be improved in next step)
        stdscr.clear()
        stdscr.addstr(0, 0, f"Score: {game.score} | Press Q to Quit")
        # Draw snake (simple 'S')
        for y, x in game.snake_pos: # Note: curses uses (y,x)
             if 0 <= y < game_height and 0 <= x < game_width: # Boundary check for drawing
                stdscr.addstr(y + 1, x, "S") # +1 to avoid score line
        # Draw food (simple 'F')
        if game.food_pos and 0 <= game.food_pos[1] < game_height and 0 <= game.food_pos[0] < game_width:
             stdscr.addstr(game.food_pos[1] + 1, game.food_pos[0], "F") # +1 to avoid score line
        stdscr.refresh()


    # Game over screen
    stdscr.clear() 
    # Calculate center position for messages
    # Note: game.height here refers to the game board, not necessarily screen height
    center_y = game_height // 2 
    center_x_offset_msg = len("Game Over!") // 2
    center_x_offset_score = len(f"Score: {game.score}") // 2
    center_x_offset_exit = len("Press any key to exit.") // 2

    # Ensure messages are within screen bounds if game board is large
    # This is a simplified centering for the game board area.
    # For true screen centering, stdscr.getmaxyx() would be used.
    
    stdscr.addstr(center_y, game_width // 2 - center_x_offset_msg, "Game Over!")
    stdscr.addstr(center_y + 1, game_width // 2 - center_x_offset_score, f"Score: {game.score}")
    stdscr.addstr(center_y + 3, game_width // 2 - center_x_offset_exit, "Press any key to exit.")
    
    stdscr.nodelay(False) # Make getch blocking for the final key press
    stdscr.getch()

def run_random_agent_test():
    game = SnakeGame(width=10, height=10)
    max_steps = 200 # Increased steps for more thorough random test
    print("Running Random Agent Test...")
    for step in range(max_steps):
        if game.game_over:
            print(f"Random agent game over at step {step+1}. Score: {game.score}")
            print(f"Final snake: {game.snake_pos}, Food: {game.food_pos}")
            break

        action = game.get_random_action()
        game.change_direction(action) 
        game.update()
        
        # Simple console print for the random agent
        print(f"Step: {step+1}, Action: {action}, Dir: {game.direction}, Score: {game.score}, Snake Head: {game.snake_pos[0]}, Food: {game.food_pos}")
        
        # Optional: Basic text rendering (can be very verbose)
        # board_display = [['.' for _ in range(game.width)] for _ in range(game.height)]
        # if game.food_pos:
        #     board_display[game.food_pos[1]][game.food_pos[0]] = 'F'
        # for r, c in game.snake_pos:
        #     board_display[r][c] = 'S'
        # for row in board_display:
        #     print("".join(row))
        # print("-" * game.width)

        time.sleep(0.05) # Faster than curses mode for quick testing
    else:
        print(f"Random agent finished {max_steps} steps. Final Score: {game.score}")
    
    print("\nRandom Agent Test Finished.\n")

if __name__ == '__main__':
    # To run the game with curses (human playable):
    # curses.wrapper(main_loop)

    # To run the random agent test (prints to console):
    run_random_agent_test()
