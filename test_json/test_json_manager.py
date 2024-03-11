import json
import os

from util.FragmentedJsonProcessor import ImportFragmentedJSON
current_dir = os.path.dirname(os.path.abspath(__file__))

JSON_filenames = {
    "g_base": "grids\\grid_templates.json",

    "t_base": "basic_tests.json",
    "t_mirror": "mirror_tests.json",
    "t_maze": "basic_maze_tests.json",
    "t_allcat": "all_categories.json",
    "null": "sandbox.json"
}


def read_all_files(namedict: dict):
    resdict = dict()
    for e, v in namedict.items():
        filepath=os.path.join(current_dir,v)
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


def ImportManagedJSON(main_file):
    """

    :param main_file:
    :return:
    """
    return ImportFragmentedJSON(main_file, JSON_data)


def main():
    for e in JSON_data:
        print(type(e))
    return


if __name__ == "__main__":
    main()
