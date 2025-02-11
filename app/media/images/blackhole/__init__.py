from pathlib import Path


RANDOM = [
    Path(__file__).resolve().parent / f"blackhole{i}.png" for i in range(1, 8)
]
