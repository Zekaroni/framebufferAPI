keyboard_device = "/dev/input/event2"

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event (bytes)

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break
        data = bytearray(event_data)
        
        tv_sec  = data[0:9]
        tv_usec = data[9:17]
        evtype  = data[17:20]
        code    = data[20:23]
        value   = data[23:]

        print(
            f"Type: {evtype}\nCode: {code}\nValue: {value}"
            )