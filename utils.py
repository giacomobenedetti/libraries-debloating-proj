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

    for csv in os.listdir("csv/per_executable"):
        # if not "PEMesh" in csv:
        #     continue
        data = pd.read_csv(f"csv/per_executable/{csv}", delimiter=";")
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
    ax1.set_yscale('log')

    # Line plot for mean bloating factor
    ax2 = ax1.twinx()
    ax2.plot(grouped_data["Library"], grouped_data["% Unused Functions"], color='r', marker='o')
    ax2.set_ylabel('Mean Bloating Factor (%)', color='r', fontsize=14)
    ax2.tick_params(axis='y', labelcolor='r')

    plt.tight_layout()
    plt.savefig("plots/bloating_factor.pdf")

def plot_bloating_histogram_per_executable():
    all_data_direct = []
    all_data_indirect = []

    for csv in os.listdir("csv/per_executable"):
        data = pd.read_csv(f"csv/per_executable/{csv}", delimiter=";")
        if "% Unused Functions" in data.columns and "# Total Functions" in data.columns and "Direct" in data.columns:
            data_direct = data[data["Direct"] == 1]
            data_indirect = data[data["Direct"] == 0]
            # Remove '%' and replace ',' with '.' for numeric conversion
            data_indirect["% Unused Functions"] = data_indirect["% Unused Functions"].str.replace('%', '').str.replace(',', '.').astype(float)
            data_direct["% Unused Functions"] = data_direct["% Unused Functions"].str.replace('%', '').str.replace(',', '.').astype(float)
            
            # Calculate the number of unused functions
            data_indirect["# Unused Functions"] = (data_indirect["% Unused Functions"] / 100) * data_indirect["# Total Functions"]
            data_direct["# Unused Functions"] = (data_direct["% Unused Functions"] / 100) * data_direct["# Total Functions"]
            # 
            # Create a new DataFrame with executable name, mean number of unused functions, and direct field
            executable_name = os.path.splitext(os.path.basename(csv))[0]
            unused_functions_direct = data_direct["# Unused Functions"].sum()
            unused_functions_indirect = data_indirect["# Unused Functions"].sum()
            
            
            all_data_direct.append({"Executable": executable_name, "Unused Functions": unused_functions_direct, "Direct": 1})
            all_data_indirect.append({"Executable": executable_name, "Unused Functions": unused_functions_indirect, "Direct": 0})
        else:
            print(f"Columns '% Unused Functions', '# Total Functions', or 'Direct' not found in {csv}")

    # Convert the list of dictionaries to a DataFrame
    bloat_data_indirect = pd.DataFrame(all_data_indirect)
    bloat_data_direct = pd.DataFrame(all_data_direct)

    if bloat_data_direct.empty:
        print("No valid data found.")
        return

    # Sort the DataFrame alphabetically by executable name
    bloat_data_indirect = bloat_data_indirect.sort_values(by="Executable")
    bloat_data_direct = bloat_data_direct.sort_values(by="Executable")

    # Separate data into direct and indirect dependencies
    # direct_data = bloat_data[bloat_data["Direct"] == 1].set_index("Executable")
    # indirect_data = bloat_data[bloat_data["Direct"] == 0].set_index("Executable")

    # print(bloat_data)

    # Reindex indirect_data to match direct_data
    # indirect_data = indirect_data.reindex(direct_data.index).fillna(0)

    # Calculate the percentage of indirect unused functions
    # total_unused_functions = direct_data["Unused Functions"] + indirect_data["Unused Functions"]
    # indirect_percentage = (indirect_data["Unused Functions"] / total_unused_functions) * 100

    # Plot horizontal stacked bar chart of mean number of unused functions per executable
    fig, ax = plt.subplots(figsize=(15, 8))

    bar_width = 0.35
    index = range(len(bloat_data_direct))

    direct_bars = ax.barh([i  for i in index], bloat_data_direct["Unused Functions"], bar_width, label='Direct', color='b', alpha=0.7)
    indirect_bars = ax.barh([i for i in index], bloat_data_indirect["Unused Functions"], bar_width, label='Indirect', color='r', alpha=0.7)
    ax.set_xlabel('Number of Unused Functions', fontsize=20)
    ax.set_ylabel('Executable', fontsize=20)
    ax.set_yticks(index)
    ax.set_xscale('log')
    ax.set_yticklabels(bloat_data_direct["Executable"], fontsize=16)
    ax.tick_params(axis='x', labelsize=16)
    ax.legend(fontsize=16)

    # Add percentage labels for indirect dependencies
    # for i in index:
    #     ax.text(total_unused_functions[i], i, f'{indirect_percentage[i]:.1f}%', va='center', ha='left', fontsize=12, color='black')

    plt.tight_layout()
    print("Saving plot to plots/bloating_per_executable.pdf")
    plt.savefig("plots/bloating_per_executable.pdf")
    # plt.show()

def generate_combined_functions_csv(input_dir='csv/function_names', output_file='combined_functions.csv'):
    all_functions = set()

    # Iterate over all CSV files in the input directory
    for csv_file in os.listdir(input_dir):
        if csv_file.endswith('.csv'):
            file_path = os.path.join(input_dir, csv_file)
            data = pd.read_csv(file_path, delimiter=";")
            
            # Check if the 'Library' and 'Function' columns exist
            if 'Library' in data.columns and 'Function' in data.columns:
                for _, row in data.iterrows():
                    all_functions.add((row['Library'], row['Function']))
            else:
                print(f"Columns 'Library' or 'Function' not found in {csv_file}")

    # Convert the list of dictionaries to a DataFrame
    combined_data = pd.DataFrame(all_functions)

    # Write the combined function names to a new CSV file
    combined_data.to_csv(output_file, index=False, sep=';')

    print(f"Combined functions CSV generated: {output_file}")

if __name__ == "__main__":
    # clone_repos()
    # check_cmake_files()
    # plot_imports_vs_bloating()
    # plot_bloating_factor()
    plot_bloating_histogram_per_executable()
    # generate_combined_functions_csv()