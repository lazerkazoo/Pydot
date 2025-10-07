from typing import Callable, Union
from text import Text
import pygame


class Button(Text):
    def connect(self, todo: Callable):
        self.connected.append(todo)

    def is_pressed(
        self, clicked_by: Union[tuple, pygame.Rect] = pygame.mouse.get_pos()
    ) -> None:
        if isinstance(clicked_by, tuple):
            x, y = clicked_by
            if self.rect.collidepoint(x, y):
                for do in self.connected:
                    do()

        elif isinstance(clicked_by, pygame.Rect):
            if self.rect.colliderect(clicked_by):
                for do in self.connected:
                    do()
