import json
import os

from util.FragmentedJsonProcessor import ImportFragmentedJSON
current_dir = os.path.dirname(os.path.abspath(__file__))

JSON_filenames = {
    "g_base": "grids\\basic_grids.json",

    "tb_base": "basic\\basic_tests.json",
    "t_mirror": "mirror_tests.json",
    "tb_maze": "basic\\basic_maze_tests.json",
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


def ImportManagedJSON(main_file, files:dict=None, applyToMain=False):
    """

    :param applyToMain: Toggles whether the main_file entry is replaced with a full version when complete.
    :param main_file:
    :param files:
    :return:
    """
    files=JSON_data if files is None else files
    full_main=ImportFragmentedJSON(main_file, JSON_data)
    if applyToMain:
        files[main_file]=full_main
    return full_main


def main():
    ImportManagedJSON("tb_base")
    return


if __name__ == "__main__":
    main()
