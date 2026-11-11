# Syndata-Fit
### An End-to-End Synthetic Data Generation Pipeline for Human Motion Tracking

**Project Category:** Computer Vision | Synthetic Data Generation | 3D Animation | Human Motion Tracking

**Project Status:** Initial 100-frame prototype completed and validated.

---

## 1. Project Overview

Syndata-Fit is an end-to-end synthetic human motion data generation pipeline developed using Blender and Python.

The project combines AI-generated 3D human characters, skeletal rigging, animation, 3D rendering and automated annotation generation to create synthetic datasets for human pose estimation and motion tracking applications.

The initial prototype focuses on a forward-jogging human character. It generates rendered images, corresponding 2D and 3D body-joint coordinates, JSON annotations and skeleton visualizations.

The primary objective is to establish an automated and extensible workflow for generating labelled human motion data.

## 2. Project Objectives

- Generate synthetic human characters and animated scenes.
- Create human motion sequences using skeletal animation.
- Render synthetic human motion images using Blender.
- Extract 3D body-joint coordinates from an animated character.
- Project 3D joint positions into 2D camera coordinates.
- Generate structured JSON annotations for every frame.
- Visualize human skeletal structures using OpenCV.
- Organize image and annotation files using a CSV manifest.
- Establish a foundation for future human pose-estimation and motion-tracking experiments.

## 3. Technologies and Tools

| Technology | Application |
|---|---|
| Meshy AI | AI-generated 3D human character |
| Mixamo | Automatic character rigging and animation |
| Blender | 3D scene setup, animation and rendering |
| Blender Python API | Animation inspection and joint-coordinate extraction |
| Python | Dataset processing and automation |
| OpenCV | 2D skeleton visualization |
| JSON | Structured joint annotations |
| CSV | Dataset indexing and organization |
| Visual Studio Code | Python development environment |

**Python version:** 3.13.1

**Python packages:** OpenCV and NumPy installed. The current visualization and manifest scripts primarily use OpenCV and Python's built-in modules; NumPy is not directly used in these scripts.

## 4. 3D Character and Animation Pipeline

### Character Creation

An AI-generated human character was created using Meshy AI and imported into Blender.

### Rigging

The character was rigged using Mixamo with a standard skeletal structure.

The imported character was inspected to confirm:

- Armature object: `Armature`
- Mesh object: `geometry_0.001`
- Correct mesh parenting
- Correct Armature modifier connection
- 41 skeletal bones

### Animation

A forward-jogging animation was downloaded from Mixamo.

The original animation action has a frame range of 1–26. Blender F-Curve Cycles modifiers were configured to repeat the animation over the required sequence.

Root motion was preserved so that the character moves forward rather than jogging in place.

### Rendering

The Blender scene includes a configured character, camera, lighting, materials and background.

The animation was rendered using Blender's built-in animation rendering workflow (`Ctrl + F12`).

The initial dataset contains 100 rendered frames at 30 FPS, representing approximately 3.33 seconds of animation.

## 5. Dataset Specifications

| Property | Current prototype |
|---|---|
| Dataset name | Syndata-Fit |
| Character count | 1 |
| Action category | Forward jogging |
| Rendered frames | 100 |
| Frame rate | 30 FPS |
| Approximate sequence duration | 3.33 seconds |
| Original Mixamo action range | 1–26 frames |
| Tracked body joints | 17 |
| Image format | PNG |
| Annotation format | JSON |
| Visualization format | PNG |
| Dataset index | CSV |

### Dataset Contents

Each frame has:

1. An original rendered image.
2. A JSON annotation containing 2D and 3D joint coordinates.
3. A skeleton visualization generated using OpenCV.

The complete dataset contains 100 image-annotation pairs and 100 corresponding skeleton visualizations.

## 6. Human Body Joint Annotation

The dataset tracks 17 body joints.

| No. | Joint |
|---:|---|
| 1 | Head |
| 2 | Neck |
| 3 | Left shoulder |
| 4 | Right shoulder |
| 5 | Left elbow |
| 6 | Right elbow |
| 7 | Left wrist |
| 8 | Right wrist |
| 9 | Left hip |
| 10 | Right hip |
| 11 | Left knee |
| 12 | Right knee |
| 13 | Left ankle |
| 14 | Right ankle |
| 15 | Left toe |
| 16 | Right toe |
| 17 | Hips |

### Annotation Format

Each rendered frame has a corresponding JSON annotation.

Example:

```json
{
    "frame": 1,
    "action": "jogging",
    "joints": {
        "head": {
            "3d": [
                0.004693,
                -0.164665,
                0.855778
            ],
            "2d": [
                0.501188,
                0.213055
            ],
            "in_frame": true
        }
    }
}
```

### Annotation Fields

- `frame`: Frame number.
- `action`: Human action label.
- `joints`: Dictionary containing the tracked body joints.
- `3d`: World-space joint coordinates.
- `2d`: Normalized camera-projected image coordinates.
- `in_frame`: Indicates whether the projected joint is within camera image bounds and has positive camera depth.

The 2D coordinates are normalized relative to image width and height, using a top-left image origin.

**Important:** The current `in_frame` field does not perform occlusion detection or determine actual anatomical visibility.

## 7. Python Processing Pipeline

The Python stage processes the generated dataset and creates visual representations of the annotations.

### A. Skeleton Visualization

**Script:** `visualizer.py`

Functions:

- Loads rendered PNG images.
- Reads corresponding JSON annotations.
- Extracts normalized 2D joint coordinates.
- Converts normalized coordinates into image pixel positions.
- Draws skeleton connections using OpenCV.
- Marks joint positions on the rendered images.
- Saves the resulting visualization images.

The script automatically processes all 100 frames.

### B. Dataset Manifest Generation

**Script:** `manifest.py`

The manifest generator:

- Checks the availability of rendered images.
- Checks corresponding JSON annotation files.
- Checks skeleton visualization images.
- Reads annotation metadata.
- Records frame numbers, action labels and joint counts.
- Creates a CSV index linking each frame to its corresponding files.

**Output:** `manifest.csv`

### C. Dataset Audit

**Script:** `audit.py`

The final audit checks:

- Availability of all 100 rendered images.
- Availability of all 100 JSON annotations.
- Expected 17 joint names in every annotation.
- Numeric and finite coordinate values.
- Frame-number consistency.
- Manifest record count and referenced file availability.
- Availability of all 100 skeleton visualizations.

The final audit completed successfully with zero errors.

### D. Annotation Standardization

**Script:** `fix_annotations.py`

This helper script standardizes the central joint name in the first two annotations, changing `pelvis` to `hips` to maintain consistency across the dataset.

## 8. Repository Structure

The GitHub repository contains the Python processing scripts, documentation and a selected five-frame sample dataset.

```text
Syndata-Fit-Python/
│
├── sample_dataset/
│   ├── images/
│   │   ├── frame_0001.png
│   │   ├── frame_0025.png
│   │   ├── frame_0050.png
│   │   ├── frame_0075.png
│   │   └── frame_0100.png
│   │
│   ├── annotations/
│   │   ├── frame_0001.json
│   │   ├── frame_0025.json
│   │   ├── frame_0050.json
│   │   ├── frame_0075.json
│   │   └── frame_0100.json
│   │
│   └── visualizations/
│       ├── frame_0001_skeleton.png
│       ├── frame_0025_skeleton.png
│       ├── frame_0050_skeleton.png
│       ├── frame_0075_skeleton.png
│       └── frame_0100_skeleton.png
│
├── visualizer.py
├── manifest.py
├── audit.py
├── fix_annotations.py
├── manifest.csv
├── requirements.txt
├── .gitignore
└── README.md
```

### Complete Dataset Storage

The complete generated dataset is maintained separately from the GitHub repository.

```text
Syndata_Output/
│
├── images/
│   ├── frame_0001.png
│   ├── frame_0002.png
│   ├── ...
│   └── frame_0100.png
│
└── annotations/
    ├── frame_0001.json
    ├── frame_0002.json
    ├── ...
    └── frame_0100.json
```

The complete 100-frame dataset and full set of skeleton visualizations are retained locally. GitHub contains five representative frames: 1, 25, 50, 75 and 100.

This keeps the repository smaller while still allowing visitors to inspect the generated images, annotations and visualizations.

## 9. Installation and Execution

### Prerequisites

- Python 3.13.1 or a compatible Python 3 version.
- Visual Studio Code or another Python development environment.
- Blender for reproducing the 3D generation and rendering stage.
- A generated dataset with corresponding images and JSON annotations for the Python processing stage.

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Syndata-Fit-Python
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the repository's actual URL.

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure Dataset Paths

Before running the processing scripts on another computer, configure the image, annotation and visualization directory paths in the relevant Python scripts to point to the available dataset folders.

The five-frame GitHub sample is provided for inspection. The original processing workflow was validated against the complete local 100-frame dataset.

### Step 5: Run the Visualization Script

```bash
python visualizer.py
```

### Step 6: Generate the Dataset Manifest

```bash
python manifest.py
```

### Step 7: Run the Dataset Audit

```bash
python audit.py
```

The audit verifies the dataset files, annotation structure, coordinates, manifest and visualization outputs.

## 10. Dataset Validation and Results

The initial prototype underwent several validation stages.

| Validation | Result |
|---|---|
| Rendered image generation | 100 frames |
| JSON annotation generation | 100 files |
| Image-annotation pairing | Successful |
| Coordinate validation | Zero reported errors |
| Joint visualization | 100 frames |
| Visual inspection | Frames 1, 50 and 100 checked |
| Manifest generation | 100 records |
| Missing files during manifest generation | 0 |
| Batch visualization errors | 0 |
| Final dataset audit | Zero errors |

### Final Audit Output

```text
===== SYNDATA-FIT FINAL DATASET AUDIT =====
Frames checked: 100
Manifest records: 100
Expected joints per frame: 17
Total errors: 0

SUCCESS: All dataset integrity checks passed!
```

The skeleton visualizations were inspected at different points in the animation to verify that the projected joint positions and skeleton connections align with the rendered character.

These checks establish basic file and coordinate consistency. They do not yet constitute a complete quantitative evaluation of annotation accuracy or motion-tracking performance.

## 11. Current Limitations

The current implementation is an initial prototype.

- Only one AI-generated human character is included.
- Only one action category, forward jogging, is available.
- The dataset contains 100 frames from a single animation sequence.
- Only 17 body joints are tracked.
- Facial landmarks and detailed hand landmarks are not included.
- Occlusion and anatomical visibility labels are not implemented.
- Multiple camera angles and environmental variations are not yet included.
- No trained human pose-estimation model has been evaluated yet.
- Unreal Engine integration is a future development objective, not part of the completed prototype.

## 12. Future Improvements

### Dataset Expansion

- Add walking, running, jumping and other human actions.
- Generate multiple character variations.
- Introduce different body proportions and clothing.
- Generate additional animation sequences.

### Synthetic Data Improvements

- Add multiple camera angles.
- Vary lighting and environmental conditions.
- Improve occlusion and joint visibility annotations.
- Explore additional annotation formats.

### Computer Vision Integration

- Prepare datasets for human pose-estimation models.
- Explore 2D and 3D human pose estimation.
- Evaluate model performance on synthetic data.
- Investigate synthetic-to-real domain adaptation.

### Real-Time Simulation

- Explore Unreal Engine integration.
- Investigate real-time human motion visualization.
- Explore simulation-based synthetic data generation.

## 13. Conclusion

Syndata-Fit establishes an initial automated workflow for generating synthetic human motion data using Blender and Python.

The completed prototype demonstrates the integration of AI-generated 3D characters, skeletal animation, rendering, 3D joint-coordinate extraction, 2D camera projection, structured annotations, automated skeleton visualization and dataset validation.

The project provides a foundation for expanding synthetic human motion datasets and exploring applications in computer vision, human pose estimation, motion tracking and real-time simulation.

---

**Project:** Syndata-Fit

**Current milestone:** 100-frame forward-jogging synthetic dataset successfully generated, visualized, indexed and audited with zero errors.

**GitHub sample:** Five representative frames with images, JSON annotations and skeleton visualizations.