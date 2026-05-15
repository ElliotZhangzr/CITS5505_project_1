import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "tests" / "unit"


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = loader.discover(str(TEST_DIR), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
