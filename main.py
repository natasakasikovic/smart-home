import sys
from controllers import pi1 

def main():
    if len(sys.argv) > 1:
        pi = sys.argv[1].upper()
    else:
        pi = "PI1"

    if pi == "PI1":
        pi1.run()
    else:
        print(f"ERROR: Unknown PI: {pi}")
        print("Usage: python main.py [PI1]")
        sys.exit(1)

if __name__ == "__main__":
    main()