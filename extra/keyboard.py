KEYBOARD_DEVICE = "/dev/input/event2"
KEYS = {
    27648: "DOWN",
    27136: "RIGHT",
    26880: "LEFT",
    26368: "UP",
    7168:  "ENTER",
    256:   "ESC",
}
STATES = {}
for i in KEYS: STATES[i] = 0
UNKNOWN_EVENT = 1024
EVENT_SIZE = 24

with open(KEYBOARD_DEVICE, "rb") as f:
    while True:
        event_data = f.read(EVENT_SIZE)
        if len(event_data) != EVENT_SIZE:
            break
        data = bytearray(event_data)
        evtype  = int.from_bytes(bytes(data[17:20]), byteorder='little')
        if evtype and evtype!=UNKNOWN_EVENT:
            code    = int.from_bytes(bytes(data[20:23]), byteorder='little')
            print("\x1b[2J\x1b[H",end="")
            print(f"Type: {KEYS[evtype] if evtype in KEYS else evtype} - Code: {'PRESSED' if code else 'RELEASED'}       ",end="\r")