r = 255 # FF
g = 170 # AA
b = 51  # 33 # NOTE: If bellow 127, it shows as the ascii char value

def convertRGBtoBGRA(r:int, g:int, b:int) -> bytes:
    b = b << (16)
    g = g << (8)
    return (b + g + r).to_bytes(4,'little')