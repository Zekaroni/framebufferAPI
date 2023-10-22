keyboard_device = "/dev/input/event2"

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event (bytes)

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break

        # Parse the event data into its components
        time_sec, time_usec, event_type, event_code, event_value = (
            int.from_bytes(event_data[i:i + 8], byteorder='little')
            for i in range(0, event_size, 8)
        )

        if event_type == 1 and event_value == 1:
            # Key press event
            print(f"Key pressed: Event Code {event_code}")