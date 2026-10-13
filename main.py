"""Entry point. Run:  python main.py"""
import os
import traceback

import pygame

import core
from game import main

if __name__ == "__main__":
    try:
        main()
    except Exception:
        crash_path = os.path.join(core.BASE_DIR, "crash_log.txt")
        try:
            with open(crash_path, "w", encoding="utf-8") as crash_file:
                traceback.print_exc(file=crash_file)
        except OSError:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
        raise
