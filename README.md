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


Current workflow:
- cpg lidar tools pipeline (matt's code)
   spits out erosion2_dbscan.las

- gridsV5 on iwa for grid making
    spits out date_clusters_10x10cm.csv
- clean_grids
    spits out date_clusters_cleaned.csv
- get_data
    spits out date_clusters_cropped_cleaned.npy
    these npy files can be used for all the plots






The workflow goes as follows:

cpg_lidar.level_one(survey_path)
cpg_lidar.level_two(etc)
cpr_lidar.level_three() # thats what this repo currently is/what the paper 1 will be


cpg_lidar.level_one() # john knows what these do, translate them to python
cpg_lidar.level_two() # integrate cliff/beach seperation earlier

cpg_lidar.level_three() 
vegetation removal part 2: canupo or 3masc?
cpg_lidar.m3c2()
cpg_lidar.dbscan()
cpg_lidar.gridding()
cpg_lidar.clean_grids()


Add plotting functions
cpg_lidar.display()
 etc





  
  
