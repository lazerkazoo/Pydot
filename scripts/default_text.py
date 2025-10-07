from typing import Callable, Union
import pygame


class Text:
    def __init__(
        self,
        font_file: str,
        font_size: int,
        anti_a: bool = True,
        txt_color: str = "black",
        bg_color: str = "white",
    ) -> None:
        self.font = pygame.font.Font(font_file, font_size)
        self.text = ""
        self.last_text = self.text
        self.anti_a = anti_a
        self.txt_color = txt_color
        self.bg_color = bg_color
        self.rendered = self.font.render(self.text, anti_a, txt_color, bg_color)

        self.rect = self.rendered.get_rect()

        self.connected: list[Callable] = []

    def draw(self, screen: pygame.Surface):
        screen.blit(self.rendered, self.rect)
        if self.last_text != self.text:
            self.rendered = self.font.render(
                self.text, self.anti_a, self.txt_color, self.bg_color
            )
