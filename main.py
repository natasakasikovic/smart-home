import sys
from controllers.pi1 import pi1 
from controllers.pi2 import pi2
from controllers.pi3 import pi3

def main():
    if len(sys.argv) > 1:
        pi = sys.argv[1].upper()
    else:
        pi = "PI1"

    if pi == "PI1":
        pi1.run()
    elif pi == "PI2":
        pi2.run()
    elif pi == "PI3":
        pi3.run()

    else:
        print(f"ERROR: Unknown PI: {pi}")
        print("Usage: python main.py [PI1]")
        sys.exit(1)

if __name__ == "__main__":
    main()