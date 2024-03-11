import json

JSON_filenames = {
    "t_base": "basic_tests.json",
    "t_mirror": "mirror_tests.json",
    "t_maze": "basic_maze_tests.json",
    "t_allcat": "all_categories.json",
    "null": "sandbox.json"
}

def read_all_files(namedict:dict):
    resdict=dict()
    for e, v in namedict.items():
        F = open(v, 'r')
        raw = F.read()
        F.close()
        try:
            processed = json.loads(raw)
            resdict[e] = processed
        except json.decoder.JSONDecodeError as err:
            print(v,err)
    return resdict

JSON_data = read_all_files(JSON_filenames)



def main():
    for e in JSON_data:
        print(type(e))
    return


if __name__ == "__main__":
    main()
