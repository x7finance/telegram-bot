from pathlib import Path


RANDOM = [
    Path(__file__).resolve().parent / f"blackhole{i}.jpg" for i in range(1, 8)
]
