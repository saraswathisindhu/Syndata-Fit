
import csv
import json
import math
from pathlib import Path

# ==========================================
# SYNDATA-FIT PORTABLE DATASET AUDIT
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_CANDIDATES = [
    BASE_DIR / "Syndata_Output",
    BASE_DIR.parent / "Syndata_Output",
    BASE_DIR.parent / "New folder" / "Syndata_Output"
]

DATASET_ROOT = next(
    (
        folder for folder in DATASET_CANDIDATES
        if folder.is_dir()
        and any(
            (item / "images").is_dir()
            and (item / "annotations").is_dir()
            and (item / "visualizations").is_dir()
            for item in folder.iterdir()
            if item.is_dir()
        )
    ),
    None
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


def check_annotation(json_path, expected_frame, expected_action):

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    errors = []

    if data.get("frame") != expected_frame:
        errors.append("Incorrect frame number")

    if data.get("action") != expected_action:
        errors.append("Incorrect action label")

    joints = data.get("joints", {})

    if not isinstance(joints, dict):
        return ["Invalid joints structure"]

    if set(joints.keys()) != EXPECTED_JOINTS:
        errors.append("Incorrect joint names")

    for name, joint in joints.items():

        if not isinstance(joint, dict):
            errors.append(f"Invalid joint structure: {name}")
            continue

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
            continue

        if not isinstance(in_frame, bool):
            errors.append(f"Invalid in_frame flag: {name}")

        elif in_frame:
            x, y = coords_2d

            if not (0 <= x <= 1 and 0 <= y <= 1):
                errors.append(f"Out-of-bounds joint: {name}")

    return errors


def audit_full_dataset():

    print("\n===== SYNDATA-FIT FULL DATASET AUDIT =====")

    if DATASET_ROOT is None:
        print("Full dataset not found.")
        print("Skipping full dataset audit.")
        return None

    print("Dataset root:", DATASET_ROOT)

    errors = []
    action_counts = {}
    checked = 0
    seen_records = set()

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

    actions = sorted(
        folder.name
        for folder in DATASET_ROOT.iterdir()
        if folder.is_dir()
        and (folder / "images").is_dir()
        and (folder / "annotations").is_dir()
        and (folder / "visualizations").is_dir()
    )

    for action in actions:
        action_counts[action] = 0

    for row in records:

        action = row["action"]

        if action not in action_counts:
            errors.append(f"Unexpected action in manifest: {action}")
            continue

        try:
            frame = int(row["frame"])
        except (ValueError, TypeError):
            errors.append(f"Invalid frame number: {row['frame']}")
            continue

        record_key = (action, frame)

        if record_key in seen_records:
            errors.append(f"Duplicate record: {action} frame {frame}")
            continue

        seen_records.add(record_key)

        action_folder = DATASET_ROOT / action

        expected_paths = {
            "image": action_folder / "images" / f"frame_{frame:04d}.png",
            "annotation": action_folder / "annotations" / f"frame_{frame:04d}.json",
            "visualization": action_folder / "visualizations" / f"frame_{frame:04d}_skeleton.png"
        }

        for column, expected_path in expected_paths.items():

            if not row.get(column):
                errors.append(
                    f"Empty {column} path: {action} frame {frame}"
                )
                continue

            actual_path = (BASE_DIR / row[column]).resolve()

            if actual_path != expected_path.resolve():
                errors.append(
                    f"Incorrect {column} path: {action} frame {frame}"
                )

            if not actual_path.is_file():
                errors.append(
                    f"Missing {column}: {action} frame {frame}"
                )

        if row.get("joint_count") != "17":
            errors.append(
                f"Incorrect joint count in manifest: {action} frame {frame}"
            )

        annotation_path = expected_paths["annotation"]

        if annotation_path.is_file():

            try:
                annotation_errors = check_annotation(
                    annotation_path, frame, action
                )

                for error in annotation_errors:
                    errors.append(
                        f"{action} frame {frame}: {error}"
                    )

            except Exception as error:
                errors.append(
                    f"JSON error: {action} frame {frame}: {error}"
                )

        checked += 1
        action_counts[action] += 1

    # Check that every source image is represented in the manifest.
    for action in actions:

        image_folder = DATASET_ROOT / action / "images"

        image_frames = {
            int(path.stem.replace("frame_", ""))
            for path in image_folder.glob("frame_*.png")
        }

        manifest_frames = {
            frame
            for record_action, frame in seen_records
            if record_action == action
        }

        missing_frames = image_frames - manifest_frames
        extra_frames = manifest_frames - image_frames

        if missing_frames:
            errors.append(
                f"{action}: {len(missing_frames)} images missing from manifest"
            )

        if extra_frames:
            errors.append(
                f"{action}: {len(extra_frames)} manifest frames have no source image"
            )

    print("\n--- ACTION SUMMARY ---")

    for action in actions:
        print(
            f"{action.capitalize()} records:",
            action_counts[action]
        )

    print("Total records checked:", checked)
    print("Expected joints per frame:", len(EXPECTED_JOINTS))
    print("Total errors:", len(errors))

    if errors:

        print("\nAUDIT ERRORS:")

        for error in errors:
            print("-", error)

        print("\nFULL DATASET AUDIT FAILED")
        return False

    print("\nSUCCESS: Full dataset passed!")
    return True


def audit_github_sample():

    print("\n===== GITHUB SAMPLE AUDIT =====")

    errors = []

    image_folder = SAMPLE_ROOT / "images"
    annotation_folder = SAMPLE_ROOT / "annotations"
    visualization_folder = SAMPLE_ROOT / "visualizations"

    if not image_folder.is_dir():
        print("ERROR: Sample images folder missing")
        return False

    if not annotation_folder.is_dir():
        print("ERROR: Sample annotations folder missing")
        return False

    if not visualization_folder.is_dir():
        print("ERROR: Sample visualizations folder missing")
        return False

    images = sorted(image_folder.glob("frame_*.png"))
    checked = 0

    print("Dataset:", SAMPLE_ROOT)
    print("Frames found:", len(images))

    if not SAMPLE_MANIFEST.is_file():
        print("ERROR: Sample manifest missing")
        return False

    for image_path in images:

        frame_name = image_path.stem

        json_path = annotation_folder / f"{frame_name}.json"

        visualization_path = (
            visualization_folder /
            f"{frame_name}_skeleton.png"
        )

        if not json_path.is_file():
            errors.append(
                f"Missing sample annotation: {frame_name}"
            )
            continue

        if not visualization_path.is_file():
            errors.append(
                f"Missing sample visualization: {frame_name}"
            )

        try:
            frame = int(frame_name.replace("frame_", ""))

            with open(
                json_path, "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            action = data.get("action")

            errors.extend(
                f"{frame_name}: {error}"
                for error in check_annotation(
                    json_path, frame, action
                )
            )

            checked += 1

        except Exception as error:
            errors.append(
                f"Sample JSON error: {frame_name}: {error}"
            )

    with open(
        SAMPLE_MANIFEST, "r", encoding="utf-8"
    ) as file:
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


# ==========================================
# RUN AUDITS
# ==========================================

full_result = audit_full_dataset()
sample_result = audit_github_sample()

results = [
    result for result in [full_result, sample_result]
    if result is not None
]

print("\n===== FINAL AUDIT SUMMARY =====")
print("Datasets checked:", len(results))
print("Successful audits:", sum(results))
print("Failed audits:", len(results) - sum(results))

if results and all(results):
    print("\nSUCCESS: All available dataset audits passed!")
else:
    print("\nWARNING: One or more dataset audits failed.")
