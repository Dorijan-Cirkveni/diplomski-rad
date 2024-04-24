import torch

from util.struct.Grid2D import Grid2D


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
        other_bases: dict={e:Grid2D(grid_base.scale,defaultValue=v) for e,v in self.keys}
        entities:dict=state.get('entities',{})
        for entID, entData in entities.items():
            entLoc=divmod(entID,ebl0)
            location=entData.get('loc')
            entity_base[location]=entID
            for (key,default) in self.keys:
                value=entID if key=="key" else entData.get(key,default)
                other_bases[key][entLoc]=value
        resBase=[grid_base.M,entity_base.M]
        for key,_ in self.keys:
            resBase.append(other_bases[key].M)
        tensor=torch.tensor(resBase, dtype=torch.long)
        return tensor



    def decode(self):
        raise NotImplementedError


import time


def main():
    print("Encoding...")
    start_time = time.time()  # Start timer

    encoder = GridStateEncoder()
    grid = Grid2D((20, 20), defaultValue=2)
    test = {'grid': grid, 'entities': {0: {'loc': (15, 5), 'viewdir': 10}, 1: {'image': 'blue', 'loc': (15, 10)}}}
    res = encoder.encode(test)

    end_time = time.time()  # End timer
    elapsed_time = end_time - start_time
    print("Encoding completed in {:.4f} seconds.".format(elapsed_time))
    return res

if __name__ == "__main__":
    main()
