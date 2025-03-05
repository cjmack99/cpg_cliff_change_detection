import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def load_csv_data(filepath):
    """
    Loads a CSV file containing a header row and a header column.
    Returns a tuple: (header_labels, row_labels, data)
      - header_labels: list of column labels (excluding the first column header)
      - row_labels: list of row labels (from the first column of each data row)
      - data: 2D NumPy array of numeric values (empty fields become np.nan)
    """
    with open(filepath, 'r') as f:
        header_line = f.readline().strip()
    # Assume header is comma-separated; skip the first cell.
    header_labels = header_line.split(',')[1:]
    
    row_labels = []
    data_rows = []
    with open(filepath, 'r') as f:
        next(f)  # Skip header row.
        for line in f:
            parts = line.strip().split(',')
            if not parts:
                continue
            row_labels.append(parts[0])
            # Convert the remaining parts: if empty, use np.nan
            row_data = [float(x) if x.strip() != '' else np.nan for x in parts[1:]]
            data_rows.append(row_data)
    
    # Ensure we get a 2D array even if there's only one row.
    data = np.array(data_rows)
    return header_labels, row_labels, data

def save_csv_data(filepath, data, header_labels, row_labels, testing, replace):
    """
    Saves data to a CSV file with the same header row and row labels as the incoming CSV.
    Missing values (np.nan) are written as empty fields.
    If testing is True, prints the file path instead of writing.
    """
    if testing:
        print(f"[TESTING] Would write file: {filepath}")
    else:
        if not replace and os.path.exists(filepath):
            print(f"File {filepath} exists and replace=False; skipping.")
        else:
            with open(filepath, 'w') as f:
                # Write header row: first cell blank, then header labels.
                f.write(',' + ','.join(header_labels) + '\n')
                # Write each row: row label followed by data values.
                for label, row in zip(row_labels, data):
                    formatted = [f'{val:g}' if not np.isnan(val) else '' for val in row]
                    f.write(f"{label}," + ",".join(formatted) + "\n")
            print(f"Wrote file: {filepath}")

def process_files_in_folder(date_folder, file_type, threshold=25):
    """
    Processes a single date folder for the given file type.
    file_type: "erosion" or "accretion"
      - For erosion, selects files WITHOUT "acc" in the name.
      - For accretion, selects files WITH "acc" in the filename.
    Loads the cluster and grid CSVs (with headers and row labels) and filters out clusters
    that have fewer than 'threshold' nonzero cells.
    Returns a dictionary with:
      - header_clusters, row_labels_clusters, original_clusters,
      - header_grid, row_labels_grid, original_grid,
      - filtered_clusters, filtered_grid,
      - and paths for the input files.
    Returns None if required files are not found.
    """
    files = os.listdir(date_folder)
    if file_type == "erosion":
        cluster_candidates = [f for f in files if "clusters_10x10cm.csv" in f and "acc" not in f]
        grid_candidates = [f for f in files if "grid_10x10cm.csv" in f and "acc" not in f]
    else:
        cluster_candidates = [f for f in files if "acc_clusters_10x10cm.csv" in f]
        grid_candidates = [f for f in files if "acc_grid_10x10cm.csv" in f]
        
    if not (cluster_candidates and grid_candidates):
        return None

    cluster_path = os.path.join(date_folder, cluster_candidates[0])
    grid_path = os.path.join(date_folder, grid_candidates[0])
    try:
        header_clusters, row_labels_clusters, clusters = load_csv_data(cluster_path)
        header_grid, row_labels_grid, grid = load_csv_data(grid_path)
    except Exception as e:
        print(f"Error loading {file_type} files in {date_folder}: {e}")
        return None

    # Remove noise: keep only clusters with at least 'threshold' nonzero cells.
    nonzero = clusters[(~np.isnan(clusters)) & (clusters != 0)]
    if nonzero.size == 0:
        valid_ids = np.array([])
    else:
        unique_ids, counts = np.unique(nonzero, return_counts=True)
        valid_ids = unique_ids[counts >= threshold]
    mask = np.in1d(clusters, valid_ids).reshape(clusters.shape)
    # Set cells that do not meet the threshold to 0 (or you could set them to np.nan if preferred)
    filtered_clusters = np.where(mask, clusters, 0)
    filtered_grid = np.where(mask, grid, 0)
    
    return {
        "header_clusters": header_clusters,
        "row_labels_clusters": row_labels_clusters,
        "header_grid": header_grid,
        "row_labels_grid": row_labels_grid,
        "original_clusters": clusters,
        "original_grid": grid,
        "filtered_clusters": filtered_clusters,
        "filtered_grid": filtered_grid,
        "cluster_file": cluster_path,
        "grid_file": grid_path
    }

def footprint_check(acc_result, erosion_grid, buffer_bins=20):
    """
    For each accretion event in acc_result["filtered_clusters"], performs a footprint check:
      - Determines the event’s alongshore (row) and vertical (column) extents.
      - Defines the accretion event’s top as its highest column index.
      - Expands the alongshore extent by buffer_bins on each side.
      - Extracts from the erosion grid the region covering the expanded alongshore range
        and the vertical range from the accretion event’s top to the top of the grid.
      - Checks that there is at least one erosion cell (value > 0) within that footprint.
      - If no such cell exists, the accretion event is removed.
    Returns updated filtered_clusters and filtered_grid.
    """
    acc_clusters = acc_result["filtered_clusters"].copy()
    acc_grid = acc_result["filtered_grid"].copy()
    unique_ids = np.unique(acc_clusters[(acc_clusters != 0)])
    
    for cid in unique_ids:
        indices = np.where(acc_clusters == cid)
        if indices[0].size == 0:
            continue

        alongshore_min = indices[0].min()
        alongshore_max = indices[0].max()
        acc_top = indices[1].max()
        
        new_alongshore_min = max(0, alongshore_min - buffer_bins)
        new_alongshore_max = min(erosion_grid.shape[0], alongshore_max + buffer_bins + 1)
        
        footprint = erosion_grid[new_alongshore_min:new_alongshore_max, acc_top:erosion_grid.shape[1]]
        
        if not np.any(np.nan_to_num(footprint) > 0):
            acc_clusters[indices] = 0
            acc_grid[indices] = 0
            print(f"Accretion event {cid} removed: no erosion cell found in footprint "
                  f"(rows {new_alongshore_min}-{new_alongshore_max}, cols {acc_top}-{erosion_grid.shape[1]}).")
    
    return acc_clusters, acc_grid

def plot_bubble(clusters, grid, title, bubble_scale=100, color=None):
    """
    Computes cluster centroids and volumes from a clusters grid and its corresponding grid.
    Assumes rows represent alongshore (x-axis) and columns represent vertical (y-axis).
    Bubble size is proportional to the cluster volume.
    """
    mask = (clusters != 0)
    if np.sum(mask) == 0:
        print("No clusters to plot for", title)
        return
    rows, cols = np.where(mask)
    cluster_ids = clusters[mask]
    unique_ids, inv_idx, counts = np.unique(cluster_ids, return_inverse=True, return_counts=True)
    centroid_alongshore = np.bincount(inv_idx, weights=rows) / counts
    centroid_vertical = np.bincount(inv_idx, weights=cols) / counts
    volumes = np.bincount(inv_idx, weights=np.nan_to_num(grid[mask])) * 0.01
    if color is not None:
        plt.scatter(centroid_alongshore, centroid_vertical, s=volumes * bubble_scale, 
                    alpha=0.6, edgecolor='k', color=color)
    else:
        plt.scatter(centroid_alongshore, centroid_vertical, s=volumes * bubble_scale, 
                    alpha=0.6, edgecolor='k')
    plt.title(title)
    plt.xlabel("Alongshore (Row Index)")
    plt.ylabel("Vertical (Column Index)")
    plt.xlim(0, grid.shape[0])
    plt.ylim(0, grid.shape[1])

def clean_lidar_data(parent_folder, testing=True, replace=False, threshold=25, erosion=True):
    """
    For each date subdirectory in parent_folder, processes either erosion or accretion files.
    Creates a subfolder 'cleaned' in each date folder and writes out CSVs that have the same
    header and row labels as the incoming files.
    """
    date_folders = [os.path.join(parent_folder, d) for d in os.listdir(parent_folder)
                    if os.path.isdir(os.path.join(parent_folder, d))]
    if testing:
        date_folders = random.sample(date_folders, min(5, len(date_folders)))
    
    plot_results = []
    overall_start = time.time()
    for date_folder in date_folders:
        print(f"\nProcessing date folder: {date_folder}")
        folder_start = time.time()
        cleaned_folder = os.path.join(date_folder, "cleaned")
        
        file_type = "erosion" if erosion else "accretion"
        date_name = os.path.basename(date_folder)
        
        if erosion:
            clusters_out = os.path.join(cleaned_folder, f"{date_name}_ero_clusters_cleaned.csv")
            grid_out = os.path.join(cleaned_folder, f"{date_name}_ero_grid_cleaned.csv")
        else:
            clusters_out = os.path.join(cleaned_folder, f"{date_name}_acc_clusters_cleaned.csv")
            grid_out = os.path.join(cleaned_folder, f"{date_name}_acc_grid_cleaned.csv")
        
        if not testing and not replace and os.path.exists(clusters_out) and os.path.exists(grid_out):
            print(f"Skipping {date_folder} because output files exist and replace=False.")
            continue
        
        if not os.path.exists(cleaned_folder):
            if not testing:
                os.makedirs(cleaned_folder)
                print(f"Created folder: {cleaned_folder}")
            else:
                print(f"[TESTING] Would create folder: {cleaned_folder}")
        
        result = process_files_in_folder(date_folder, file_type, threshold)
        
        if file_type == "accretion" and result is not None:
            erosion_result = process_files_in_folder(date_folder, "erosion", threshold)
            if erosion_result is not None:
                new_clusters, new_grid = footprint_check(result, erosion_result["original_grid"], buffer_bins=20)
                result["filtered_clusters"] = new_clusters
                result["filtered_grid"] = new_grid
                print("Applied footprint check for accretion events.")
            else:
                print("No erosion data found for footprint check; skipping it.")
        
        if result is not None:
            save_csv_data(clusters_out, result["filtered_clusters"],
                          result["header_clusters"], result["row_labels_clusters"],
                          testing, replace)
            save_csv_data(grid_out, result["filtered_grid"],
                          result["header_grid"], result["row_labels_grid"],
                          testing, replace)
        else:
            print(f"No valid {file_type} files found in {date_folder}.")
        
        folder_duration = time.time() - folder_start
        print(f"Finished processing {date_name} in {folder_duration:.2f} seconds.")
        
        if testing:
            erosion_result = None
            if file_type == "accretion":
                erosion_result = process_files_in_folder(date_folder, "erosion", threshold)
            plot_results.append({
                "date": date_folder,
                "result": result,
                "file_type": file_type,
                "erosion_result": erosion_result if file_type == "accretion" else None
            })
    
    overall_duration = time.time() - overall_start
    print(f"\nTotal processing time for {len(date_folders)} folders: {overall_duration:.2f} seconds.")
    
    if testing and plot_results:
        for res in plot_results:
            date_folder = res["date"]
            file_type = res["file_type"]
            result = res["result"]
            plt.figure(figsize=(12, 6))
            if file_type == "accretion":
                plt.suptitle(f"Accretion Bubble Plots for {os.path.basename(date_folder)} (threshold >= {threshold} cells)", fontsize=16)
                plt.subplot(2, 1, 1)
                if result is not None:
                    plot_bubble(result["original_clusters"], result["original_grid"], "Original Accretion (blue) + Erosion (red)", bubble_scale=10, color="blue")
                    if res["erosion_result"] is not None:
                        plot_bubble(res["erosion_result"]["original_clusters"], res["erosion_result"]["original_grid"], "Original Erosion", bubble_scale=10, color="red")
                    blue_patch = Patch(facecolor='blue', edgecolor='k', label='Accretion')
                    red_patch = Patch(facecolor='red', edgecolor='k', label='Erosion')
                    plt.legend(handles=[blue_patch, red_patch])
                else:
                    plt.text(0.5, 0.5, "No Accretion Data", ha='center', va='center')
                plt.subplot(2, 1, 2)
                if result is not None:
                    plot_bubble(result["filtered_clusters"], result["filtered_grid"], "Filtered Accretion", bubble_scale=10)
                else:
                    plt.text(0.5, 0.5, "No Accretion Data", ha='center', va='center')
            else:
                plt.suptitle(f"Erosion Bubble Plots for {os.path.basename(date_folder)} (threshold >= {threshold} cells)", fontsize=16)
                plt.subplot(2, 1, 1)
                if result is not None:
                    plot_bubble(result["original_clusters"], result["original_grid"], "Original Erosion", bubble_scale=10)
                else:
                    plt.text(0.5, 0.5, "No Erosion Data", ha='center', va='center')
                plt.subplot(2, 1, 2)
                if result is not None:
                    plot_bubble(result["filtered_clusters"], result["filtered_grid"], "Filtered Erosion", bubble_scale=10)
                else:
                    plt.text(0.5, 0.5, "No Erosion Data", ha='center', va='center')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()

# Example usage:
# parent_folder = "/path/to/your/parent_folder"
# clean_lidar_data(parent_folder, testing=False, replace=False, threshold=25, erosion=True)
