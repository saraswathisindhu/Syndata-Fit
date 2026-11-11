
import csv
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATASET_CONFIGS = [
    {
        "name": "FULL DATASET",
        "dataset": BASE_DIR / "Syndata_Output",
        "visualizations": BASE_DIR / "visualized_frames",
        "manifest": BASE_DIR / "manifest.csv",
    },
    {
        "name": "FULL DATASET",
        "dataset": BASE_DIR.parent / "New folder" / "Syndata_Output",
        "visualizations": BASE_DIR / "visualized_frames",
        "manifest": BASE_DIR / "manifest.csv",
    },
    {
        "name": "GITHUB SAMPLE",
        "dataset": BASE_DIR / "sample_dataset",
        "visualizations": BASE_DIR / "sample_dataset" / "visualizations",
        "manifest": BASE_DIR / "sample_manifest.csv",
    },
]

EXPECTED_JOINTS = {
    "head", "neck",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_toe", "right_toe", "hips"
}


def audit_dataset(config):

    dataset = config["dataset"]
    image_folder = dataset / "images"
    annotation_folder = dataset / "annotations"
    visualization_folder = config["visualizations"]
    manifest_path = config["manifest"]

    errors = []
    checked_frames = 0

    image_files = sorted(image_folder.glob("frame_*.png"))

    print(f"\n===== {config['name']} AUDIT =====")
    print("Dataset:", dataset.resolve())
    print("Frames found:", len(image_files))

    for image_path in image_files:

        filename = image_path.stem

        try:
            frame_number = int(filename.replace("frame_", ""))
        except ValueError:
            errors.append(f"Invalid image filename: {image_path.name}")
            continue

        json_path = annotation_folder / f"{filename}.json"
        visualization_path = (
            visualization_folder / f"{filename}_skeleton.png"
        )

        if not json_path.exists():
            errors.append(f"Missing annotation: {filename}")
            continue

        if not visualization_path.exists():
            errors.append(f"Missing visualization: {filename}")

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if data.get("frame") != frame_number:
                errors.append(f"Incorrect frame number: {filename}")

            if data.get("action") != "jogging":
                errors.append(f"Unexpected action: {filename}")

            joints = data.get("joints", {})

            if set(joints.keys()) != EXPECTED_JOINTS:
                errors.append(f"Incorrect joint names: {filename}")

            for name, joint in joints.items():

                coords_3d = joint.get("3d")
                coords_2d = joint.get("2d")
                in_frame = joint.get("in_frame")

                if not isinstance(coords_3d, list) or len(coords_3d) != 3:
                    errors.append(
                        f"Invalid 3D coordinates: {filename}, {name}"
                    )
                    continue

                if not isinstance(coords_2d, list) or len(coords_2d) != 2:
                    errors.append(
                        f"Invalid 2D coordinates: {filename}, {name}"
                    )
                    continue

                coordinates = coords_3d + coords_2d

                if not all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    for value in coordinates
                ):
                    errors.append(
                        f"Invalid numeric value: {filename}, {name}"
                    )

                if not isinstance(in_frame, bool):
                    errors.append(
                        f"Invalid in_frame flag: {filename}, {name}"
                    )

                elif in_frame:
                    x, y = coords_2d

                    if not (0 <= x <= 1 and 0 <= y <= 1):
                        errors.append(
                            f"Out-of-bounds joint: {filename}, {name}"
                        )

            checked_frames += 1

        except Exception as error:
            errors.append(f"JSON error in {filename}: {error}")

    # Check manifest
    manifest_records = 0

    if not manifest_path.exists():
        errors.append(f"Manifest missing: {manifest_path.name}")

    else:
        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    manifest_records += 1

                    for column in [
                        "image", "annotation", "visualization"
                    ]:
                        if not row.get(column):
                            errors.append(
                                f"Empty manifest field: {column}"
                            )
                            continue

                        referenced_path = BASE_DIR / row[column]

                        if not referenced_path.exists():
                            errors.append(
                                f"Manifest path missing: {row[column]}"
                            )

            if manifest_records != len(image_files):
                errors.append(
                    f"Expected {len(image_files)} manifest records, "
                    f"found {manifest_records}"
                )

        except Exception as error:
            errors.append(f"Manifest error: {error}")

    print("Frames checked:", checked_frames)
    print("Manifest records:", manifest_records)
    print("Expected joints per frame:", len(EXPECTED_JOINTS))
    print("Total errors:", len(errors))

    if errors:
        print("\nAUDIT ERRORS:")
        for error in errors:
            print("-", error)

        print("\nAUDIT FAILED")

    else:
        print("\nSUCCESS: Dataset integrity checks passed!")

    return len(errors) == 0


# Select available datasets
selected_configs = []
seen_datasets = set()

for config in DATASET_CONFIGS:

    dataset = config["dataset"]

    if (
        (dataset / "images").is_dir()
        and (dataset / "annotations").is_dir()
        and config["visualizations"].is_dir()
        and config["manifest"].is_file()
        and dataset.resolve() not in seen_datasets
    ):
        selected_configs.append(config)
        seen_datasets.add(dataset.resolve())


if not selected_configs:
    raise FileNotFoundError(
        "No valid dataset and manifest combination found."
    )


# Run audits
results = []

for config in selected_configs:
    results.append(audit_dataset(config))


print("\n===== FINAL AUDIT SUMMARY =====")
print("Datasets checked:", len(results))
print("Successful audits:", sum(results))
print("Failed audits:", len(results) - sum(results))

if all(results):
    print("\nSUCCESS: All available dataset audits passed!")

else:
    print("\nWARNING: One or more dataset audits failed.")
