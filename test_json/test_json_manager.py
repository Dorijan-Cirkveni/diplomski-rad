import json
import os

from util.FragmentedJsonProcessor import ImportFragmentedJSON

current_dir = os.path.dirname(os.path.abspath(__file__))

JSON_filenames = {
    "g_base": "basic_grids.json",

    "tb_base": "basic_tests.json",
    "tb_maze": "basic_maze_tests.json",
    "t_maze1": "maze_tests_1.json",

    "t_mirror": "mirror_tests.json",

    "t_allcat": "all_categories.json",

    "null": "sandbox.json"
}


import os

def search_files(maindir: str, filenames: set[str]) -> dict:
    """
    Search for files with specified filenames in the given directory and its subdirectories.

    :param maindir: The main directory to start the search.
    :param filenames: A set of filenames to search for.
    :return: A dictionary containing the found filenames as keys and their paths as values.
    """
    result = {}

    for root, dirs, files in os.walk(maindir):
        for file in files:
            if file in filenames:
                result[file] = os.path.join(root, file)

    return result



def read_all_files(namedict: dict):
    paths:dict=search_files(current_dir,set(namedict.values()))
    resdict = dict()
    for e, v in namedict.items():
        if v not in paths:
            raise Exception("File {} missing!".format(v))
        v2=paths[v]
        filepath = os.path.join(current_dir, v2)
        F = open(filepath, 'r')
        raw = F.read()
        F.close()
        try:
            processed = json.loads(raw)
            resdict[e] = processed
        except json.decoder.JSONDecodeError as err:
            print(v, err)
    return resdict


JSON_data = read_all_files(JSON_filenames)


def ImportManagedJSON(main_file, files: dict = None, applyToMain=False):
    """

    :param applyToMain: Toggles whether the main_file entry is replaced with a full version when complete.
    :param main_file:
    :param files:
    :return:
    """
    files = JSON_data if files is None else files
    full_main = ImportFragmentedJSON(main_file, JSON_data)
    if applyToMain:
        files[main_file] = full_main
    return full_main


def main():
    path = os.path.normpath(current_dir)
    res = path.split(os.sep)
    print(res)
    # ImportManagedJSON("tb_base")
    return


if __name__ == "__main__":
    main()
