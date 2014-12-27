class TileType:
    def __init__(self, tile_type_id, name, char,
                 color, color_not_visible,
                 background, background_not_visible,
                 move_through, see_through):
        self.tile_type_id = tile_type_id,
        self.name = name
        self.char = char

        self.color = color
        self.color_not_visible = color_not_visible
        self.background = background
        self.background_not_visible = background_not_visible

        self.move_through = move_through
        self.see_through = see_through
