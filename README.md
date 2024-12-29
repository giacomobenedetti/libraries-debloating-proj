# Project Goal

The goal of this project is to create a tool that identifies and retrieves the dependencies of a given software package. This helps in understanding the required components for the software to function correctly and aids in the process of debloating by removing unnecessary dependencies.

Removing unnecessary dependensies is key for a reduced attack surface, and to reduce the developers burden in analysing CVE identified through software composition analysis (SCA) tools.

This project primarily targets the analysis of libraries developed within the IMATI (Institute of Applied Mathematics and Information Technology) or those where IMATI members have contributed. The goal is to evaluate the performance, usability, and overall impact of these libraries in their respective domains.

## Usage

To use this project, you need to build the Dockerfile provided. The Dockerfile contains all the necessary system dependencies required to test the binaries contained in the programs. Follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/giacomobenedetti/libraries-debloating-proj
    cd libraries-debloating-proj
    ```

2. Build the Docker image:
    ```sh
    docker build -t libraries-debloating-proj .
    ```

3. Run the Docker container:
    ```sh
    docker run -v $PWD:/home -it libraries-debloating-proj
    ```

This will set up an environment with all the dependencies needed to analyze and test the binaries of the software packages.

4. Run the main script inside the container:
    ```sh
    cd /home
    python3 main.py
    ```

This will execute the main script which performs the dependency analysis on the software packages.


## Main Script Overview

The `main.py` script is the core component of this project. It performs the following steps:

1. **Input Parsing**: The script runs the analysis on binaries listed in `config.ini`. 

2. **Dependency Analysis**: The script then analyzes the specified software package to identify its dependencies. This involves examining the shared libraries linked in the binary. The script uses [`libtree`](https://github.com/haampie/libtree) at the highest level of verbosity (`-vvv`), parsing its output.
 
3. **Undefined Functions Retrieval**: The functions that are tagged as undefined inside of the binary are retrieved. We use `nm` to collect functions tagged as `U` (i.e., undefined). Those are the functions which are called in the binary, but that are statically missing an implementation.

4. **Exported Functions Retrieval**: The set of exported functions is identified for each shared library in the identified depedencies. Using `nm` on each library, we collect functions tagget with `T`.

By following these steps, the `main.py` script provides a comprehensive analysis of the dependencies required by the software package, aiding in the debloating process by identifying unnecessary components.

# Acknowledgement
This work has been supported by the project "Analisi delle dipendenze e dell’efficacia del debloating per il software sviluppato dal gruppo di ricerca afferente al progetto autofinanziato DIT.AD004.181" 

