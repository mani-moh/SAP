import pyautogui
import time

# Initialize the toggle state
is_holding = False

# Key to use for toggling the hold state
toggle_key = 't' 

print(f"Press '{toggle_key}' to toggle holding down the 'a' key.")
print("Press 'q' to quit.")

while True:
    # Check if the toggle key is pressed
    if pyautogui.keyUp(toggle_key): # Use keyUp to detect a release for a clean toggle
        is_holding = not is_holding # Flip the toggle state
        print(f"Holding 'a' key: {is_holding}")
        time.sleep(0.2) # Add a small delay to prevent multiple toggles from a single press

    # If holding is enabled, press down the key
    if is_holding:
        pyautogui.keyDown('a') 
    else:
        pyautogui.keyUp('a') # Ensure the key is released if holding is off

    # Check for a quit key
    if pyautogui.keyUp('q'):
        print("Exiting script.")
        break

    time.sleep(0.01) # Small delay to prevent excessive CPU usaget