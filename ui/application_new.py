"""
Backward Compatibility Launcher
This script maintains the original interface while using the new architecture.
"""
from application_refactored import main

# For backward compatibility
def window():
    """Original function name for backward compatibility."""
    main()

if __name__ == "__main__":
    window()
