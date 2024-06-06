from util.struct.Grid2D import *


def test_grid_initialization():
    grid = Grid2D((5, 5))
    print("Initialized 5x5 Grid with default values:")
    print(grid.get_text_display(str))

def test_drawing_shapes():
    rect = Rect(1, 1, 3, 3, 9)
    grid = Grid2D((5, 5))
    grid.use_draw_element(rect)
    print("\nGrid after drawing a rectangle from (1,1) to (3,3) with value 9:")
    print(grid.get_text_display(str))

def test_grid_operations():
    X = [
        [-1, 2, 1, 1, 1],
        [1, 0, 0, 0, 0]
    ]
    grid = Grid2D((5, 5), X)
    print("\nOriginal Grid:")
    print(grid.get_text_display(str))

    # Mirroring the grid vertically
    mirrored_grid = grid.mirror(dimension=1)
    print("\nMirrored Grid (Vertically):")
    print(mirrored_grid.get_text_display(str))

    # Creating a framed grid
    framed_grid = init_framed_grid((7, 7), frameType=2, fillType=0)
    print("\nFramed Grid (7x7):")
    print(framed_grid.get_text_display(str))

def demonstrate_rotate_layer():
    grid = Grid2D((5, 5), [
        [8, 1, 2, 3, 4],
        [7, 0, 0, 0, 5],
        [6, 0, 0, 0, 6],
        [5, 0, 0, 0, 7],
        [4, 3, 2, 1, 8]
    ])
    print("\nOriginal Grid:")
    print(grid.get_text_display(str))

    grid.rotate_layer(0, 1)
    print("\nGrid after rotating the outermost layer clockwise:")
    print(grid.get_text_display(str))

    grid.rotate_layer(1, -1)
    print("\nGrid after rotating the second layer counterclockwise:")
    print(grid.get_text_display(str))

def test_diff():
    grid1_data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    grid2_data = [
        [1, 2, 3],
        [4, 0, 6],  # Difference here (5 -> 0)
        [7, 8, 9]
    ]

    grid1 = Grid2D((3, 3), grid1_data)
    grid2 = Grid2D((3, 3), grid2_data)

    diff_grid = grid1.diff(grid2)
    print("\nDifference Grid (comparing grid1 and grid2):")
    print(diff_grid.get_text_display(str))

def test_anim_change():
    # Create two grids with differences
    grid1_data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

    grid2_data = [
        [1, 2, 3],
        [4, 0, 6],  # Difference here (5 -> 0)
        [7, 8, 9]
    ]

    grid1 = Grid2D((3, 3), grid1_data)
    grid2 = Grid2D((3, 3), grid2_data)

    # Define special tiles to be highlighted
    specials = {(1, 1)}

    # Apply the anim_change function
    anim_grid = grid1.anim_change(grid2, specials)

    # Display the grids and the animation change
    display_method = str  # Use a simple string conversion for display

    print("Grid 1:")
    print(grid1.get_text_display(display_method))

    print("\nGrid 2:")
    print(grid2.get_text_display(display_method))

    print("\nAnimation Change Grid:")
    print(anim_grid.get_text_display(display_method))


# Running the tests
test_grid_initialization()
test_drawing_shapes()
test_grid_operations()
demonstrate_rotate_layer()
test_diff()
test_anim_change()
