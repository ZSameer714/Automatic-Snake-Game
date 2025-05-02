import pygame
import sys
import random
import heapq
import math

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

# Directions (vectors)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- A* Node ---
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start
        self.h = 0  # Heuristic cost to end
        self.f = 0  # Total cost (g + h)

    # Comparison for priority queue
    def __lt__(self, other):
        return self.f < other.f

    # Equality check based on position
    def __eq__(self, other):
        return self.position == other.position

    # Hash based on position for use in sets
    def __hash__(self):
        return hash(self.position)

# --- Heuristic Function (Manhattan Distance) ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# --- A* Algorithm ---
def a_star(grid_width, grid_height, start, end, obstacles):
    """
    Finds the shortest path using A*.
    Args:
        grid_width: Width of the grid.
        grid_height: Height of the grid.
        start: Tuple (x, y) start position.
        end: Tuple (x, y) end position.
        obstacles: Set or List of tuple (x, y) obstacle positions.
                   Important: Obstacles should generally include the snake body *except* maybe the tail
                   if the snake is about to move off it.
    Returns:
        List of tuple (x, y) positions representing the path, or None if no path found.
    """
    start_node = Node(start)
    end_node = Node(end)

    open_list = [] # Priority queue (min-heap)
    closed_list = set() # Set of visited positions

    heapq.heappush(open_list, start_node)

    # Convert obstacles list to set for faster lookups
    obstacle_set = set(obstacles)

    while open_list:
        # Get the node with the lowest f cost
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # --- Goal Reached ---
        if current_node.position == end_node.position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path (start to end)

        # --- Explore Neighbors ---
        (x, y) = current_node.position
        neighbors = [(x + dx, y + dy) for dx, dy in [UP, DOWN, LEFT, RIGHT]]

        for next_pos in neighbors:
            nx, ny = next_pos

            # Check bounds
            if not (0 <= nx < grid_width and 0 <= ny < grid_height):
                continue

            # Check if neighbor is an obstacle (part of snake body)
            if next_pos in obstacle_set:
                continue

            # Check if neighbor is already evaluated
            if next_pos in closed_list:
                continue

            # Create neighbor node
            neighbor_node = Node(next_pos, current_node)
            neighbor_node.g = current_node.g + 1 # Cost to move to neighbor is 1
            neighbor_node.h = heuristic(neighbor_node.position, end_node.position)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # Check if neighbor is in open list and if this path is better
            # Use a flag and loop because heapq doesn't have a direct update/contains check
            in_open_list = False
            for i, item in enumerate(open_list):
                if item.position == neighbor_node.position:
                    in_open_list = True
                    if neighbor_node.g < item.g:
                        # Found a better path to this neighbor, update it
                        # (In heapq, it's often easier to just add the better node;
                        # the worse one will eventually be popped and ignored via closed_list)
                        open_list[i] = neighbor_node # Update existing node (less efficient)
                        heapq.heapify(open_list) # Need to reheapify after update
                        # Or simply: heapq.heappush(open_list, neighbor_node)
                        # and let the closed_list check handle duplicates later.
                    break # Exit inner loop once found/updated

            if not in_open_list:
                heapq.heappush(open_list, neighbor_node)

    return None # No path found

# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Automatic Snake (A*)')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 25)

# --- Helper Functions ---
def draw_grid():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

def spawn_food(snake_body):
    while True:
        food_pos = (random.randint(0, GRID_WIDTH - 1),
                    random.randint(0, GRID_HEIGHT - 1))
        # Ensure food doesn't spawn on the snake
        if food_pos not in snake_body:
            return food_pos

def draw_snake(snake_body):
    for i, segment in enumerate(snake_body):
        x, y = segment
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Head different color
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, rect)
        # Optional: add a small border
        pygame.draw.rect(screen, BLACK, rect, 1)


def draw_food(food_pos):
    x, y = food_pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, rect)

def draw_path(path):
    if path:
        for step in path:
             x, y = step
             rect = pygame.Rect(x * CELL_SIZE + CELL_SIZE // 4, y * CELL_SIZE + CELL_SIZE // 4, CELL_SIZE // 2, CELL_SIZE // 2)
             pygame.draw.rect(screen, (0, 0, 200), rect) # Draw blue dots for path

# --- Game Variables ---
snake_start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
snake_body = [snake_start_pos,
              (snake_start_pos[0] - 1, snake_start_pos[1]),
              (snake_start_pos[0] - 2, snake_start_pos[1])]
snake_direction = RIGHT  # Initial direction
food_pos = spawn_food(snake_body)
path = None # Stores the current path from A*
score = 0
game_over = False

# --- Main Game Loop ---
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Pathfinding Logic ---
    # If no path exists (or snake reached previous target), find a new one
    if path is None or not path:
        # Pass snake body EXCEPT the head as obstacles for A*
        # (Head is the start point, not an obstacle for itself)
        # Tail is usually not an obstacle either if the snake is long enough,
        # as it will move out of the way. Let's exclude the tail for simplicity.
        obstacles_for_astar = snake_body[1:-1] if len(snake_body) > 2 else [] # Exclude head and tail
        
        # Find path from head to food
        path = a_star(GRID_WIDTH, GRID_HEIGHT, snake_body[0], food_pos, obstacles_for_astar)
        # print(f"New path found: {path}") # Debugging
        if path and len(path) > 1:
            path.pop(0) # Remove the current head position from the path
        elif path and len(path) <= 1: # Path is just the current position (already there?) or invalid
             path = None # Force recalculation or stop


    # --- Movement Logic ---
    next_move_calculated = False
    if path:
        try:
            # Get the next step from the pre-calculated path
            next_step = path[0]
            current_head = snake_body[0]

            # Determine direction needed to get to next_step
            dx = next_step[0] - current_head[0]
            dy = next_step[1] - current_head[1]

            # Basic check to prevent impossible moves (shouldn't happen with A*)
            if abs(dx) + abs(dy) == 1:
                 snake_direction = (dx, dy)
                 next_move_calculated = True
                 path.pop(0) # Consume this step from the path
            else:
                # Path seems invalid (e.g., diagonal move requested) - clear path
                print(f"Warning: Invalid step in path {current_head} -> {next_step}. Clearing path.")
                path = None # Recalculate next frame

        except IndexError:
            # Path list might be empty if something went wrong
             print("Warning: Path list empty unexpectedly.")
             path = None # Recalculate


    # --- Update Snake Position ---
    if next_move_calculated: # Only move if we determined a valid step
        head_x, head_y = snake_body[0]
        dir_x, dir_y = snake_direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # --- Collision Detection ---
        # Wall collision
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            game_over = True
            print("Game Over: Wall Collision")
        # Self collision (check against body *excluding* the tail that will move)
        elif new_head in snake_body[:-1]: # Check against all but the last segment
            game_over = True
            print("Game Over: Self Collision")

        if not game_over:
            # Insert new head
            snake_body.insert(0, new_head)

            # --- Food Eating ---
            if new_head == food_pos:
                score += 1
                food_pos = spawn_food(snake_body)
                path = None # Need to calculate a new path to the new food
                # Don't pop the tail, snake grows
            else:
                # Remove tail segment if food not eaten
                snake_body.pop()
    # else: # If no valid move calculated (e.g., no path found), snake waits

    # --- Drawing ---
    screen.fill(BLACK)
    # draw_grid() # Optional: draw grid lines
    draw_snake(snake_body)
    draw_food(food_pos)
    # draw_path(path) # Optional: visualize the A* path

    # Display Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (5, 5))

    # --- Update Display ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(8) # Control game speed (frames per second)

# --- Game Over Screen (Simple) ---
print(f"Final Score: {score}")
game_over_font = pygame.font.SysFont(None, 50)
game_over_text = game_over_font.render('GAME OVER', True, RED)
text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
screen.blit(game_over_text, text_rect)
pygame.display.flip()

# Keep window open for a bit after game over
pygame.time.wait(3000)

pygame.quit()
sys.exit()