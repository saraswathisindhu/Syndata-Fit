
import csv
import json
import os
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Automatically locate the dataset
DATASET_CANDIDATES = [
    (
        BASE_DIR / "Syndata_Output",
        BASE_DIR / "visualized_frames"
    ),
    (
        BASE_DIR.parent / "New folder" / "Syndata_Output",
        BASE_DIR / "visualized_frames"
    ),
    (
        BASE_DIR / "sample_dataset",
        BASE_DIR / "sample_dataset" / "visualizations"
    )
]
DATASET = None
VISUALIZATION_FOLDER = None

for dataset_path, visualization_path in DATASET_CANDIDATES:

    if (
        (dataset_path / "images").is_dir()
        and (dataset_path / "annotations").is_dir()
        and visualization_path.is_dir()
    ):
        DATASET = dataset_path
        VISUALIZATION_FOLDER = visualization_path
        break

if DATASET is None:
    raise FileNotFoundError(
        "Dataset or visualization folders not found."
    )

IMAGE_FOLDER = DATASET / "images"
ANNOTATION_FOLDER = DATASET / "annotations"

# Manifest output
MANIFEST_PATH = BASE_DIR / "manifest.csv"

rows = []
errors = []

# Find available images
image_files = sorted(IMAGE_FOLDER.glob("frame_*.png"))

for image_path in image_files:

    try:
        frame_number = int(
            image_path.stem.replace("frame_", "")
        )

        filename = f"frame_{frame_number:04d}"

        annotation_path = (
            ANNOTATION_FOLDER / f"{filename}.json"
        )

        visualization_path = (
            VISUALIZATION_FOLDER /
            f"{filename}_skeleton.png"
        )

        # Check annotation
        if not annotation_path.exists():
            errors.append(f"Missing annotation: {filename}")
            continue

        # Check visualization
        if not visualization_path.exists():
            errors.append(f"Missing visualization: {filename}")
            continue

        # Read annotation information
        with open(
            annotation_path, "r", encoding="utf-8"
        ) as file:
            data = json.load(file)

        # Store paths relative to project folder
        rows.append({
            "frame": frame_number,
            "action": data["action"],
            "joint_count": len(data["joints"]),
            "image": os.path.relpath(
                image_path.resolve(), BASE_DIR
            ),
            "annotation": os.path.relpath(
                annotation_path.resolve(), BASE_DIR
            ),
            "visualization": os.path.relpath(
                visualization_path.resolve(), BASE_DIR
            )
        })

    except Exception as error:
        errors.append(
            f"{image_path.name}: {error}"
        )

# Write CSV
columns = [
    "frame",
    "action",
    "joint_count",
    "image",
    "annotation",
    "visualization"
]

with open(
    MANIFEST_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=columns
    )
    writer.writeheader()
    writer.writerows(rows)

# Final report
print("\n===== SYNDATA-FIT MANIFEST =====")
print("Dataset:", DATASET.resolve())
print("Frames found:", len(image_files))
print("Total records:", len(rows))
print("Errors:", len(errors))

for error in errors:
    print(error)

if len(rows) == len(image_files) and len(image_files) > 0 and len(errors) == 0:
    print("SUCCESS: Manifest created for all available frames!")
else:
    print("WARNING: Check missing files or processing errors.")

print("Manifest:", MANIFEST_PATH)

