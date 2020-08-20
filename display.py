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


class Display:

    def __init__(self, width, height, screen, scale_factor=SCALE_FACTOR):
        self.width = width
        self.height = height
        self.screen = screen
        self.scale_factor = scale_factor
        self.pixels = self.create_pixels()

    def get_pixel(self, x, y):
        if 0 <= x < self.width:
            if 0 <= y < self.height:
                return self.pixels[x][y]
            else:
                print(f"Invalid y coord of {y} (max is {self.height - 1})")
        else:
            print(f"Invalid x coord of {x} (max is {self.width -1})")

    # Draw the given sprite to the screen starting at the given x and y coordinates
    # The sprite is a list of bytes, the upper nibble of each contains the sprite info
    def draw_sprite(self, start_x, start_y, sprite):
        collision = 0
        for x in range(4):
            px = x + start_x

            if px >= self.width:
                # wrap around if we go off screen
                px -= self.width

            for y in range(len(sprite)):
                py = y + start_y

                if py >= len(self.pixels[px]):
                    # wrap around if we go off screen
                    py -= self.height

                p = self.pixels[px][py]
                sprite_bit = (sprite[y] >> (7 - x)) & 0x1

                new_state = p.state ^ sprite_bit
                if p.state == 1 and new_state == 0:
                    # print(f"Collision! (x={x}, y={y})")
                    collision = 1

                p.state = new_state

        return collision

    def draw_all(self):
        for col in self.pixels:
            for p in col:
                p.draw(self.screen)

    def clear(self):
        for col in self.pixels:
            for p in col:
                p.set_color(WHITE)
                p.clear()

    def create_pixels(self):
        pixels = []
        for x in range(self.width):
            pixels.append([])
            for y in range(self.height):
                pixels[x].append(Pixel(x, y))

        return pixels


def main():
    screen = pygame.display.set_mode(DISPLAY_SIZE)
    pygame.display.set_caption("Testing the display only")

    done = False
    clock = pygame.time.Clock()

    my_display = Display(NATIVE_WIDTH, NATIVE_HEIGHT, screen)

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
                if event.key == pygame.K_0: my_display.draw_sprite(px, py, CHIP8_SPRITES['0'])
                elif event.key == pygame.K_1: my_display.draw_sprite(px, py, CHIP8_SPRITES['1'])
                elif event.key == pygame.K_2: my_display.draw_sprite(px, py, CHIP8_SPRITES['2'])
                elif event.key == pygame.K_3: my_display.draw_sprite(px, py, CHIP8_SPRITES['3'])

                elif event.key == pygame.K_4: my_display.draw_sprite(px, py, CHIP8_SPRITES['4'])
                elif event.key == pygame.K_5: my_display.draw_sprite(px, py, CHIP8_SPRITES['5'])
                elif event.key == pygame.K_6: my_display.draw_sprite(px, py, CHIP8_SPRITES['6'])
                elif event.key == pygame.K_7: my_display.draw_sprite(px, py, CHIP8_SPRITES['7'])

                elif event.key == pygame.K_8: my_display.draw_sprite(px, py, CHIP8_SPRITES['8'])
                elif event.key == pygame.K_9: my_display.draw_sprite(px, py, CHIP8_SPRITES['9'])
                elif event.key == pygame.K_a: my_display.draw_sprite(px, py, CHIP8_SPRITES['A'])
                elif event.key == pygame.K_b: my_display.draw_sprite(px, py, CHIP8_SPRITES['B'])

                elif event.key == pygame.K_c: my_display.draw_sprite(px, py, CHIP8_SPRITES['C'])
                elif event.key == pygame.K_d: my_display.draw_sprite(px, py, CHIP8_SPRITES['D'])
                elif event.key == pygame.K_e: my_display.draw_sprite(px, py, CHIP8_SPRITES['E'])
                elif event.key == pygame.K_f: my_display.draw_sprite(px, py, CHIP8_SPRITES['F'])
                else: my_display.draw_sprite(px, py, CUSTOM_SPRITES['block'])

            # process input events

        # if event.type == pygame.MOUSEBUTTONDOWN:
        mouse1, mouse2, mouse3 = pygame.mouse.get_pressed()
        if mouse1 or mouse2 or mouse3:
            p = my_display.get_pixel(px, py)

            # print(f"Mouse button {event.button} pressed")
            if mouse1:
                p.set_color(GREEN)
                p.set()
                # my_display.draw_sprite(px, py, CUSTOM_SPRITES['pixel'])
            elif mouse2:
                my_display.clear()
                # my_display.draw_sprite(px, py, CUSTOM_SPRITES['pixel'])
            elif mouse3:
                # p.set_color(GREEN)
                p.clear()

        screen.fill(BLACK)

        my_display.draw_all()

        pygame.display.flip()
        dx, dy = 0, 0

    pygame.quit()


if __name__ == "__main__":
    main()
