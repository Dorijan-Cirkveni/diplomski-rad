import random

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
