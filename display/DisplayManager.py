from display.display_sandbox_tk import *
from display.DisplayGrid import *

def main():
    mainframe=Test()
    grid_display_frame=GridDisplayFrame(mainframe)
    first=ExampleFrame(mainframe,"Example")
    second=ExampleFrameRedux(mainframe,"ExampleRedux")

    test_grid=Grid2D((20,20),[[i+j for j in range(20)]for i in range(20)])
    grid_display_frame.set_grid(test_grid)

    mainframe.add_frame(first)
    mainframe.add_frame(second)
    mainframe.add_frame(grid_display_frame)
    mainframe.run(grid_display_frame.name)
    return


if __name__ == "__main__":
    main()
