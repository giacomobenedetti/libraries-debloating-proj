import json
import os
from matplotlib import pyplot as plt
from pandas import read_csv, concat
import pandas as pd
import csv

def write_aggregated_data_to_csv(data, filename='aggregated_data.csv'):
    # Get the root directory of the project
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(root_dir, filename)

    print(f"Writing aggregated data to {file_path}")
    
    # Get the header from the columns of the dataframe
    header = data.columns
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for row in data.itertuples(index=False):
            writer.writerow(row)

# Get the repositories.json file and clone all the repositories in repos folder
def clone_repos():
    with open("repositories.json", "r") as f:
        repos = json.load(f)
        for repo in repos['repositories']:
            print(f"Cloning {repo}")
            # if the current directory is not repos, change to repos
            if os.getcwd().split("/")[-1] != "repos":
                os.chdir("repos")
            os.system(f"git clone --recursive {repo}")




# For each repo in repos check the parameters used for compiling the project, They are contained in the cmake files
def check_cmake_files():
    for repo in os.listdir("repos"):
        print(f"Checking {repo}")
        if os.path.isdir(f"repos/{repo}"):
            os.chdir(f"repos/{repo}")
            os.system("find . -name CMakeLists.txt -exec grep -Hn 'add_executable' {} \;")
            os.chdir("../../")


def plot_bloating_factor():
    all_data = []

    for csv in os.listdir("csv"):
        data = pd.read_csv(f"csv/{csv}", delimiter=";")
        if "% Unused Functions" in data.columns:
            # Remove '%' and replace ',' with '.' for numeric conversion
            data["% Unused Functions"] = data["% Unused Functions"].str.replace('%', '').str.replace(',', '.').astype(float)
            all_data.append(data)
        else:
            print(f"Column '% Unused Functions' not found in {csv}")

    if not all_data:
        print("No valid data found.")
        return

    # Concatenate all dataframes
    combined_data = pd.concat(all_data)

    # Remove libraries that contain 'libicudata.so.74' from the dataset
    combined_data = combined_data[~combined_data["Library"].str.contains("libicudata.so.74")]

    # Group by library name and compute mean bloating factor and total usage
    grouped_data = combined_data.groupby("Library").agg({
        "# Total Functions": "sum",
        "% Unused Functions": "mean"
    }).reset_index()

    # Extract the last part of the library name
    grouped_data["Library"] = grouped_data["Library"].apply(lambda x: x.split('/')[-1])

    # Write the aggregated data to a CSV file
    write_aggregated_data_to_csv(grouped_data)

    # Plotting
    fig, ax1 = plt.subplots(figsize=(15, 8))  # Adjust the figure size here

    # Bar plot for total usage
    ax1.bar(grouped_data["Library"], grouped_data["# Total Functions"], color='b', alpha=0.6)
    ax1.set_xlabel('Libraries', fontsize=14)
    ax1.set_ylabel('Total Exported Functions', color='b', fontsize=14)
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xticklabels(grouped_data["Library"], rotation=45, ha='right')

    # Line plot for mean bloating factor
    ax2 = ax1.twinx()
    ax2.plot(grouped_data["Library"], grouped_data["% Unused Functions"], color='r', marker='o')
    ax2.set_ylabel('Mean Bloating Factor (%)', color='r', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='r')

    fig.tight_layout()
    plt.savefig("plots/bloating_factor_analysis.pdf")
    plt.show()


def plot_imports_vs_bloating():
    all_data = []

    for csv in os.listdir("csv"):
        data = pd.read_csv(f"csv/{csv}", delimiter=";")
        if "% Unused Functions" in data.columns:
            # Remove '%' and replace ',' with '.' for numeric conversion
            data["% Unused Functions"] = data["% Unused Functions"].str.replace('%', '').str.replace(',', '.').astype(float)
            all_data.append(data)
        else:
            print(f"Column '% Unused Functions' not found in {csv}")

    if not all_data:
        print("No valid data found.")
        return

    # Concatenate all dataframes
    combined_data = pd.concat(all_data)

    # Remove libraries that contain 'libicudata.so.74' from the dataset
    combined_data = combined_data[~combined_data["Library"].str.contains("libicudata.so.74")]

    # Count the number of times each library is imported
    import_counts = combined_data["Library"].value_counts().reset_index()
    import_counts.columns = ["Library", "Import Count"]

    # Compute the mean bloating factor for each library
    mean_bloating = combined_data.groupby("Library")["% Unused Functions"].mean().reset_index()

    # Merge the import counts and mean bloating data
    merged_data = pd.merge(import_counts, mean_bloating, on="Library")

    # Extract the last part of the library name
    merged_data["Library"] = merged_data["Library"].apply(lambda x: x.split('/')[-1])

    # Plotting
    fig, ax1 = plt.subplots(figsize=(20, 12))  # Adjust the figure size here

    # Bar plot for import counts
    ax1.bar(merged_data["Library"], merged_data["Import Count"], color='b', alpha=0.6)
    ax1.set_xlabel('Libraries', fontsize=18)
    ax1.set_ylabel('Number of Imports', color='b', fontsize=18)
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.set_xticklabels(merged_data["Library"], rotation=45, ha='right', fontsize=12)

    # Line plot for mean bloating factor
    ax2 = ax1.twinx()
    ax2.plot(merged_data["Library"], merged_data["% Unused Functions"], color='r', marker='o')
    ax2.set_ylabel('Mean Bloating Factor (%)', color='r', fontsize=18)
    ax2.tick_params(axis='y', labelcolor='r')

    fig.tight_layout()
    plt.savefig("plots/imports_vs_bloating_factor.png")
    plt.show()

if __name__ == "__main__":
    # clone_repos()
    # check_cmake_files()
    # plot_imports_vs_bloating()
    plot_bloating_factor()