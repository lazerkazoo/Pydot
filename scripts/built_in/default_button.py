from typing import Callable, Union
from scripts.built_in.text import Text
import pygame


class Button(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connected: list[Callable] = []

    def connect(self, todo: Callable):
        self.connected.append(todo)

    def is_pressed(self, pos: tuple = None) -> bool:
        if pos is None:
            pos = pygame.mouse.get_pos()

        x, y = pos
        is_clicked = self.rect.collidepoint(x, y)

        if is_clicked:
            # Execute all connected callbacks
            for callback in self.connected:
                callback()

        return is_clicked

    def handle_click(self, mouse_pos: tuple) -> bool:
        return self.is_pressed(mouse_pos)

    def check_collision(self, other: Union[tuple, pygame.Rect]) -> bool:
        if isinstance(other, tuple):
            return self.rect.collidepoint(other)
        elif isinstance(other, pygame.Rect):
            return self.rect.colliderect(other)
        return False
