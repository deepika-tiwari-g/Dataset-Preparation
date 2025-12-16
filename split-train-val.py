#!/usr/bin/env python3
import os
import random
import shutil
from collections import defaultdict
from pathlib import Path

# Configuration
ROOT = Path(__file__).resolve().parent
TRAIN_DIR = ROOT / "train"
VAL_DIR = ROOT / "val"
# ROOT = "/home/deepika/Downloads/billets/frames"
# TRAIN_DIR = f"{ROOT}/train"
# VAL_DIR = f"{ROOT}/val"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
VAL_RATIO = 0.20  # 20%
SEED = 42

random.seed(SEED)


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def get_label_from_name(name: str) -> str:
    # Simple heuristic: look for 'Day' or 'Night' token in filename (case-insensitive)
    lower = name.lower()
    if "night" in lower:
        return "Night"
    return "Day"


def collect_images_by_label(root: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    for entry in root.iterdir():
        if not is_image_file(entry):
            continue
        label = get_label_from_name(entry.name)
        groups[label].append(entry)
    return groups


def split_indices(n: int, val_ratio: float) -> tuple[list[int], list[int]]:
    idx = list(range(n))
    random.shuffle(idx)
    val_count = max(1 if n > 0 else 0, int(round(n * val_ratio))) if n > 0 else 0
    val_idx = set(idx[:val_count])
    train_idx = [i for i in idx if i not in val_idx]
    return train_idx, list(val_idx)


def ensure_clean_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_files(files: list[Path], dest_dir: Path) -> None:
    for src in files:
        dest = dest_dir / src.name
        # If name collision happens, add numeric suffix
        if dest.exists():
            stem, ext = src.stem, src.suffix
            k = 1
            while True:
                alt = dest_dir / f"{stem}_{k}{ext}"
                if not alt.exists():
                    dest = alt
                    break
                k += 1
        shutil.copy2(src, dest)


def main() -> None:
    # Prepare output dirs
    ensure_clean_dir(TRAIN_DIR)
    ensure_clean_dir(VAL_DIR)

    images_by_label = collect_images_by_label(ROOT)

    train_files: list[Path] = []
    val_files: list[Path] = []

    for label, files in images_by_label.items():
        if not files:
            continue
        train_idx, val_idx = split_indices(len(files), VAL_RATIO)
        train_files.extend([files[i] for i in train_idx])
        val_files.extend([files[i] for i in val_idx])

    copy_files(train_files, TRAIN_DIR)
    copy_files(val_files, VAL_DIR)

    print(f"Done. Train: {len(train_files)} images, Val: {len(val_files)} images.")


if __name__ == "__main__":
    main()

