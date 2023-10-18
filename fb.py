WIDTH = 1360
HEIGHT = 768
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")


def writePixel(x: int, y: int, byte: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = (y * WIDTH + x) * BYTES_PER_PIXEL + (40 * y)
        SYS_VIDEO_BUFFER.seek(position)
        SYS_VIDEO_BUFFER.write(byte)

# def getBufferSize() -> int:
#     return len(getCurrentBuffer())/4

# def getCurrentBuffer() -> bytes:
#     return bytes(SYS_VIDEO_BUFFER)

# def writeBuffer(Bytes: bytes, position: int = 0) -> None:
#     SYS_VIDEO_BUFFER.seek(position)
#     SYS_VIDEO_BUFFER.write(Bytes)
#     SYS_VIDEO_BUFFER.seek(0)

# def clearBuffer(Bytes: bytes = b'\x00') -> None:
#     writeBuffer(Bytes*(WIDTH*HEIGHT*BYTES_PER_PIXEL))