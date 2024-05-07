from display.display_sandbox_tk import *
from display.DisplayGrid import *

def main():
    mainframe=Test()
    grid=GridDisplayFrame(mainframe)
    first=ExampleFrame(mainframe,"Example")
    second=ExampleFrameRedux(mainframe,"ExampleRedux")
    mainframe.add_frame(first)
    mainframe.add_frame(second)
    mainframe.add_frame(grid)
    mainframe.run(grid.name)
    return


if __name__ == "__main__":
    main()
