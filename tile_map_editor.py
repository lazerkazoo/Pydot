from sys import exit

import pygame


class TileMapEditor:
    def __init__(self, tile_size: int, image: str):
        pygame.init()
        self.win = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        pygame.display.set_caption("Tile Map Editor")

        self.tile_size = tile_size
        self.tiles = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]

        self.image = pygame.image.load(image)

        while True:
            self.handle_events()
            self.draw()

    def draw(self):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def load_tiles_with_image(self):
        img_width, img_height = self.image.get_size()
        for i in range(0, img_height, self.tile_size):
            for j in range(0, img_width, self.tile_size):
                tile = self.image.subsurface((j, i, self.tile_size, self.tile_size))
                # Check if tile is not fully transparent
                if pygame.Surface.get_alpha(tile):
                    pixels = pygame.surfarray.pixels_alpha(tile)
                    if pixels.any():
                        grid_x = j // self.tile_size
                        grid_y = i // self.tile_size
                        if 0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height:
                            self.tiles[grid_y][grid_x] = 1
