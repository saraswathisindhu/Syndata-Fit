

import csv
import json
import os
from pathlib import Path

# ==========================================
# SYNDATA-FIT MULTI-ACTION MANIFEST
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_CANDIDATES = [
    BASE_DIR.parent / "New folder" / "Syndata_Output",
    BASE_DIR / "Syndata_Output"
]

DATASET_ROOT = next(
    (
        folder for folder in DATASET_CANDIDATES
        if (folder / "jogging").is_dir()
        and (folder / "walking").is_dir()
    ),
    None
)

if DATASET_ROOT is None:
    raise FileNotFoundError(
        "Could not locate the jogging and walking dataset folders."
    )

MANIFEST_PATH = BASE_DIR / "manifest.csv"

rows = []
errors = []

# Process each action separately
for action in ["jogging", "walking"]:

    DATASET = DATASET_ROOT / action

    IMAGE_FOLDER = DATASET / "images"
    ANNOTATION_FOLDER = DATASET / "annotations"
    VISUALIZATION_FOLDER = DATASET / "visualizations"

    if not IMAGE_FOLDER.is_dir():
        errors.append(f"{action}: Images folder missing")
        continue

    if not ANNOTATION_FOLDER.is_dir():
        errors.append(f"{action}: Annotations folder missing")
        continue

    if not VISUALIZATION_FOLDER.is_dir():
        errors.append(f"{action}: Visualizations folder missing")
        continue

    image_files = sorted(IMAGE_FOLDER.glob("frame_*.png"))

    print(f"\nProcessing action: {action}")
    print("Images found:", len(image_files))

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

            if not annotation_path.exists():
                errors.append(
                    f"{action}: Missing annotation {filename}"
                )
                continue

            if not visualization_path.exists():
                errors.append(
                    f"{action}: Missing visualization {filename}"
                )
                continue

            with open(
                annotation_path, "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            if data.get("action") != action:
                errors.append(
                    f"{action}: Incorrect action label in {filename}"
                )
                continue

            if data.get("frame") != frame_number:
                errors.append(
                    f"{action}: Frame number mismatch in {filename}"
                )
                continue

            if len(data.get("joints", {})) != 17:
                errors.append(
                    f"{action}: Incorrect joint count in {filename}"
                )
                continue

            rows.append({
                "frame": frame_number,
                "action": action,
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
                f"{action}/{image_path.name}: {error}"
            )

# Write combined CSV
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
jogging_count = sum(
    1 for row in rows if row["action"] == "jogging"
)

walking_count = sum(
    1 for row in rows if row["action"] == "walking"
)

print("\n===== SYNDATA-FIT MULTI-ACTION MANIFEST =====")
print("Dataset root:", DATASET_ROOT)
print("Jogging records:", jogging_count)
print("Walking records:", walking_count)
print("Total records:", len(rows))
print("Errors:", len(errors))

for error in errors:
    print("ERROR:", error)

if (
    jogging_count == 100
    and walking_count == 100
    and len(rows) == 200
    and len(errors) == 0
):
    print("\nSUCCESS: Both action datasets added to manifest!")
else:
    print("\nWARNING: Check dataset records and errors.")

print("Manifest saved:", MANIFEST_PATH)
