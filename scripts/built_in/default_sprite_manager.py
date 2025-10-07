import pygame as pydot
from pygame.surface import Surface


class Sprite:
    def __init__(self, image: str, x: int, y: int):
        self.x = x
        self.y = y
        self.image = pydot.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class SpriteFromSheet:
    def __init__(self, sheet: str, x: int, y: int, width: int, height: int):
        self.sheet_image = pydot.image.load(sheet).convert_alpha()

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.surface = pydot.Surface((width, height), pydot.SRCALPHA)
        self.rect = self.surface.get_rect(center=(x, y))
        self.surface.blit(self.sheet_image, (0, 0), (0, 0, width, height))

    def update(self):
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class SheetAnimManager:
    def __init__(
        self,
        sheet: str,
        x: int,
        y: int,
        width: int,
        height: int,
        frame_rate: int,
        anims: list[tuple[str, int]],
    ) -> None:
        self.sheet = sheet

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.frame_rate = frame_rate
        self.frame = 0
        self.current_frame = 0
        self.anims: list[tuple[str, int]] = anims
        self.current_anim = anims[0] if anims else ("", 0)

        # Cache all animation frame images
        self.anim_cache: dict[str, Surface] = {}
        for anim_name, frame_count in anims:
            for frame_idx in range(frame_count):
                # Assuming animation frames follow a naming pattern
                self.anim_cache[f"{anim_name}_{frame_idx}"] = pydot.image.load(
                    f"{anim_name}_{frame_idx}.png"
                ).convert_alpha()

        self.surface = pydot.Surface((width, height), pydot.SRCALPHA)
        self.rect = self.surface.get_rect(center=(x, y))

    def update(self):
        self.rect.center = (self.x, self.y)

    def draw(self, surface: Surface):
        self.frame += 1
        if self.frame >= self.frame_rate:
            self.frame = 0
            self.current_frame += 1
            anim_name, frame_count = self.current_anim
            if self.current_frame >= frame_count:
                self.current_frame = 0

        # Use cached image
        anim_name = self.current_anim[0]
        cache_key = f"{anim_name}_{self.current_frame}"
        if cache_key in self.anim_cache:
            self.surface.fill((0, 0, 0, 0))  # Clear surface
            self.surface.blit(
                self.anim_cache[cache_key],
                (0, 0),
                (0, 0, self.width, self.height),
            )
        surface.blit(self.surface, self.rect)
