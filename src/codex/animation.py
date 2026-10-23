import os, time, sys

C = "\033[96m" # Sky Blue
B = "\033[1m"  # Bold
X = "\033[0m"  # Reset

# Frames where the letters build up one by one
FRAMES = [
    f"""{C}{B}
      ▄████▄
    {X}""",
    f"""{C}{B}
      ▄████▄   ▒█████
    {X}""",
    f"""{C}{B}
      ▄████▄   ▒█████  ▓█████▄
    {X}""",
    f"""{C}{B}
      ▄████▄   ▒█████  ▓█████▄ ▓█████
    {X}""",
    f"""{C}{B}
      ▄████▄   ▒█████  ▓█████▄ ▓█████ ▒██   ██▒
      ▒██▀ ▀█  ▒██▒  ██▒▒██▀ ██▌▓█   ▀ ▒▒ █ █ ▒░
      ▒▓█    ▄ ▒██░  ██▒░██   █▌▒███   ░░  █   ░
      ▒▓▓▄ ▄██▒▒██   ██░░▓█▄   ▌▒▓█  ▄  ░ █ █ ▒
      ▒ ▓███▀ ░░ ████▓▒░░▒████▓ ░▒████▒▒██▒ ▒██▒
    {X}"""
]

def play():
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    for frame in FRAMES:
        os.system("clear")
        print(frame)
        time.sleep(0.15)  # Speed of the animation
        
    time.sleep(0.4) # Pause at the end so you can see it
    
    # Show cursor again
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
