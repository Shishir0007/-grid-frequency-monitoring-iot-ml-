# Project Summary

**Title**: Monitoring and Analysis of Grid Frequency
**Institution**: Kathmandu University, School of Engineering, Dept. of Electrical & Electronics Engineering
**Type**: Fourth Year (Final Year) Project — Bachelor of Engineering
**Date**: December 2025
**Award**: Best Undergraduate Project, KUCAP 2025

## Objectives
1. Model a section of the Nepal power system for frequency analysis.
2. Monitor and analyze the grid frequency in real time for the considered system.

## Method Summary
- **Site visit**: Conducted at Sunkoshi Hydropower, Sindhupalchok District, to validate
  assumptions against real equipment: a 300 rpm synchronous generator, dry-type DC
  excitation, a manually operated oil governor system, a 6.3 kV/66 kV step-up
  transformer, and an observed frequency variation of 49.5–50 Hz.
- **Hardware**: ESP32 microcontroller + ZMPT101B voltage sensor, using zero-crossing
  detection to measure grid frequency from AC mains voltage. Data streamed via Wi-Fi to
  a Node-RED dashboard for real-time visualization.
- **Simulation**: A section of Nepal's central-region grid (Bhotekoshi, Sunkoshi, and
  Indrawati hydropower plants feeding Lamosangu, Panchkhal, Banepa, and Bhaktapur
  substations) modeled in DIgSILENT PowerFactory. Load flow analysis and dynamic
  simulation performed across four disturbance cases: load increment, load decrement,
  load outage, and generator outage.
- **Validation**: A real, measured load increment (5.47%) from Banepa Substation's
  24-hour load data was used as simulation input and cross-checked against 24-hour
  hardware frequency recordings taken on-site.
- **Prediction**: Historical frequency data modeled as a time series using linear
  regression, polynomial regression (degree 2 and 3), and Random Forest regression, with
  an interactive interface for predicting frequency at any given time.

## Headline Results
- Across all four dynamic simulation cases, frequency deviations stayed within IEEE-typical
  stability margins, with the lowest ROCOF (0.076 Hz/s) seen in the generator outage case
  and the highest (0.396 Hz/s) in the load decrement case at the Lamosangu bus.
- Hardware-measured frequency over two independent 24-hour periods stayed within
  49.7–50.2 Hz, closely matching the simulated response for the equivalent real-world
  load disturbance.
- The frequency prediction model was trained on 4,271 data points (mean 50.006 Hz,
  standard deviation 0.29 Hz).

## Limitations
- Machine parameters in the simulation used default values rather than site-measured
  parameters for the specific generators modeled.
- Real-time data may not perfectly match all real-world conditions due to noise and
  simplified modeling assumptions.

## Full Report
The complete project report (with literature review, full methodology, all figures, and
references) is available on request — not included in this repository to keep it
focused on reproducible code and key results.
