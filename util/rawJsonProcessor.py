def get_area(raw:dict,key:str,default:tuple=(0,0,0,0)):
    single=key+"_single"
    if single in raw:
        return raw[single]*2
    area=key+"_area"
    if area in raw:
        return raw[area]



def main():
    return


if __name__ == "__main__":
    main()
