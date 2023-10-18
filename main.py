import fb

def drawSquare(size: int, start_x: int, start_y: int, Byte: bytes):
    for j in range(start_y, start_y + size):
        for i in range(start_x, start_x + size):
            fb.writePixel(i, j, Byte)
    fb.syncBuffers()

drawSquare(100,0,0,b'\x00\xff\xff\x00')
drawSquare(100,100,0,b'\x44\xfe\xd2\x00')
drawSquare(400,200,0,b'\x00\x00\xFF\x00')
drawSquare(200,0,100,b'\xFF\x00\x00\x00')