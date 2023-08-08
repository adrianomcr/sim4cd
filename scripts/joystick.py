#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Communication with joystick to get the RC commands


from inputs import get_gamepad

def main():
    print("Reading Xbox joystick inputs. Press Ctrl+C to exit.")

    while True:
        events = get_gamepad()
        
        for event in events:
            print(f"{event.ev_type}: {event.code}: {event.state}")
            print()
            print()
            print()
            #print(event)
            #if event.ev_type == "Absolute":
            #    print(f"{event.ev_type}: {event.code}: {event.state}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
