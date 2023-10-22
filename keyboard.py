keyboard_device = "/dev/input/event2"

KEYS = {
    26880: "LEFT",
    27648: "DOWN",
    27136: "RIGHT",
    26368: "UP",
}

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event (bytes)

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break
        data = bytearray(event_data)
        
        evtype  = int.from_bytes(bytes(data[17:20]), byteorder='little')
        code    = int.from_bytes(bytes(data[20:23]), byteorder='little')
        value   = int.from_bytes(bytes(data[23:]), byteorder='little')

        print(
            f"Type: {KEYS[evtype] if evtype in KEYS else evtype} - Code: {code} - Value: {value}"
            )