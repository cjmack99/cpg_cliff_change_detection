# cpg_cliff_change_detection
Data processing pipeline for LiDAR point clouds
Code for Mack et al 2024 "An Automated Workflow for Detecting Coastal Cliff Change in Large LiDAR Datasets"
Published in _____

This project is built for San Diego county on data collected by the Coastal Process Group (CPG) Field Crew from 2017-2024.

We present an automated pipeline for processing LiDAR point clouds and extracting metrics of coastal cliff change.

Three main processing steps are included in this workflow:
1. Isolate cliff surface using machine learning classification
2. Change detection using M3C2 (Lague et al 2013)
3. Extract change metrics using shore-normal, 2.75D grids

