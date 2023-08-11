#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Communication with joystick to get the RC commands


from inputs import get_gamepad




def read_keyboard_input(prompt="Enter input: "):
    user_input = input(prompt)
    return user_input

def keyboard_input_thread():
    while True:
        user_input = read_keyboard_input("Please enter your input (or 'exit' to quit): ")
        
        global channels
        #roll_pwm = roll # Channel 1 (Roll) PWM value
        #pitch_pwm = pitch# Channel 2 (Pitch) PWM value
        #throttle_pwm = throttle  # Channel 3 (Throttle) PWM value
        #yaw_pwm = yaw  # Channel 4 (Yaw) PWM value
        
        if user_input.lower() == "exit":
            break
        
        channels = [1500]*18
        if "w" in user_input.lower():
            channels[2] = 2000
        elif "s" in user_input.lower():
            channels[2] = 1000
        elif "a" in user_input.lower():
            channels[3] = 2000
        elif "d" in user_input.lower():
            channels[3] = 1000
        elif "i" in user_input.lower():
            channels[1] = 2000
        elif "k" in user_input.lower():
            channels[1] = 1000
        elif "j" in user_input.lower():
            channels[0] = 2000
        elif "l" in user_input.lower():
            channels[0] = 1000
        
        
        print("You entered:", user_input)









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
