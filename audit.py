
import csv
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATASET_ROOT = (
    BASE_DIR.parent / "New folder" / "Syndata_Output"
)

MANIFEST_PATH = BASE_DIR / "manifest.csv"
SAMPLE_ROOT = BASE_DIR / "sample_dataset"
SAMPLE_MANIFEST = BASE_DIR / "sample_manifest.csv"

EXPECTED_JOINTS = {
    "head", "neck", "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow", "left_wrist", "right_wrist",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_toe", "right_toe", "hips"
}

EXPECTED_ACTIONS = ["jogging", "walking"]


def check_annotation(json_path, expected_frame, expected_action):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    errors = []

    if data.get("frame") != expected_frame:
        errors.append("Incorrect frame number")

    if data.get("action") != expected_action:
        errors.append("Incorrect action label")

    joints = data.get("joints", {})

    if set(joints.keys()) != EXPECTED_JOINTS:
        errors.append("Incorrect joint names")

    for name, joint in joints.items():
        coords_3d = joint.get("3d")
        coords_2d = joint.get("2d")
        in_frame = joint.get("in_frame")

        if not isinstance(coords_3d, list) or len(coords_3d) != 3:
            errors.append(f"Invalid 3D coordinates: {name}")
            continue

        if not isinstance(coords_2d, list) or len(coords_2d) != 2:
            errors.append(f"Invalid 2D coordinates: {name}")
            continue

        coordinates = coords_3d + coords_2d

        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in coordinates
        ):
            errors.append(f"Invalid numeric values: {name}")

        if not isinstance(in_frame, bool):
            errors.append(f"Invalid in_frame flag: {name}")

        elif in_frame:
            x, y = coords_2d
            if not (0 <= x <= 1 and 0 <= y <= 1):
                errors.append(f"Out-of-bounds joint: {name}")

    return errors


def audit_full_dataset():
    print("\n===== SYNDATA-FIT FULL MULTI-ACTION AUDIT =====")
    print("Dataset root:", DATASET_ROOT)

    errors = []
    action_counts = {action: 0 for action in EXPECTED_ACTIONS}
    checked = 0

    if not MANIFEST_PATH.is_file():
        print("ERROR: manifest.csv is missing")
        return False

    with open(MANIFEST_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required = {
            "frame", "action", "joint_count",
            "image", "annotation", "visualization"
        }

        if not required.issubset(set(reader.fieldnames or [])):
            print("ERROR: Manifest columns are incomplete")
            return False

        records = list(reader)

    print("Manifest records:", len(records))

    for row in records:
        action = row["action"]

        if action not in EXPECTED_ACTIONS:
            errors.append(f"Unexpected action: {action}")
            continue

        try:
            frame = int(row["frame"])
        except ValueError:
            errors.append(f"Invalid frame number: {row['frame']}")
            continue

        action_folder = DATASET_ROOT / action

        expected_paths = {
            "image": action_folder / "images" / f"frame_{frame:04d}.png",
            "annotation": action_folder / "annotations" / f"frame_{frame:04d}.json",
            "visualization": action_folder / "visualizations" / f"frame_{frame:04d}_skeleton.png"
        }

        for column, expected_path in expected_paths.items():
            if not row.get(column):
                errors.append(f"Empty {column} path: {action} frame {frame}")
                continue

            actual_path = (BASE_DIR / row[column]).resolve()

            if actual_path != expected_path.resolve():
                errors.append(f"Incorrect {column} path: {action} frame {frame}")

            if not actual_path.is_file():
                errors.append(f"Missing {column}: {action} frame {frame}")

        if row.get("joint_count") != "17":
            errors.append(f"Incorrect joint count in manifest: {action} frame {frame}")

        annotation_path = expected_paths["annotation"]

        if annotation_path.is_file():
            try:
                annotation_errors = check_annotation(
                    annotation_path, frame, action
                )

                for error in annotation_errors:
                    errors.append(f"{action} frame {frame}: {error}")

            except Exception as error:
                errors.append(f"JSON error: {action} frame {frame}: {error}")

        checked += 1
        action_counts[action] += 1

    expected_counts = {"jogging": 100, "walking": 100}

    for action in EXPECTED_ACTIONS:
        if action_counts[action] != expected_counts[action]:
            errors.append(
                f"{action}: expected {expected_counts[action]}, "
                f"found {action_counts[action]}"
            )

    print("\n--- ACTION SUMMARY ---")
    print("Jogging records:", action_counts["jogging"])
    print("Walking records:", action_counts["walking"])
    print("Total records checked:", checked)
    print("Expected joints per frame:", len(EXPECTED_JOINTS))
    print("Total errors:", len(errors))

    if errors:
        print("\nAUDIT ERRORS:")
        for error in errors:
            print("-", error)
        print("\nFULL DATASET AUDIT FAILED")
        return False

    print("\nSUCCESS: Full multi-action dataset passed!")
    return True


def audit_github_sample():
    print("\n===== GITHUB SAMPLE AUDIT =====")

    errors = []
    images = sorted((SAMPLE_ROOT / "images").glob("frame_*.png"))
    checked = 0

    print("Dataset:", SAMPLE_ROOT)
    print("Frames found:", len(images))

    if not SAMPLE_MANIFEST.is_file():
        print("ERROR: Sample manifest missing")
        return False

    for image_path in images:
        frame_name = image_path.stem
        json_path = SAMPLE_ROOT / "annotations" / f"{frame_name}.json"
        visualization_path = (
            SAMPLE_ROOT / "visualizations" /
            f"{frame_name}_skeleton.png"
        )

        if not json_path.is_file():
            errors.append(f"Missing sample annotation: {frame_name}")
            continue

        if not visualization_path.is_file():
            errors.append(f"Missing sample visualization: {frame_name}")

        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            frame = int(frame_name.replace("frame_", ""))
            action = data.get("action")

            errors.extend(
                f"{frame_name}: {error}"
                for error in check_annotation(json_path, frame, action)
            )

            checked += 1

        except Exception as error:
            errors.append(f"Sample JSON error: {frame_name}: {error}")

    with open(SAMPLE_MANIFEST, "r", encoding="utf-8") as file:
        sample_records = list(csv.DictReader(file))

    if len(sample_records) != len(images):
        errors.append("Sample manifest record count mismatch")

    print("Frames checked:", checked)
    print("Manifest records:", len(sample_records))
    print("Expected joints per frame:", len(EXPECTED_JOINTS))
    print("Total errors:", len(errors))

    if errors:
        for error in errors:
            print("-", error)
        print("GITHUB SAMPLE AUDIT FAILED")
        return False

    print("SUCCESS: GitHub sample audit passed!")
    return True


full_result = audit_full_dataset()
sample_result = audit_github_sample()

print("\n===== FINAL AUDIT SUMMARY =====")
print("Datasets checked: 2")
print("Successful audits:", sum([full_result, sample_result]))
print("Failed audits:", 2 - sum([full_result, sample_result]))

if full_result and sample_result:
    print("\nSUCCESS: All dataset audits passed!")
else:
    print("\nWARNING: One or more dataset audits failed.")
