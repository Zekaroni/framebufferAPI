import pygame
import numpy as np
from time import time

class EmulatedFrameBuffer:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.BYTES_PER_PIXEL = 4
        self.TOTAL_BYTES = self.WIDTH * self.HEIGHT * self.BYTES_PER_PIXEL
        self.image_buffer = bytearray(b'\x00\x00\x00\xFF' * self.TOTAL_BYTES)  # Initialize with transparent black

    def init_pygame(self):
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
    
    def render_rgba_byte_array(self):
        image_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pixel_array = pygame.PixelArray(image_surface)
        return image_surface    

    def renderBuffer(self):
        pass

    def writeToBuffer(self, color):
        self.image_buffer = bytearray(color * self.TOTAL_BYTES)


def main():
    fb0 = EmulatedFrameBuffer(1600, 900)
    pygame.init()
    fb0.init_pygame()
    colours = [
        b'\xFF\x00\x00\xFF',  # Red
        b'\x00\xFF\x00\xFF',  # Green
        b'\x00\x00\xFF\xFF',  # Blue
    ]
    times = []
    cycles = 5000

    fb0.render_rgba_byte_array()
    for i in range(cycles):
        start = time()
        fb0.writeToBuffer(colours[i % 3])
        fb0.renderBuffer()
        times.append(round(time() - start, 3))
    print(sum(times) / cycles)
    pygame.quit()

if __name__ == "__main__":
    main()