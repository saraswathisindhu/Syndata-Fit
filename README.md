# Syndata-Fit
### An End-to-End Synthetic Data Generation Pipeline for Human Motion Tracking

**Project Category:** Computer Vision | Synthetic Data Generation | 3D Animation | Human Motion Tracking

**Current Status:** Two-action synthetic dataset successfully generated, visualized, indexed and audited.

---

## 1. Project Overview

Syndata-Fit is an extensible synthetic human motion data generation pipeline developed using Blender and Python.

The project combines AI-generated 3D human characters, skeletal rigging, animation, 3D rendering and automated annotation processing to create synthetic datasets for human pose estimation and motion tracking applications.

The current dataset contains two human motion categories:

- Jogging
- Walking

Each action contains 100 rendered frames with corresponding 2D and 3D joint annotations and skeleton visualizations.

The project aims to establish an automated and extensible workflow for generating labelled human motion data.

## 2. Project Objectives

- Generate synthetic human characters and animated scenes.
- Create human motion sequences using skeletal animation.
- Render synthetic human motion images using Blender.
- Extract 3D body-joint coordinates from an animated character.
- Project 3D joint positions into 2D camera coordinates.
- Generate structured JSON annotations for every frame.
- Visualize human skeletal structures using OpenCV.
- Organize image and annotation files using a CSV manifest.
- Validate dataset integrity through automated Python scripts.
- Establish a foundation for future human pose-estimation and motion-tracking experiments.

## 3. Technologies and Tools

| Technology | Application |
|---|---|
| Meshy AI | AI-generated 3D human character |
| Mixamo | Character rigging and animation |
| Blender | 3D scene setup, animation and rendering |
| Blender Python API | Animation inspection and joint-coordinate extraction |
| Python | Dataset processing and automation |
| OpenCV | 2D skeleton visualization |
| JSON | Structured joint annotations |
| CSV | Dataset indexing and organization |
| Visual Studio Code | Python development |

**Python version used:** 3.13.1

**Python packages:** OpenCV and NumPy installed.

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

Two animation sequences were prepared using Mixamo:

**Jogging**
- Original animation range: 26 frames.
- Blender F-Curve Cycles modifiers used to repeat the animation.
- Root motion configured to preserve continuous forward movement.
- Extended to a 100-frame sequence.

**Walking**
- Animation action: `Walking_30F`.
- Original animation range: 30 frames.
- Animation repeated to produce a 100-frame sequence.
- Root motion configured to maintain continuous forward movement.

### Rendering

The Blender scene includes a configured character, camera, lighting, materials and background.

The animation sequences were rendered using Blender's built-in animation rendering workflow (`Ctrl + F12`).

Each action produces 100 rendered frames at 30 FPS, representing approximately 3.33 seconds of animation.

## 5. Dataset Specifications

| Property | Current dataset |
|---|---|
| Dataset name | Syndata-Fit |
| Character count | 1 |
| Action categories | 2 |
| Actions | Jogging, Walking |
| Frames per action | 100 |
| Total rendered frames | 200 |
| Frame rate | 30 FPS |
| Approximate duration per action | 3.33 seconds |
| Tracked body joints | 17 |
| Image format | PNG |
| Annotation format | JSON |
| Visualization format | PNG |
| Dataset index | CSV |

### Dataset Contents

Each frame contains:

1. Original rendered image.
2. JSON annotation containing 2D and 3D joint coordinates.
3. Skeleton visualization generated using OpenCV.

The complete local dataset contains:

- 200 rendered images.
- 200 JSON annotations.
- 200 skeleton visualizations.

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
            "3d": [0.004693, -0.164665, 0.855778],
            "2d": [0.501188, 0.213055],
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

The Python stage processes the generated datasets and creates visual representations of the annotations.

### A. Skeleton Visualization

**Script:** `visualizer.py`

Functions:

- Automatically detects valid action folders.
- Loads rendered PNG images.
- Reads corresponding JSON annotations.
- Extracts normalized 2D joint coordinates.
- Converts normalized coordinates into image pixel positions.
- Draws skeleton connections using OpenCV.
- Marks joint positions on rendered images.
- Saves skeleton visualization images.

The script supports multiple action folders without requiring action names to be manually added to the code.

### B. Dataset Manifest Generation

**Script:** `manifest.py`

The manifest generator:

- Automatically detects action folders.
- Checks the availability of rendered images.
- Checks corresponding JSON annotation files.
- Checks skeleton visualization images.
- Reads annotation metadata.
- Records frame numbers, action labels and joint counts.
- Creates a combined CSV index linking each frame to its corresponding files.

**Output:** `manifest.csv`

### C. Dataset Audit

**Script:** `audit.py`

The full dataset audit checks:

- Availability of rendered images.
- Availability of JSON annotations.
- Expected 17 joint names in every annotation.
- Numeric and finite coordinate values.
- Frame-number consistency.
- Action-label consistency.
- Manifest record counts and referenced file availability.
- Availability of skeleton visualizations.
- Missing and duplicate manifest records.

The script also performs a separate audit of the five-frame GitHub sample dataset.

The full local dataset audit and GitHub sample audit both completed successfully with zero errors.

## 8. Repository Structure

The GitHub repository contains the Python processing scripts, documentation and a selected five-frame sample dataset.

```text
Syndata-Fit/
│
├── sample_dataset/
│   ├── images/
│   ├── annotations/
│   └── visualizations/
│
├── visualizer.py
├── manifest.py
├── audit.py
├── manifest.csv
├── sample_manifest.csv
├── requirements.txt
├── .gitignore
└── README.md
```

### Complete Dataset Storage

The complete generated dataset is maintained separately from the GitHub repository.

```text
Syndata_Output/
│
├── jogging/
│   ├── images/
│   ├── annotations/
│   └── visualizations/
│
└── walking/
    ├── images/
    ├── annotations/
    └── visualizations/
```

Each action folder contains 100 images, 100 JSON annotations and 100 skeleton visualizations.

GitHub contains five representative sample frames with their corresponding images, annotations and visualizations.

This keeps the repository smaller while allowing visitors to inspect the dataset format.

## 9. Installation and Execution

### Prerequisites

- Python 3.9 or newer.
- Visual Studio Code or another Python development environment.
- OpenCV and other dependencies listed in `requirements.txt`.
- A generated dataset for full multi-action processing.
- Blender for reproducing the 3D generation and rendering stage.

### Step 1: Clone the Repository

```bash
git clone https://github.com/saraswathisindhu/Syndata-Fit.git
cd Syndata-Fit
```

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

### Step 4: Configure the Dataset Folder

For full dataset processing, place the `Syndata_Output` folder inside the project directory