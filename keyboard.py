keyboard_device = "/dev/input/event2"  # Replace X with the appropriate device number

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break

        # Extract values from the event data
        a,b,c = (
            int.from_bytes(event_data[i:i + 8], byteorder='little')
            for i in range(0, event_size, 8)
        )

        print(a,b,c)