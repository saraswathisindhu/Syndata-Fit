
import cv2
import json
from pathlib import Path

# Automatically locate the dataset
DATASET_CANDIDATES = [
    Path("Syndata_Output"),
    Path("../New folder/Syndata_Output"),
    Path("sample_dataset")
]

DATASET = next(
    (
        folder for folder in DATASET_CANDIDATES
        if (folder / "images").is_dir()
        and (folder / "annotations").is_dir()
    ),
    None
)

if DATASET is None:
    raise FileNotFoundError(
        "Dataset not found. Check the dataset folder structure."
    )

IMAGE_FOLDER = DATASET / "images"
ANNOTATION_FOLDER = DATASET / "annotations"

# Output folder
OUTPUT_FOLDER = Path("visualized_frames")
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Skeleton connections
connections = [
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

# Find available image frames
image_files = sorted(IMAGE_FOLDER.glob("frame_*.png"))

success_count = 0
errors = []

for image_path in image_files:

    try:
        frame_number = int(
            image_path.stem.replace("frame_", "")
        )

        json_path = ANNOTATION_FOLDER / f"frame_{frame_number:04d}.json"

        # Load image
        image = cv2.imread(str(image_path))

        if image is None:
            raise FileNotFoundError(
                f"Could not read image: {image_path}"
            )

        # Load annotation
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        joints = data["joints"]

        height, width = image.shape[:2]
        points = {}

        # Convert normalized coordinates to pixels
        for name, joint in joints.items():

            if not joint["in_frame"]:
                continue

            x, y = joint["2d"]

            points[name] = (
                int(x * (width - 1)),
                int(y * (height - 1))
            )

        # Draw skeleton connections
        for a, b in connections:

            if a in points and b in points:
                cv2.line(
                    image,
                    points[a],
                    points[b],
                    (0, 255, 0),
                    3,
                    cv2.LINE_AA
                )

        # Draw joint points
        for name, position in points.items():

            cv2.circle(
                image,
                position,
                6,
                (0, 0, 255),
                -1,
                cv2.LINE_AA
            )

        # Save visualization
        output_path = OUTPUT_FOLDER / (
            f"frame_{frame_number:04d}_skeleton.png"
        )

        if not cv2.imwrite(str(output_path), image):
            raise RuntimeError("Could not save output image")

        success_count += 1

        if success_count % 10 == 0:
            print(f"Processed {success_count}/{len(image_files)} frames")

    except Exception as error:
        errors.append((image_path.name, str(error)))

# Final report
print("\n===== SYNDATA-FIT BATCH VISUALIZATION =====")
print("Dataset:", DATASET.resolve())
print("Frames found:", len(image_files))
print("Successfully processed:", success_count)
print("Errors:", len(errors))

if errors:
    for frame, message in errors:
        print(f"{frame}: {message}")
else:
    print("SUCCESS: All available visualizations completed!")

print("Output folder:", OUTPUT_FOLDER.resolve())
