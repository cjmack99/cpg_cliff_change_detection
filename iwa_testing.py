


c1 = "/Volumes/group/LiDAR/VMZ2000_Truck/LiDAR_Processed_Level2/20170323_00590_00636_NoWaves_DelMar/Beach_And_Backshore/m3c2_processing/delmar_grid_run_20240927/20170323_00590_00636_NoWaves_DelMar_beach_cliff_ground_cropped_no_beach.las"
c2 = "/Volumes/group/LiDAR/VMZ2000_Truck/LiDAR_Processed_Level2/20201217_00519_00636_NoWaves_BlacksTorreyDelMar/Beach_And_Backshore/m3c2_processing/delmar_grid_run_20240927/20201217_00519_00636_NoWaves_BlacksTorreyDelMar_beach_cliff_ground_cropped_no_beach.las"




import subprocess
c1 = "/project/group/LiDAR/LidarProcessing/iwa_testing/in_file_v2.las"
outpath = "/project/group/LiDAR/LidarProcessing/iwa_testing/out_file.las"
classifier = "/project/group/LiDAR/LidarProcessing/changedetection_m3c2/m3c2_tools/classifiers/delMar3.prm"
global_shift = ('-475000', '-3641000', '0')


command = [
    "xvfb-run",
    "/usr/local/bin/CloudCompare",
    "-silent", 
    '-auto_save', 'off', 
    '-c_export_fmt', 'las',
    '-o', 
    '-global_shift', *global_shift, c1, 
    '-ss','spatial','0.05', 
    '-canupo_classify', '-use_confidence', '0.8', classifier,
    '-save_clouds', "out_file.las"]
  


subprocess.run(command, check=True)







# cmd = [
#     "xvfb-run",
#     "/usr/local/bin/CloudCompare",
#     "-silent",
#     "-auto_save", "off",
#     "-c_export_fmt", "asc",
#     "-o",
#     "-global_shift", *global_shift, c1,
#     "-ss", "spatial", "0.05",
#     "-save_clouds", "file", outpath
# ]
# subprocess.run(cmd, check=True)








# # command = [
# #     'xvfb-run', 'flatpak', 'run', 'org.cloudcompare.CloudCompare',
# #     '--', 
# #     '-silent', '-auto_save', 'off', '-c_export_fmt', 'asc',
# #     '-o', '-global_shift', *global_shift, c1, '-ss', 'spatial', '0.05',
# #     '-save_clouds', 'file', outpath
# # ]

# command = ['xvfb-run', '/usr/local/bin/CloudCompare',  '-silent', '-auto_save', 'off',
# '-c_export_fmt', 'asc', '-o', '-global_shift', *global_shift, c1, '-ss', 'spatial', '0.05',
# '-save_clouds', 'file', outpath]






# Run the command and check for errors.
subprocess.run(cmd, check=True)



result = subprocess.run(command, capture_output=True, text=True)
print(result.stdout)
