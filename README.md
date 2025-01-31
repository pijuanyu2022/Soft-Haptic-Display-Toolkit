# Soft Haptic Display (SHD) Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

A **fingertip-sized, high-resolution pneumatic haptic display** designed to provide realistic tactile feedback in virtual reality (VR) environments or during robot teleoperation. This repository includes all the **hardware** (CAD files, BOM) and **software** (Arduino, Raspberry Pi, GUI) needed to build and control the SHD.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Citation & References](#citation--references)
- [Acknowledgments](#acknowledgments)

---

## Features

- **4×4 Wearable Tactile Array** – A low-cost silicone actuator array with 16 individually controlled chambers.
- **Desktop-Sized Control Box** – Integrates an Arduino Due, a Raspberry Pi, and pneumatic valves.
- **Real-Time Control** – Low-latency wireless communication between the SHD and a PC or VR platform.
- **Open-Source** – All code, CAD files, and documentation are released under the MIT license.
- **Easy to Build** – Minimal development time; accessible to students and researchers with diverse backgrounds.

---

## Screenshots

The 4 × 4 tactile array haptic display (red) is connected to the control box (white) via transparent air tubes. The control box communicates with the laptop wirelessly using a socket communication method.

<p>
  <img src="Docs/Images/System Overview.png" alt="static animation 1" width="800" />
  
</p>


Static Patterns
<p>
  <img src="Docs/Images/Gif/static_1.gif" alt="static animation 1" width="160" />
  <img src="Docs/Images/Static/1.png" alt="static 1" width="137" />
  <img src="Docs/Images/Static/2.png" alt="static 2" width="122" />
  <img src="Docs/Images/Static/3.png" alt="static 3" width="130" />
  <img src="Docs/Images/Static/4.png" alt="static 4" width="125" />
  <img src="Docs/Images/Static/5.png" alt="static 5" width="131" />
  <img src="Docs/Images/Static/6.png" alt="static 6" width="122" />
  
</p>


Animation Patterns
<p>
  <img src="Docs/Images/Gif/1.gif" alt="Animation gif 1" width="160" />
  <img src="Docs/Images/Animation/5.png" alt="Animation 1" width="150" />
  <img src="Docs/Images/Animation/6.png" alt="Animation 2" width="155" />

  <img src="Docs/Images/Gif/2.gif" alt="Animation gif 2" width="160" />
  <img src="Docs/Images/Animation/7.png" alt="Animation 3" width="163" />
  <img src="Docs/Images/Animation/8.png" alt="Animation 4" width="172" />
  
</p>

<p>
  <img src="Docs/Images/Gif/3.gif" alt="Animation gif 3" width="150" />
  <img src="Docs/Images/Animation/9.png" alt="Animation 5" width="180" />
  <img src="Docs/Images/Animation/10.png" alt="Animation 6" width="205" />
  <img src="Docs/Images/Animation/11.png" alt="Animation 7" width="150" />
  <img src="Docs/Images/Animation/12.png" alt="Animation 8" width="142" />
  
</p>


---

## Project Structure

Here’s an overview of how this repository is organized:

```plaintext
Soft-haptic-display/
├── hardware/
│   ├── CAD/           # 3D/2D design files (STLs, STEP, source CAD)
│   ├── schematics/    # Electronics circuit diagrams
│   ├── BOM/           # Bill of Materials (CSV or Markdown)
├── firmware/
│   ├── arduino/       # Arduino sketches for low-level control
│   └── raspberry_pi/  # Scripts running on the Pi
├── software/
│   └── gui/           # GUI code on the Computer for controlling the SHD
├── docs/
│   ├── manual/        # User manual, assembly guide
│   ├── images/        # Animation pictures, Gif, Static pictures
├── LICENSE
├── README.md
└── CONTRIBUTING.md

```
--- 

## Installation

### Hardware Assembly

Purchase all required items from:
- [list of Controller.md](Hardware/Bill%20of%20Materials/list%20of%20Controller.md)
- [list of Pneumatic.md](Hardware/Bill%20of%20Materials/list%20of%20Pneumatic.md)
- [list of Silicone.md](Hardware/Bill%20of%20Materials/list%20of%20Silicone.md)

Follow the instructions in [docs/manual/hardware_assembly.md](docs/manual/hardware_assembly.md) to:
1. **3D-print** the mold and control box.
2. **Fabricate** the tactile array.
3. **Solder** the control board.
4. **Assemble** the entire control box and connect it to the tactile array.

---
### Install Software on Your Windows PC

1. **Fork** this repository in GitHub.
2. **Open GitHub Desktop** and clone your fork to your local machine.
3. **Open the cloned repository** in Visual Studio Code or any other Python IDE.
4. **Locate** the `main.py` file in the `soft-haptic-display/Software` directory:
   ```plaintext
   python main.py
   ```
5. Install all required Python libraries until the GUI successfully appears on your computer.

---
### Install Software on the Raspberry Pi

1. **Connect** the Raspberry Pi to a monitor.
2. **Open a terminal** on the Raspberry Pi:
```plaintext
git clone https://github.com/pijuanyu2022/Soft-Haptic-Display-Toolkit.git
cd Soft-Haptic-Display-Toolkit/Firmware/Raspberry_Pi/
```
3. **Create a virtual environment** in the terminal window:
```plaintext
python -m venv SoftRobo
source SoftRobo/bin/activate
```

4. **Install**  all required Python libraries so that `run_robot.py` can be opened correctly:
```plaintext
python run_robot.py
```

---
### Install Software on the Arduino Uno

1. **Connect** the Arduino Uno to your PC.
2. **Navigate** to the `/Firmware/Arduino/` directory and open `Pneumatic.ino` in the Arduino IDE.
3. **Select** Arduino Uno under *Tools → Board* in the Arduino IDE.
4. **Upload** the code to the Arduino Uno.

Tips: You can also install the Arduino IDE on the Raspberry Pi and use the Pi to upload the code to the Arduino Uno.

