# private
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
def safe_format(value, width=8, precision=2, default="   N/A  "):
    try:
        return f"{value:>{width}.{precision}f}"
    except (TypeError, ValueError):
        return default

class _Getch:
    def __init__(self):
        try:
            # Try the cbreak version first
            self.impl = _GetchUnixCBreak()
        except ImportError:
            # Fallback for non-Unix (Windows)
            self.impl = _GetchWindows()
        except termios.error:
            # Fallback if stdin is not a tty (e.g., piped input)
            # or if setcbreak fails for other reasons.
            # You might want a different fallback here,
            # maybe one that reads a line?
            # For now, let's try the original raw mode as a second fallback
            print("Warning: setcbreak failed, falling back to setraw.", file=sys.stderr)
            try:
                self.impl = _GetchUnix() # Original raw mode class
            except ImportError:
                 self.impl = _GetchWindows()


    def __call__(self): return self.impl()
# class _Getch:
#     """Gets a single character from standard input.  Does not echo to the
# screen."""
#     def __init__(self):
#         try:
#             self.impl = _GetchUnix()
#         except ImportError:
#             self.impl = _GetchWindows()
#     def __call__(self): return self.impl()


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

class _GetchUnixCBreak:
    def __init__(self):
        import sys, tty, termios

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # Use cbreak instead of raw
            tty.setcbreak(sys.stdin.fileno())
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
def format_bytes(size):
    """Converts bytes to a human-readable format (KB, MB, GB, etc.), handling negative values."""
    if size is None:
        return "N/A"
    if size == 0:
        return "0 B" # Handle zero case explicitly

    sign = "-" if size < 0 else ""
    size = abs(size)

    # Define the units and their corresponding byte values
    power = 2**10 # 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'} # Start label with 'B'

    # Find the appropriate unit
    while size >= power and n < len(power_labels) - 1:
        size /= power
        n += 1

    # Format the output, adding the sign back if needed
    return f"{sign}{size:.2f} {power_labels[n]}"
def colorPrint(print_string, color = "w", end="\n"):
    print(print_string, end=end)
def printfun(it, s='', e='\n'):
    for i in it:
        print(s + i + e)
getch = _Getch()

if __name__ == '__main__':
    print("getchar test")
