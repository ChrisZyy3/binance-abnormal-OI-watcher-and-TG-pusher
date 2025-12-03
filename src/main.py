from __future__ import annotations

import asyncio
import logging
import sys

from .config import load_config
from .oi_monitor import OIMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    config = load_config()
    monitor = OIMonitor(config)
    try:
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        print("Stopped by user", file=sys.stderr)


if __name__ == "__main__":
    main()
