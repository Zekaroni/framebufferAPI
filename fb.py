class RenderEngine:
    def __init__(self):
        with open('/sys/class/graphics/fb0/virtual_size') as size_file:
            self.WIDTH, self.HEIGHT = [int(i) for i in size_file.read().split(',')]
        size_file.close()
        del size_file
        with open('/sys/class/graphics/fb0/bits_per_pixel') as bits_file:
            self.BYTES_PER_PIXEL = int(bits_file.read()) // 8
        bits_file.close()
        del bits_file
        self.SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
        self.LOCAL_BUFFER = self.SYS_VIDEO_BUFFER.read()
        self.LOCAL_QUEUE = {}
        self.COLOURS = {"RED":b'\x00\x00\xFF\x00',"GREEN":b'\x00\xFF\x00\x00',"BLUE":b'\xFF\x00\x00\x00',"PURPLE":b'\xFF\x00\xFF\x00',"WHITE":b'\xFF\xFF\xFF\x00',"BLACK":b'\x00\x00\x00\x00',"YELLOW":b'\x00\xFF\xFF\x00',"PASTEL_PINK":b'\xFC\xCF\xF6\x00',}
    
    def getPosition(self, x: int, y: int):
        return (y * self.WIDTH + x) * self.BYTES_PER_PIXEL
    
    def writePixel(self, x: int, y: int, Bytes: bytes):
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            position = self.getPosition(x,y)
            self.SYS_VIDEO_BUFFER.seek(position)
            self.SYS_VIDEO_BUFFER.write(Bytes)
    
    def writeToBuffer(self, Bytes: bytes, position: int = 0) -> None:
        self.SYS_VIDEO_BUFFER.seek(position)
        self.SYS_VIDEO_BUFFER.write(Bytes)

    def queueLocalChange(self, x: int, y: int, Bytes: bytes) -> None:
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            position = self.getPosition(x,y)
            self.LOCAL_QUEUE[position] = Bytes

    def updateLocalBuffer(self) -> None:
        buffer_list = bytearray(self.LOCAL_BUFFER)
        for position in self.LOCAL_QUEUE:
            buffer_list[position:position+self.BYTES_PER_PIXEL] = self.LOCAL_QUEUE[position]
        self.LOCAL_BUFFER = bytes(buffer_list)
        self.LOCAL_QUEUE = {}

    def syncBuffers(self) -> None:
        self.SYS_VIDEO_BUFFER.seek(0)
        self.SYS_VIDEO_BUFFER.write(self.LOCAL_BUFFER)

    def updateFrameBuffer(self) -> None:
        self.updateLocalBuffer()
        self.syncBuffers()

    def clearFrameBuffer(self, Bytes: bytes = b'\x00\x00\x00\x00') -> None:
        for i in range(self.WIDTH):
            for j in range(self.HEIGHT):
                self.queueLocalChange(i,j,Bytes)
        self.updateFrameBuffer()

    def initTerminal(self) -> None:
        print("\x1b[2J\x1b[H",end="")
        self.clearFrameBuffer()
        print("\n"*(self.HEIGHT//14))

    def drawRectangle(self, start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes) -> None:
        for j in range(start_y, end_y):
            for i in range(start_x, end_x):
                self.queueLocalChange(i, j, colour)

    def drawLine(self, start_x: int, start_y: int, end_x: int, end_y: int, colour: bytes, thickness: int = 3) -> None:
        slope = (end_y - start_y) / (end_x - start_x)
        c = start_y - slope * start_x
        for x in range(start_x, end_x + 1):
            for i in range(thickness+1):
                y = round(slope * (x+i) + c)
                self.queueLocalChange(x, y, colour)
                self.queueLocalChange(x, y - (i * 2), colour)

    def drawCircle(self, center_x: int, center_y: int, radius: int, colour: bytes, thickness: int = 3) -> None:
        e = -radius
        y = 0
        while y < radius:
            for i in range(thickness):
                # TODO: Streamline these for loops, mostly finished but I feel there can be more
                for x_sign, y_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    [self.queueLocalChange(center_x + (radius*x_sign), center_y + (y*y_sign) + (i*o), colour) for o in [1,-1]]
                for y_sign, x_sign in [[1,1],[1,-1],[-1,1],[-1,-1]]:
                    [self.queueLocalChange(center_x + (y*y_sign), center_y + (radius*x_sign) + (i*o), colour) for o in [1,-1]]
            e+=2*y+1
            y+=1
            if e >= 0:
                e-=2*radius-1
                radius-=1

    def drawImage(self, filePath:str, start_x:int =0, start_y:int =0) -> None:
        if filePath.endswith(".zeke"):
            try:
                image = open(filePath, "rb")
                data = bytearray(image.read())
                width = int.from_bytes(data[0:2], byteorder='little')
                height = int.from_bytes(data[2:4], byteorder='little')
                cursor = 4
                for y in range(height):
                    for x in range(width):
                        self.queueLocalChange(x+start_x,y+start_y,int.to_bytes(int.from_bytes(data[cursor:cursor+3], byteorder='little') << 8, byteorder='little'))
                        cursor+=3
            except FileNotFoundError as e:
                raise e
        else:
            raise TypeError("File format not supported")

def debug() -> None:
    """
    For debugging
    """
    renderer = RenderEngine()

    renderer.initTerminal()
    renderer.drawRectangle(400,200,1200,400,renderer.COLOURS["YELLOW"])
    renderer.drawLine(0,0,200,200,renderer.COLOURS["WHITE"])
    renderer.drawCircle(300,150,150,renderer.COLOURS["PASTEL_PINK"],thickness=3)
    renderer.drawImage("image.zeke", start_x=500, start_y=300)

    renderer.updateFrameBuffer()


if __name__ == "__main__":
    debug()