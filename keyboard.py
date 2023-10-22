keyboard_device = "/dev/input/event2"

KEYS = {
    27648: "DOWN",
    27136: "RIGHT",
    26880: "LEFT",
    26368: "UP",
    7168:  "ENTER",
    256:   "ESC",
}
UNKNOWN_EVENT = 1024
EVENT_SIZE = 24

with open(keyboard_device, "rb") as f:
    while True:
        event_data = f.read(EVENT_SIZE)
        if len(event_data) != EVENT_SIZE:
            break
        data = bytearray(event_data)
        evtype  = int.from_bytes(bytes(data[17:20]), byteorder='little')
        if evtype and evtype!=UNKNOWN_EVENT:
            code    = int.from_bytes(bytes(data[20:23]), byteorder='little')
            value   = int.from_bytes(bytes(data[23:]), byteorder='little')
            print(
                f"Type: {KEYS[evtype] if evtype in KEYS else evtype} - Code: {code} - Value: {value}       ",
                end="\r"
            )