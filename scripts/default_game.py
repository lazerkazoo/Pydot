import pygame as pydot
import main as m


def main():
    pydot.init()
    print("Game starting...")

    if m.fullscreen:
        screen = pydot.display.set_mode((0, 0), pydot.FULLSCREEN)
    else:
        screen = pydot.display.set_mode(m.resolution)
    pydot.display.set_caption("PyDot Game")
    clock = pydot.time.Clock()

    running = True
    while running:
        for event in pydot.event.get():
            if event.type == pydot.QUIT:
                running = False
                print("Game exit requested")

        screen.fill("purple")

        m.main(screen)

        pydot.display.flip()
        clock.tick(m.fps)

    print("Game shutting down...")
    pydot.quit()


main()
