# PID Controller Tutorial

[![Python: ≥ 3.15](https://img.shields.io/badge/Python-%E2%89%A5%203.15-3776AB?style=flat&logo=python&logoColor=white)](pyproject.toml)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)](pyproject.toml)
[![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=flat&logo=scipy&logoColor=white)](pyproject.toml)
[![Matplotlib](https://img.shields.io/badge/Plots-Matplotlib-11557C?style=flat)](pyproject.toml)

A hands-on Python tutorial for building a PID controller from scratch. Simulate a
DC motor, control its speed, and see how proportional, integral, and derivative
action change its response.

**Tutorial material is available for all nine lessons:** explanations, diagrams,
implementation exercises, and collapsed reference solutions. Readers write the new
code in each lesson; later notebooks include executable setup code for previously
taught concepts. Reference solutions are included for comparison, not executed by
Run All.

[Getting started](#getting-started) · [Tutorial](#tutorial) ·
[Experiments](#experiments) · [Project structure](#project-structure)

## Getting started

Requirements: **Python 3.15+** and **uv**. From the repository directory, install
the project and its dependencies:

```sh
uv sync
```

Open the first tutorial notebook in Jupyter Notebook:

```sh
uv run pid-controller
```

This starts a local Jupyter Notebook server and opens Section 1 in your browser.
Follow the previous/next links to navigate. Run each notebook’s setup cell, then
write your code in the empty exercise cells and press **Shift+Enter**. Expand the
hints or reference solutions when needed; solutions build in order within each notebook.
Keep the terminal open while working; press **Ctrl+C** there to stop the server.

To start without opening a browser automatically, use `uv run pid-controller --no-browser`.

### Background knowledge

You should be comfortable with Python functions and classes, basic algebra, and
the idea of derivatives and integrals. No prior control theory experience or
physical motor is required. The tutorial will introduce the motor model and
control equations alongside their implementations.

## Tutorial

We'll use the same DC motor throughout, adding one piece at a time. Each section
will pair an explanation with code and plots so you can connect the controller's
behavior to its implementation.

| Section | What we'll implement |
| --- | --- |
| **[1. DC Motor Dynamics](src/notebooks/01_dc_motor_dynamics.ipynb)** | Simulate voltage, current, torque, and angular velocity. Account for resistance, inductance, back EMF, inertia, and friction. |
| **[2. Open-Loop Control](src/notebooks/02_open_loop_control.ipynb)** | Apply a constant voltage and observe startup and steady-state speed. See how the speed changes under load. |
| **[3. Proportional Control](src/notebooks/03_proportional_control.ipynb)** | Adjust voltage in proportion to speed error. Examine response speed, oscillation, and steady-state error. |
| **[4. Integral Control](src/notebooks/04_integral_control.ipynb)** | Accumulate error to form a PI controller. Correct persistent error and observe the effect on overshoot and settling. |
| **[5. Derivative Control](src/notebooks/05_derivative_control.ipynb)** | Add a response to the rate of change of error. Explore damping, sensitivity to noise, and setpoint kick. |
| **[6. Full PID Controller](src/notebooks/06_full_pid_controller.ipynb)** | Combine the terms in a reusable PID class with an explicit time step, resettable state, and separate P, I, and D outputs. |
| **[7. Controller Tuning](src/notebooks/07_controller_tuning.ipynb)** | Compare values of `K_p`, `K_i`, and `K_d`. Measure rise time, overshoot, settling time, and steady-state error. |
| **[8. Disturbance Rejection](src/notebooks/08_disturbance_rejection.ipynb)** | Apply external torque after reaching the target speed. Compare the speed drop and recovery with P, PI, and PID control. |
| **[9. Practical PID](src/notebooks/09_practical_pid.ipynb)** | Add voltage saturation, anti-windup, and derivative filtering. Explore derivative-on-measurement to reduce setpoint kick. |

### The control loop

The target is a motor speed in radians per second. The controller compares that
target with the simulated speed and chooses the voltage to apply next.

```text
Target speed ──► Error ──► PID controller ──► Voltage ──► DC motor ──► Actual speed
                  ▲                                                      │
                  └──────────── subtract actual speed ───────────────────┘
```

| Term | Responds to | What we'll investigate |
| --- | --- | --- |
| **P — Proportional** | The current error | How strongly the controller reacts to a speed mismatch. |
| **I — Integral** | Accumulated error | How the controller corrects an error that persists over time. |
| **D — Derivative** | The rate of change of error | How the controller can damp the response, and why noise becomes a problem. |

The motor simulation and controller will be separate components. That lets us
compare control strategies against the same physical model and repeat experiments
under identical conditions.

## Experiments

The lesson experiments show target and actual speed, applied voltage, and
the individual controller contributions over time.

| Experiment | What to look for |
| --- | --- |
| Start the motor at a fixed voltage | Current and torque during startup, then the final speed. |
| Step the target speed | Rise time, overshoot, and settling time. |
| Increase one gain at a time | How each term changes the response and voltage demand. |
| Add a sudden load torque | The speed drop and how quickly the controller recovers. |
| Request a speed beyond the voltage limit | Saturation, integral windup, and recovery when the target becomes reachable again. |
| Add noise to the speed measurement | Derivative sensitivity and the tradeoff introduced by filtering. |

## Project structure

```text
pid-controller/
├── src/
│   ├── notebooks/
│   │   ├── 01_dc_motor_dynamics.ipynb
│   │   ├── 02_open_loop_control.ipynb … 09_practical_pid.ipynb
│   │   └── assets/       # Lesson diagrams
│   └── pid_controller/
│       └── __init__.py   # Jupyter Notebook launcher
├── pyproject.toml        # Package configuration and dependencies
├── uv.lock               # Dependency lockfile
└── README.md
```

NumPy will handle simulation data, SciPy will support numerical integration and
analysis, and Matplotlib will plot the results. Jupyter Notebook provides the notebook interface, and ipykernel runs notebook code
in the project's Python environment.
