class Prefab:
    def __init__(self,prefab_id, map_data, char_to_tile):
        self.prefab_id = prefab_id
        self.map_data = map_data
        self.char_to_tile = char_to_tile

    @property
    def h(self):
        return len(self.map_data[0])
    @property
    def w(self):
        return len(self.map_data)

    def get_map_data(self,rng=0):
        data = []
        for s in self.map_data:
            row=[]
            for char in s:
                if char in self.char_to_tile:
                    row.append(self.char_to_tile[char])
                else:
                    row.append(None)
            data.append(row)
        return data
