import json
import os

from util.FragmentedJsonProcessor import *
from util.Filesystem import *

current_dir = os.path.dirname(os.path.abspath(__file__))


import os


JSON_data = read_all_files()
GRIDFILES = get_valid_files()


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
        files = get_valid_files()
    data={file:[] for file in files}
    for file in files:
        L=ImportManagedJSON(file)
        for i,D in enumerate(L):
            name=D.get('name','{}-{}'.format(file,i))
            data[file].append(name)
    return [(file,data[file]) for file in files]

def getRaw(files=None):
    if files is None:
        files = get_valid_files()
    data=[]
    for file,path in files.items():
        F=open(path)
        s=F.read()
        F.close()
        L=json.loads(s)
        data.append((file,L))
    return data


def main():
    res=getRaw()
    for name,L in res:
        print(name)
        for E in L:
            if type(E)!=dict:
                print("\t",E)
                continue
            print("\t",E.get('name','unnamed'))
    return


if __name__ == "__main__":
    main()
