with open('/sys/class/graphics/fb0/virtual_size') as size_file:
    WIDTH, HEIGHT = [int(i) for i in size_file.read().split(',')]
size_file.close()
del size_file

with open('/sys/class/graphics/fb0/bits_per_pixel') as bits_file:
    BYTES_PER_PIXEL = int(bits_file.read()) // 8
bits_file.close()
del bits_file

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
    "YELLOW"     : b'\x00\xFF\xFF\x00',
    "PASTEL_PINK": b'\xFC\xCF\xF6\x00',
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

def updateFrameBuffer() -> None:
    updateLocalBuffer()
    syncBuffers()

def clearFrameBuffer(Bytes: bytes = b'\x00\x00\x00\x00') -> None:
    for i in range(WIDTH):
        for j in range(HEIGHT):
            queueLocalChange(i,j,Bytes)
    updateFrameBuffer()

def initTerminal() -> None:
    print("\x1b[2J\x1b[H",end="")
    clearFrameBuffer()
    print("\n"*(HEIGHT//14))

def drawSquare(size: int, start_x: int, start_y: int, colour: bytes) -> None:
    for j in range(start_y, start_y + size):
        for i in range(start_x, start_x + size):
            queueLocalChange(i, j, colour)


def drawRectangle(start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes) -> None:
    for j in range(start_y, end_y):
        for i in range(start_x, end_x):
            queueLocalChange(i, j, colour)

def drawLine(start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes, thickness: int = 3) -> None:
    if start_x > end_x:
        start_x, end_x = end_x, start_x
        start_y, end_y = end_y, start_y
    slope = (end_y - start_y) / (end_x - start_x)
    intercept = start_y - slope * start_x
    for x in range(start_x, end_x + 1):
        for i in range(thickness):
            y = round(slope * (x+start_x+i) + intercept)
            queueLocalChange(x, y, colour)
            queueLocalChange(x, y - thickness, colour)


def drawCircle(center_x: int, center_y: int, radius: int, colour: bytes, thickness: int = 3) -> None:
    """
    TODO: While this isn't too bad, find another way eventually
    """
    e = -radius
    x = radius
    y = 0
    while y < x:
        for i in range(thickness):
            # TODO: Find optimizations for this, especially thickness
            # NOTE: Too much math for thickness on x, so nah I'm good
            for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (x*x_sign), center_y + (y*y_sign) + i, colour)
            for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (y*y_sign), center_y + (x*x_sign) + i, colour)
            for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (x*x_sign), center_y + (y*y_sign) - i, colour)
            for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                queueLocalChange(center_x + (y*y_sign), center_y + (x*x_sign) - i, colour)
        e+=2*y+1
        y+=1
        if e >= 0:
            e -2*x-1
            x-=1


def readImage(filePath:str, start_x:int =0, start_y:int =0) -> None:
    # TODO: Add a way to add the image to a specific spot on the screen
    if filePath.endswith(".zeke"):
        try:
            image = open(filePath, "rb")
            data = bytearray(image.read())
            width = int.from_bytes(data[0:2], byteorder='little')
            height = int.from_bytes(data[2:4], byteorder='little')
            cursor = 4
            for y in range(height):
                for x in range(width):
                    queueLocalChange(x+start_x,y+start_y,data[cursor:cursor+4])
                    cursor+=4
        except FileNotFoundError as e:
            raise e
    else:
        raise TypeError("File format not supported")

def debug() -> None:
    """
    For debugging
    """
    # initTerminal()
    drawSquare(100,0,0,COLOURS["RED"])
    drawSquare(100,100,0,COLOURS["GREEN"])
    drawSquare(400,200,0,COLOURS["BLUE"])
    drawSquare(200,0,100,COLOURS["PURPLE"])
    drawRectangle(400,200,1200,400,COLOURS["YELLOW"])
    drawLine(0,0,200,200,COLOURS["WHITE"])
    drawCircle(300,150,150,COLOURS["PASTEL_PINK"],thickness=3)

def drawTicTacToeBoard(x_offset: int = 0, y_offset: int = 0) -> None:
    # TODO: Make some math logic that will detemine board size and render it accoding to variables
    initTerminal()
    board_size = 500
    line_thickness = 5
    line_offset = [
        1/6,
        1/2,
        5/6
    ]

    midpoint_offset = [
        .33,
        .66,
        1
    ]
    cross_lookup = [
        [
            [
                x_offset,
                y_offset,
                x_offset+round(board_size*midpoint_offset[0]),
                y_offset+round(board_size*midpoint_offset[0])
            ],
            [
                x_offset,
                y_offset+round(board_size*midpoint_offset[0]),
                x_offset+round(board_size*midpoint_offset[0]),
                y_offset,
            ]
        ],
    ]
    circle_lookup = [
            [0,0], [1,0], [2,0],
            [0,1], [1,1], [2,1],
            [0,2], [1,2], [2,2]
    ]

    def o(index: int) -> None:
        x, y = [round(board_size * line_offset[i]) for i in circle_lookup[index]]
        drawCircle(x,y,round(board_size/10),COLOURS["WHITE"])
    
    def x(index: int) -> None:
        for line in cross_lookup[index]:
            print(line)
            start_x, start_y, end_x, end_y = line
            drawLine(start_x,start_y,end_x,end_y,COLOURS["WHITE"])

    for i in [0.33,0.66]:
        offset = round(board_size * i)
        drawRectangle(0,offset,board_size, offset+line_thickness, COLOURS["WHITE"])
        drawRectangle(offset,0,offset+line_thickness,board_size,COLOURS["WHITE"])

    for i in range(1,4):
        o(i)
    
    x(0)
    updateFrameBuffer()

if __name__ == "__main__":
    drawTicTacToeBoard()