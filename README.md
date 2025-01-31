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

Static Patterns
<p>
  <img src="Docs/images/Gif/static_1.gif" alt="static animation 1" width="160" />
  <img src="Docs/images/Static/1.png" alt="static 1" width="157" />
  <img src="Docs/images/Static/2.png" alt="static 2" width="142" />
  <img src="Docs/images/Static/3.png" alt="static 3" width="150" />
  <img src="Docs/images/Static/4.png" alt="static 4" width="145" />
  <img src="Docs/images/Static/5.png" alt="static 5" width="151" />
  <img src="Docs/images/Static/6.png" alt="static 6" width="142" />
  
</p>

<p>
  <img src="Docs/images/Gif/static_2.gif" alt="static animation 2" width="160" />
  <img src="Docs/images/Static/7.png" alt="static 7" width="150" />
  <img src="Docs/images/Static/8.png" alt="static 8" width="148" />
  <img src="Docs/images/Static/9.png" alt="static 9" width="145" />
  <img src="Docs/images/Static/10.png" alt="static 10" width="145" />
  <img src="Docs/images/Static/11.png" alt="static 11" width="148" />
  <img src="Docs/images/Static/12.png" alt="static 12" width="160" />
  
</p>


Animation Patterns
<p>
  <img src="Docs/images/Gif/1.gif" alt="Animation 1" width="160" />
  <img src="Docs/images/Animation/5.png" alt="Animation 5" width="150" />
  <img src="Docs/images/Animation/6.png" alt="Animation 6" width="155" />
  <img src="Docs/images/Gif/2.gif" alt="Animation 2" width="160" />
  <img src="Docs/images/Animation/7.png" alt="Animation 5" width="163" />
  <img src="Docs/images/Animation/8.png" alt="Animation 6" width="172" />
  
</p>

<p>
  <img src="Docs/images/Gif/3.gif" alt="Animation 2" width="150" />
  <img src="Docs/images/Animation/9.png" alt="Animation 5" width="180" />
  <img src="Docs/images/Animation/10.png" alt="Animation 6" width="205" />
  <img src="Docs/images/Animation/11.png" alt="Animation 5" width="150" />
  <img src="Docs/images/Animation/12.png" alt="Animation 6" width="142" />
  
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

Here is about how to install this system