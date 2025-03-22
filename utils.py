# private
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchUnix()
        except ImportError:
            self.impl = _GetchWindows()
    def __call__(self): return self.impl()

def save_list(data, filename):
    """Save a list to a plain text file, one item per line."""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"{item}\n")
    # print(f"List saved to {filename}")

def load_list(filename):
    """Load a list from a plain text file, one item per line."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = [line.strip() for line in f]
        # print(f"List loaded from {filename}")
        return data
    except FileNotFoundError:
        # print(f"File {filename} not found.")
        return []

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()
# public api
def colorPrint(print_string, color = "w", end="\n"):
    print(print_string, end=end)
def printfun(it, s='', e='\n'):
    for i in it:
        print(s + i + e)
getch = _Getch()

if __name__ == '__main__':
    print("getchar test")
