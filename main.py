import argparse

from game.engine import GameEngine


def parse_args():
    parser = argparse.ArgumentParser(description="Run PyGameGame")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable developer mode with per-frame debug logging",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    GameEngine(dev_mode=args.dev).run()
