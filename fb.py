WIDTH = 1280
HEIGHT = 800
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
LOCAL_BUFFER = SYS_VIDEO_BUFFER.read()

def writePixel(x: int, y: int, byte: bytes, local_buff = True):
    global LOCAL_BUFFER
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = (y * WIDTH + x) * BYTES_PER_PIXEL
        if local_buff:
            LOCAL_BUFFER = LOCAL_BUFFER[:position] + byte + LOCAL_BUFFER[position+1:]
        else:
            SYS_VIDEO_BUFFER.seek(position)
            SYS_VIDEO_BUFFER.write(byte)

def writeBuffer(Bytes: bytes, position: int = 0) -> None:
    SYS_VIDEO_BUFFER.seek(position)
    SYS_VIDEO_BUFFER.write(Bytes)

def syncBuffers() -> None:
    SYS_VIDEO_BUFFER.seek(0)
    SYS_VIDEO_BUFFER.write(LOCAL_BUFFER)


# def getBufferSize() -> int:
#     return len(getCurrentBuffer())/4

# def getCurrentBuffer() -> bytes:
#     return bytes(SYS_VIDEO_BUFFER)


# def clearBuffer(Bytes: bytes = b'\x00') -> None:
#     writeBuffer(Bytes*(WIDTH*HEIGHT*BYTES_PER_PIXEL))