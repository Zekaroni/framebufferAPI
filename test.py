r = 255 # FF
g = 170 # AA
b = 51  # 33 # NOTE: If bellow 127, it shows as the ascii char value

def convertRGBtoBGRA(r:int, g:int, b:int) -> bytes:
    r = r << (16)
    g = g << (8)
    return (r + g + b).to_bytes(4,'little')

print(convertRGBtoBGRA(r,g,b))