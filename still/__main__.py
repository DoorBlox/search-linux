"""Launch with python3 -m still from the checkout."""
import sys


def main():
    try:
        from .app import main as run
    except (ImportError, ValueError) as exc:
        print("Still requires GTK4/WebKitGTK6; run ./install-crostini.sh", file=sys.stderr)
        print(f"Import error: {exc}", file=sys.stderr)
        return 2
    return run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
