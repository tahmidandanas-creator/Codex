import os, sys, time

R = "\033[91m"; C = "\033[96m"; B = "\033[1m"; X = "\033[0m"

FRAMES = [
r"""
        ██████╗
        ╚════██╗
         █████╔╝
         ╚═══██╗
        ██████╔╝
        ╚═════╝
""",
r"""
     ┌──────────┐
     │  ▓▓▓▓▓▓  │
     │  ▓ X  ▓  │
     │  ▓▓▓▓▓▓  │
     └──────────┘
         ╱╲
        ╱  ╲
       ╱    ╲
      ▕  ▓▓  ▏
      ▕  ▓▓  ▏
""",
r"""
        ╱▔▔▔▔╲
       ╱  ▓X▓ ╲
      ╱   ▓▓   ╲
     │   ▓▓▓▓   │
     │   ▓▓▓▓   │
    ╱│   ▓▓▓▓   │╲
   ╱ │   ▓▓▓▓   │ ╲
  ╱  └──▓▓▓▓──┘  ╲
  ▏   ▓▓▓▓▓▓▓▓   ▏
  ▏   ▓▓▓▓▓▓▓▓   ▏
""",
]

def play(times=1):
    for _ in range(times):
        for frame in FRAMES:
            os.system("clear")
            print(f"{R}{B}{frame}{X}")
            time.sleep(0.4)

if __name__ == "__main__":
    play()
