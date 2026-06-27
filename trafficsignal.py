import time
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

while True:
    clear_screen()
    print("🔴")
    print("STOP")
    time.sleep(10)


    clear_screen()
    print("🟡")
    print("GET REDY")
    time.sleep(5)

    clear_screen()
    print("🟢")
    print("GO")
    time.sleep(10)