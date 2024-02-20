import random

from GridEnvironment import *


def rect(E, grid):
    if len(E) != 5:
        raise Exception("Bad rect data length!")
    (y1, x1, y2, x2, v) = E
    if y1 > y2:
        y1, y2 = y2, y1
    if x1 > x2:
        x1, x2 = x2, x1
    for dx in range(x1, x2 + 1):
        grid[y1][dx] = v
        grid[y2][dx] = v
    for dy in range(y1, y2 + 1):
        grid[dy][x1] = v
        grid[dy][x2] = v
    return


class MazeEnvironment(GridEnvironment):
    def __init__(self, scale: tuple, entities: list[itf.Entity] = None,
                 activeEntities: set = None, tileTypes=None, data=None, maze_seed=0):
        maze = self.generate_maze(scale, maze_seed)
        super().__init__(scale, maze, entities, activeEntities=activeEntities, tileTypes=tileTypes)

    def generate_maze(self, scale: tuple, maze_seed: int):
        mazeScale=Tdiv(scale,(2,2))
        random.seed(maze_seed)

        def carve_path(x, y):
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < scale[1] and 0 <= ny < scale[0] and maze[ny][nx] == 0:
                    maze[y + dy // 2][x + dx // 2] = 1
                    maze[ny][nx] = 1
                    carve_path(nx, ny)

        maze = [[0] * scale[1] for _ in range(scale[0])]

        # Set up the initial state
        start_x, start_y = random.randrange(1, scale[1], 2), random.randrange(1, scale[0], 2)
        maze[start_y][start_x] = 3  # Agent starting position

        # Generate the maze
        carve_path(start_x, start_y)

        # Set a random goal position
        goal_x, goal_y = random.randrange(1, scale[1], 2), random.randrange(1, scale[0], 2)
        maze[goal_y][goal_x] = 2  # Goal position

        return maze


# Example usage:
maze_seed = 42  # Change this seed to generate a different maze
maze_env = MazeEnvironment((20, 20), maze_seed=42)


def generate_maze(width, height):
    maze = [[0] * width for _ in range(height)]

    def is_valid(x, y):
        return 0 <= x < width and 0 <= y < height

    def carve_path(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and maze[ny][nx] == 0:
                maze[y + dy // 2][x + dx // 2] = 1
                maze[ny][nx] = 1
                carve_path(nx, ny)

    # Set up the initial state
    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    maze[start_y][start_x] = 3  # Agent starting position

    # Generate the maze
    carve_path(start_x, start_y)

    # Set a random goal position
    goal_x, goal_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    maze[goal_y][goal_x] = 2  # Goal position

    return maze



def main():
    # Example usage for a 20x20 maze
    maze_width, maze_height = 20, 20
    generated_maze = generate_maze(maze_width, maze_height)

    # Display the generated maze
    for row in generated_maze:
        print(" ".join(map(str, row)))
    return


if __name__ == "__main__":
    main()
