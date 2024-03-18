import os

class DirectoryManager:
    BASE = ""

    def __init__(self, localpath):
        if not DirectoryManager.BASE:
            DirectoryManager.BASE = os.path.abspath(localpath)

def main():
    # Example usage
    dm = DirectoryManager("example_path")
    print(dm.BASE)  # Will print the absolute path of "example_path"

if __name__ == "__main__":
    main()
