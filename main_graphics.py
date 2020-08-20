# consider changing to P5 or something faster
from graphics import *
import time

native_width = 64
native_height = 32
resolution_scale_factor = 10
rsf = resolution_scale_factor

screen_state = []
screen_pixels = []

SCREEN_BLACK = 0
SCREEN_WHITE = 1


def create_screen(width, height):

    local_screen_state = []

    for x in range(width):
        local_screen_state.append([])
        for y in range(height):
            local_screen_state[x].append(SCREEN_BLACK)

    return local_screen_state


def create_pixels(screen, win):
    global rsf

    local_pixels = []

    for x in range(len(screen)):
        local_pixels.append([])
        for y in range(len(screen[x])):
            p1 = Point(x * rsf, y * rsf)
            p2 = Point((x + 1) * rsf, (y + 1) * rsf)
            pixel = Rectangle(p1, p2)
            fill_color = 'black' if screen[x][y] == SCREEN_BLACK else 'white'
            pixel.setFill(fill_color)
            local_pixels[x].append(pixel)
            pixel.draw(win)

    return local_pixels


# update the screen with the given new data
# def update_screen(screen_data):
#     global screen_state, screen_pixels
#     # screen_data is a 2d array that is 64x32 so each element represents a pixel on the output display
#     for x in range(len(screen_state)):
#         for y in range(len(screen_state[x])):
#             # print(f"CurrentState: {screen_state[x][y]}, NewState: {screen_data[x][y]}, ", end="")
#             screen_state[x][y] ^= screen_data[x][y]
#             # print(f"Output: {screen_state[x][y]}")
#             fill_color = 'black' if screen_state[x][y] == SCREEN_BLACK else 'white'
#             screen_pixels[x][y].setFill(fill_color)


def checkerboard(pixels):

    for x in range(len(pixels)):

        for y in range(len(pixels[x])):
            if x % 2 == 0:
                if y % 2 == 0:
                    pixels[x][y].setFill('black')
                else:
                    pixels[x][y].setFill('white')
            else:
                if y % 2 == 0:
                    pixels[x][y].setFill('white')
                else:
                    pixels[x][y].setFill('black')


def main():
    global screen_state, screen_pixels, native_width, native_height, rsf
    # The CHIP-8 has a resolution of 64x32. This would be pretty small to do in just pixels, so each "pixel" of the
    # CHIP-8 will be a square drawn at 10x10 pixels on the actual display

    screen_width = native_width * rsf
    screen_height = native_height * rsf
    win = GraphWin("CHIP-8 Emulator", screen_width, screen_height)

    screen_state = create_screen(native_width, native_height)
    screen_pixels = create_pixels(screen_state, win)

    # update_screen(cur_screen_state)   # Should draw all black pixels
    # win.redraw()
    print("Screen should now be black")
    win.getMouse()

    # cur_screen_state[0][0] = SCREEN_WHITE
    # cur_screen_state[0][native_height-1] = SCREEN_WHITE
    # cur_screen_state[native_width-1][0] = SCREEN_WHITE
    # cur_screen_state[native_width-1][native_height-1] = SCREEN_WHITE

    # Manipulating the pixel color directly is much faster
    # Use this in conjunction with the screen state to quickly update pixels
    # Should consider using something faster than graphics.py as it uses a tk canvas.
    # While simple, this is pretty limiting
    checkerboard(screen_pixels)

    # win.redraw()
    print("Screen should now be a checkerboard pattern")
    win.getMouse()

    # Do stuff here before closing window
    # win.setBackground('black')

    win.getMouse()
    win.close()


if __name__ == "__main__":

    main()