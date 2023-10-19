WIDTH = 1280
HEIGHT = 800
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
LOCAL_BUFFER = SYS_VIDEO_BUFFER.read()
LOCAL_QUEUE = {}

COLOURS = {
    "RED":         b'\x00\x00\xFF\x00',
    "GREEN":       b'\x00\xFF\x00\x00',
    "BLUE":        b'\xFF\x00\x00\x00',
    "PURPLE":      b'\xFF\x00\xFF\x00',
    "WHITE":       b'\xFF\xFF\xFF\x00',
    "BLACK":       b'\x00\x00\x00\x00',
    "PASTEL_PINK": b'\xFC\xCF\xF6\x00'
}

def getPosition(x: int, y: int):
    return (y * WIDTH + x) * BYTES_PER_PIXEL

def writePixel(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = getPosition(x,y)
        SYS_VIDEO_BUFFER.seek(position)
        SYS_VIDEO_BUFFER.write(Bytes)

def writeBuffer(Bytes: bytes, position: int = 0) -> None:
    SYS_VIDEO_BUFFER.seek(position)
    SYS_VIDEO_BUFFER.write(Bytes)

def queueLocalChange(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT: # Doesn't write if negative or above screen size
        position = getPosition(x,y)
        LOCAL_QUEUE[position] = Bytes
        
def updateLocalBuffer() -> None:
    global LOCAL_BUFFER
    buffer_list = bytearray(LOCAL_BUFFER)
    for position in LOCAL_QUEUE:
        buffer_list[position:position+BYTES_PER_PIXEL] = LOCAL_QUEUE[position]
    LOCAL_BUFFER = bytes(buffer_list)

def syncBuffers() -> None:
    SYS_VIDEO_BUFFER.seek(0)
    SYS_VIDEO_BUFFER.write(LOCAL_BUFFER)

def clearFrameBuffer(Bytes: bytes = b'\x00\x00\x00\x00') -> None:
    for i in range(WIDTH):
        for j in range(HEIGHT):
            queueLocalChange(i,j,Bytes)
    updateLocalBuffer()
    syncBuffers()

def initTerminal() -> None:
    print("\x1b[2J\x1b[H",end="")
    # clearFrameBuffer()
    print("\n"*(HEIGHT//14))

def drawSquare(size: int, start_x: int, start_y: int, colour: bytes) -> None:
    for j in range(start_y, start_y + size):
        for i in range(start_x, start_x + size):
            queueLocalChange(i, j, colour)


def drawRectangle(size_x: int, size_y: int, start_x: int, start_y: int, colour: bytes) -> None:
    for j in range(start_y, start_y + size_x):
        for i in range(start_x, start_x + size_y):
            queueLocalChange(i, j, colour)

def drawLine(start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes, thickness: int = 3) -> None:
    m = (end_y-start_y)/(end_x-start_x)
    c = (start_x*end_x-end_y*start_x)/(end_x-start_x)
    for x in range(end_x-start_x):
        for i in range(thickness):
            y = round(m*(x+start_x+i)+c)
            queueLocalChange(x,y,colour)
            queueLocalChange(x,y-(i*2),colour) # Nice :)

def drawCircle(center_x: int, center_y: int, radius: int, colour: bytes, thickness: int) -> None:
    """
    TODO: While this isn't too bad, find another way eventually
    """
    e = -radius
    x = radius
    y = 0
    while y < x:
        for i in range(thickness):
            # TODO: Find optimizations for this, especially thickness
            for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (x*x_sign) + i, center_y + (y*y_sign) + i, colour)
            for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (y*y_sign) + i, center_y + (x*x_sign) + i, colour)
            for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (x*x_sign) - i, center_y + (y*y_sign) - i, colour)
            for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (y*y_sign) - i, center_y + (x*x_sign) - i, colour)
        e+=2*y+1
        y+=1
        if e >= 0:
            e -2*x-1
            x-=1

def debug() -> None:
    """
    For debugging
    """
    initTerminal()
    drawSquare(100,0,0,COLOURS["RED"])
    drawSquare(100,100,0,COLOURS["GREEN"])
    drawSquare(400,200,0,COLOURS["BLUE"])
    drawSquare(200,0,100,COLOURS["PURPLE"])
    drawRectangle(100,500,0,400,COLOURS["GREEN"])
    drawLine(0,0,200,200,COLOURS["WHITE"])
    drawCircle(300,150,30,COLOURS["PASTEL_PINK"])
    updateLocalBuffer()
    syncBuffers()

if __name__ == "__main__":
    debug()