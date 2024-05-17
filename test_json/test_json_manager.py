import json
import os

from util.FragmentedJsonProcessor import *

current_dir = os.path.dirname(os.path.abspath(__file__))


import os

def search_files(maindir: str, extension:str=".json") -> dict:
    """
    Search for files with a specified extension in the given directory and its subdirectories.

    :param maindir: The main directory to start the search.
    :param extension: Chosen extension, defaults to .json
    :return: A dictionary containing the found filenames as keys and their paths as values.
    """
    result = {}

    k=-len(extension)
    for root, dirs, files in os.walk(maindir):
        for file in files:
            if file.endswith(extension):
                result[file[:k]] = os.path.join(root, file)

    return result

notenv=[
    "agents",
    "tiles",
    "entities",
    "grids",
    "effects.json",
    "syntax test sandbox.json",
    "sandbox.json"
]

def filter_env_paths(filedict:dict, forbidden:set=None):
    if forbidden is None:
        forbidden = set(notenv)
    filtered=[]
    for name,path in filedict.items():
        S=set(path.split("\\"))
        if S&forbidden:
            continue
        filtered.append(name)
    return filtered

def get_grid_files():
    D=search_files(current_dir)
    res=filter_env_paths(D)
    return res


def read_all_files():
    paths:dict=search_files(current_dir)
    resdict = dict()
    for name, filepath in paths.items():
        F = open(filepath, 'r')
        raw = F.read()
        F.close()
        try:
            processed = json.loads(raw)
            resdict[name] = processed
        except json.decoder.JSONDecodeError as err:
            raise Exception(filepath, err)
    return resdict


JSON_data = read_all_files()


def ImportManagedJSON(address, files: dict = None, applyToMain=False):
    """

    :param applyToMain: Toggles whether the main_file entry is replaced with a full version when complete.
    :param address:
    :param files:
    :return:
    """
    X=address.split("|")
    main_file=X[0]
    files = JSON_data if files is None else files
    full_main = ImportFragmentedJSON(main_file, JSON_data)
    if applyToMain:
        files[main_file] = full_main
    res=DescendByFragment(full_main,X[1:])
    return res

def test(full_addr):
    print(ImportManagedJSON(full_addr))

def getNamesAndIndices(files=None):
    if files is None:
        files = get_grid_files()
    data={file:[] for file in files}
    for file in files:
        L=ImportManagedJSON(file)
        for i,D in enumerate(L):
            name=D.get('name','{}-{}'.format(file,i))
            data[file].append(name)
    return [(file,data[file]) for file in files]


def main():
    res=getNamesAndIndices()
    for E in res:
        print(E)
    return


if __name__ == "__main__":
    main()
