import pygame
import numpy as np
from time import time, sleep

class EmulatedFrameBuffer:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.image_buffer = np.zeros((self.WIDTH, self.HEIGHT, 3), dtype=np.uint8)

    def init_pygame(self):
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
    
    def renderBuffer(self):
        pygame.surfarray.blit_array(self.screen, self.image_buffer)
        pygame.display.flip()

    def writeToBuffer(self, color):
        self.image_buffer[:, :, 0] = color[0]
        self.image_buffer[:, :, 1] = color[1]
        self.image_buffer[:, :, 2] = color[2]

def main():
    fb0 = EmulatedFrameBuffer(1600, 900)
    pygame.init()

    times = []
    cycles = 10
    fb0.init_pygame()

    colours = [
        b'\xFF\x00\x00\xFF',  # Red
        b'\x00\xFF\x00\xFF',  # Green
        b'\x00\x00\xFF\xFF',  # Blue
    ]

    for i in range(cycles):
        start = time()
        fb0.writeToBuffer(colours[i % 3])
        fb0.renderBuffer()
        sleep(0.5)
        times.append(round(time() - start, 3))

    print(round(sum(times) / cycles, 5))

    pygame.quit()

if __name__ == "__main__":
    main()
