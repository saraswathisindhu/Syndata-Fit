
import cv2
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATASET_ROOT = (
    BASE_DIR.parent / "New folder" / "Syndata_Output"
)
ACTIONS = ["jogging", "walking"]

CONNECTIONS = [
    ("head", "neck"),
    ("neck", "left_shoulder"),
    ("neck", "right_shoulder"),
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("hips", "left_hip"),
    ("hips", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("left_ankle", "left_toe"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("right_ankle", "right_toe")
]

total_success = 0
total_errors = 0

for action in ACTIONS:

    dataset = DATASET_ROOT / action
    image_folder = dataset / "images"
    annotation_folder = dataset / "annotations"
    output_folder = dataset / "visualizations"

    output_folder.mkdir(parents=True, exist_ok=True)

    image_files = sorted(image_folder.glob("frame_*.png"))

    success_count = 0
    errors = []

    print(f"\n===== {action.upper()} VISUALIZATION =====")
    print("Images found:", len(image_files))

    for image_path in image_files:

        try:
            frame_number = int(
                image_path.stem.replace("frame_", "")
            )

            json_path = annotation_folder / f"frame_{frame_number:04d}.json"

            if not json_path.is_file():
                raise FileNotFoundError(
                    f"Missing annotation: {json_path.name}"
                )

            image = cv2.imread(str(image_path))

            if image is None:
                raise ValueError("Cannot read image")

            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if data.get("action") != action:
                raise ValueError("Action label mismatch")

            if data.get("frame") != frame_number:
                raise ValueError("Frame number mismatch")

            joints = data.get("joints", {})

            if len(joints) != 17:
                raise ValueError("Expected 17 joints")

            height, width = image.shape[:2]
            points = {}

            for name, joint in joints.items():

                if not joint["in_frame"]:
                    continue

                x, y = joint["2d"]

                points[name] = (
                    int(x * (width - 1)),
                    int(y * (height - 1))
                )

            for a, b in CONNECTIONS:

                if a in points and b in points:
                    cv2.line(
                        image, points[a], points[b],
                        (0, 255, 0), 3, cv2.LINE_AA
                    )

            for point in points.values():
                cv2.circle(
                    image, point, 6,
                    (0, 0, 255), -1, cv2.LINE_AA
                )

            output_path = (
                output_folder /
                f"frame_{frame_number:04d}_skeleton.png"
            )

            if not cv2.imwrite(str(output_path), image):
                raise RuntimeError("Could not save visualization")

            success_count += 1

        except Exception as error:
            errors.append((image_path.name, str(error)))

    total_success += success_count
    total_errors += len(errors)

    print("Successfully processed:", success_count)
    print("Errors:", len(errors))
    print("Output:", output_folder)

    for frame, message in errors:
        print(f"ERROR: {frame}: {message}")

print("\n===== MULTI-ACTION VISUALIZATION SUMMARY =====")
print("Total visualizations processed:", total_success)
print("Total errors:", total_errors)

if total_errors == 0:
    print("SUCCESS: All action visualizations completed!")
