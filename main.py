"""
turkey.app — Entry Point
Run the application using: `reflex run`
"""

import sys
from pathlib import Path

# Ensure the root directory is in sys.path so we can import TurkeyApp correctly
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

try:
    from TurkeyApp.TurkeyApp import app
except ImportError as e:
    print(f"Error: Could not import TurkeyApp. Ensure you are running from the project root.\nDetail: {e}")
    sys.exit(1)

def start():
    """Main execution point if called directly."""
    print("\n  🦃 turkey.app is ready.")
    print("  Run 'reflex run' to start the development server.\n")

if __name__ == "__main__":
    start()
