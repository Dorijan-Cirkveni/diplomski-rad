from util.Grid2D import Grid2D


class GridStateEncoder:
    def __init__(self,keys=None):
        self.keys=[("key",-1), ("viewdir",0)] if keys is None else keys
    @staticmethod
    def from_pretrained(origin):
        return

    def save_pretrained(self, destination):
        return

    # {'grid': Grid2D, 'entities': {0: {'loc': (15, 5), 'viewdir': 10}, 1: {'image': 'blue', 'loc': (15, 10)}}}

    def encode(self, state: dict):

        grid_base: Grid2D = state['grid']
        entity_base:Grid2D=Grid2D(grid_base.scale)
        ebl0=len(entity_base[0])
        bases=[grid_base,entity_base]
        other_bases: dict={e:Grid2D(grid_base.scale) for e in self.keys}
        for entID, entData in state.get('entities',{}):
            entLoc=divmod(entID,ebl0)
            location=state.get('loc')
            entity_base[location]=entID
            for (key,default) in self.keys:
                value=entID if key=="key" else state.get(key,default)
                other_bases[key][entLoc]=value



    def decode(self):
        raise NotImplementedError


def main():
    return


if __name__ == "__main__":
    main()
