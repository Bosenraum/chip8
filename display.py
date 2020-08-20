import pygame
import sys

from colors import *
from sprites import *

pygame.init()

SCALE_FACTOR = 10
NATIVE_WIDTH = 64
NATIVE_HEIGHT = 32

DISPLAY_WIDTH = NATIVE_WIDTH * SCALE_FACTOR
DISPLAY_HEIGHT = NATIVE_HEIGHT * SCALE_FACTOR
DISPLAY_SIZE = DISPLAY_WIDTH, DISPLAY_HEIGHT


class Pixel:

    def __init__(self, x, y, on_color=WHITE, scale_factor=SCALE_FACTOR):
        self.x = x
        self.y = y
        self.sf = scale_factor
        # pygame Rect objects use x, y, width, height, so specify our pixel coordinates and the pixel width/height
        self.rect = pygame.Rect(self.x * self.sf, self.y * self.sf, self.sf, self.sf)
        self.state = 0  # initialize to black
        self.on_color = on_color

    # @property
    # def x(self):
    #     return self._x
    #
    # @x.setter
    # def x(self, x):
    #     if 0 <= x < NATIVE_WIDTH:
    #         self._x = x
    #     elif x < 0:
    #         self._x = 0
    #     else:
    #         self._x = NATIVE_WIDTH - 1
    #
    # @property
    # def y(self):
    #     return self._y
    #
    # @y.setter
    # def y(self, y):
    #     if 0 <= y < NATIVE_HEIGHT:
    #         self._y = y
    #     elif y < 0:
    #         self._y = 0
    #     else:
    #         self._y = NATIVE_HEIGHT - 1

    def set(self):
        self.state = 1

    def clear(self):
        self.state = 0

    def toggle(self):
        self.state = not self.state

    def set_color(self, color):
        self.on_color = color

    def draw(self, screen):
        self.rect = pygame.Rect(self.x * self.sf, self.y * self.sf, self.sf, self.sf)
        pygame.draw.rect(screen, self.on_color if self.state else BLACK, self.rect)


def create_pixels(width, height):
    pixels = []
    for x in range(width):
        pixels.append([])
        for y in range(height):
            pixels[x].append(Pixel(x, y))

    return pixels


def draw_sprite(start_x, start_y, sprite, pixels):
    for x in range(4):
        px = x + start_x
        if px >= len(pixels): break # stop if we go off the screen
        for y in range(len(sprite)):
            py = y + start_y
            if py >= len(pixels[px]): break # stop if we go off the screen

            p = pixels[x+start_x][y+start_y]
            sprite_bit = (sprite[y] >> (7 - x)) & 0x1
            if p.state ^ sprite_bit == 0:
                # set the collision flag
                pass
                # vf = 1
            p.state |= sprite_bit


class Display:

    def __init__(self, width, height, scale_factor=SCALE_FACTOR):
        self.width = width
        self.height = height
        self.scale_factor = scale_factor
        self.pixels = create_pixels(self.width, self.height)

    def draw_sprite(self, start_x, start_y, sprite):
        collision = 0
        for x in range(4):
            px = x + start_x
            if px >= len(self.pixels): break  # stop if we go off the screen
            for y in range(len(sprite)):
                py = y + start_y
                if py >= len(self.pixels[px]): break  # stop if we go off the screen

                p = self.pixels[x + start_x][y + start_y]
                sprite_bit = (sprite[y] >> (7 - x)) & 0x1
                if p.state ^ sprite_bit == 0:
                    collision = 1

                p.state |= sprite_bit
        return collision


def main():
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Testing the display only")

    done = False
    clock = pygame.time.Clock()

    my_display = Display(NATIVE_WIDTH, NATIVE_HEIGHT)

    dx, dy = 0, 0

    # Main display loop
    while not done:

        clock.tick(60)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        px = mouse_x // SCALE_FACTOR
        py = mouse_y // SCALE_FACTOR

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # # Handle keypress events
            if event.type == pygame.KEYDOWN:
                # print(f"KEY {event.key} pressed down")
                # Draw the sprite of the key pressed at the current location of the mouse
                if event.key == pygame.K_0: draw_sprite(px, py, CHIP8_SPRITES['0'], pixels)
                elif event.key == pygame.K_1: draw_sprite(px, py, CHIP8_SPRITES['1'], pixels)
                elif event.key == pygame.K_2: draw_sprite(px, py, CHIP8_SPRITES['2'], pixels)
                elif event.key == pygame.K_3: draw_sprite(px, py, CHIP8_SPRITES['3'], pixels)

                elif event.key == pygame.K_4: draw_sprite(px, py, CHIP8_SPRITES['4'], pixels)
                elif event.key == pygame.K_5: draw_sprite(px, py, CHIP8_SPRITES['5'], pixels)
                elif event.key == pygame.K_6: draw_sprite(px, py, CHIP8_SPRITES['6'], pixels)
                elif event.key == pygame.K_7: draw_sprite(px, py, CHIP8_SPRITES['7'], pixels)

                elif event.key == pygame.K_8: draw_sprite(px, py, CHIP8_SPRITES['8'], pixels)
                elif event.key == pygame.K_9: draw_sprite(px, py, CHIP8_SPRITES['9'], pixels)
                elif event.key == pygame.K_a: draw_sprite(px, py, CHIP8_SPRITES['A'], pixels)
                elif event.key == pygame.K_b: draw_sprite(px, py, CHIP8_SPRITES['B'], pixels)

                elif event.key == pygame.K_c: draw_sprite(px, py, CHIP8_SPRITES['C'], pixels)
                elif event.key == pygame.K_d: draw_sprite(px, py, CHIP8_SPRITES['D'], pixels)
                elif event.key == pygame.K_e: draw_sprite(px, py, CHIP8_SPRITES['E'], pixels)
                elif event.key == pygame.K_f: draw_sprite(px, py, CHIP8_SPRITES['F'], pixels)
                else: draw_sprite(px, py, CUSTOM_SPRITES['x'], pixels)

            # process input events

        # if event.type == pygame.MOUSEBUTTONDOWN:
        mouse1, mouse2, mouse3 = pygame.mouse.get_pressed()
        if mouse1 or mouse2 or mouse3:
            p = pixels[px][py]

            # print(f"Mouse button {event.button} pressed")
            if mouse1:
                p.set_color(WHITE)
                p.set()
            elif mouse2:
                p.set_color(GREEN)
                p.set()
            elif mouse3:
                # p.set_color(GREEN)
                p.clear()

        screen.fill(BLACK)

        for px in range(len(pixels)):
            for py in range(len(pixels[px])):
                p = pixels[px][py]
                # p.x += dx
                # p.y += dy
                p.draw(screen)

        pygame.display.flip()
        dx, dy = 0, 0

    pygame.quit()


if __name__ == "__main__":
    main()
