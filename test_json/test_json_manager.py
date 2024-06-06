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

def get_grid_files(custom_exceptions=None):
    D=search_files(current_dir)
    res=filter_env_paths(D,custom_exceptions)
    return res

def read_file_to_dict(name, filepath, resdict):
    F = open(filepath, 'r')
    raw = F.read()
    F.close()
    try:
        processed = json.loads(raw)
        resdict[name] = processed
    except json.decoder.JSONDecodeError as err:
        raise Exception(filepath, err)


def read_all_files(exceptions=None):
    if exceptions is None:
        exceptions = {"sandbox.json"}
    all_paths:dict=search_files(current_dir)
    filt=filter_env_paths(all_paths,exceptions)
    paths={e:all_paths[e] for e in filt}
    resdict = dict()
    for name, filepath in paths.items():
        read_file_to_dict(name,filepath,resdict)
    return resdict


JSON_data = read_all_files()
GRIDFILES=get_grid_files()


def ImportManagedJSON(address, files: dict = None, applyToMain=False, error_if_not_env=True):
    """

    :param applyToMain: Toggles whether the main_file entry is replaced with a full version when complete.
    :param address:
    :param files:
    :return:
    """
    X=address.split("|")
    main_file=X[0]
    files = JSON_data if files is None else files
    if main_file not in files:
        s="{} does not exist, try one of these: {}"
        s2=s.format(main_file,GRIDFILES)
        raise FragmentedJSONException(s2)
    if error_if_not_env and main_file not in GRIDFILES:
        s="{} is not a registered environment! Must be on list {}"
        s2=s.format(main_file,GRIDFILES)
        raise FragmentedJSONException(s2)
    full_main = ImportFragmentedJSON(main_file, JSON_data)
    if applyToMain:
        files[main_file] = full_main
    res=DescendByFragment(full_main,X[1:])
    return res

def ExportManagedJSON(address, new_data, files: dict = None, applyToMain=False):
    X=address.split("|")
    filepaths=search_files(current_dir)
    main_file=X[0]
    if main_file not in filepaths:
        raise FragmentedJSONException(f"{main_file} not in files: {filepaths}")
    files = JSON_data if files is None else files
    raise NotImplementedError

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
