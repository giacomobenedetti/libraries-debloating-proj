from ldd import get_names, get_exported, check_intersection, run_libtree, run_ldd
from pprint import pprint
import configparser
from argparse import ArgumentParser
from json import loads

config = configparser.ConfigParser()
config.read('config.ini')
exs = loads(config['DEFAULT']['executable'])
# arg parser
parser = ArgumentParser()
# add an argument to print our the table
parser.add_argument("-t", "--table", help="Print out the bloating factor latex table", action="store_true")
parser.add_argument("-p", "--plot", help="Plot the bloating factor and total usage of libraries", action="store_true")
parser.add_argument("-n", "--names", help="Generate a csv with used function names for each library", dest="names")
libs = []


if __name__ == "__main__":
    args = parser.parse_args()

    if args.names:
        # Iterate libraries, and for each one of them create a csv storing: the name of the library and the name of functions used in that library
        for ex in exs:
            ldd_output, direct_deps = run_libtree(ex)
            names = get_names(ex)
            with open(f'csv/{args.names}/{ex.split("/")[-2]}_names.csv', 'w') as f:
                f.write("Library;Function\n")
                for lib in ldd_output:
                    exported = get_exported(lib)
                    print(lib, len(exported))
                    for name in names:
                        if name.split("@")[0] in ' '.join(exported):
                            f.write(f"{lib};{name}\n")
            print(f"Generated csv for {ex.split('/')[-2]}")
        exit(0)

    for ex in exs:
        ldd_output, direct_deps = run_libtree(ex)
        # ldd_output = run_ldd(ex)
        # pprint(ldd_output)

        exported = []
        for lib in ldd_output:
            libs.append(lib.split("/")[-1])
            print(f"Exported functions from {lib}")
            pprint(get_exported(lib))
            exported.extend(get_exported(lib))
            print("\n")

        # check how many of the functions in the executable are undefined
        names = get_names(ex)

        # # for each library in ldd output, check the bloating factor of the library
        # for lib in ldd_output:
        #     exported = get_exported(lib)
        #     # print(f"Exported functions from {lib}")
        #     # pprint(exported)
        #     print(f"Bloating in {lib}")
        #     try:
        #         print(f"Bloating factor: {len(exported) - check_intersection(exported, names)}, {((len(exported) - check_intersection(exported, names))/len(exported))*100}%")
        #         print("\n")
        #     except ZeroDivisionError:
        #         print(f"No exported functions: {lib}")
        #         print("\n")

        # generate a csv
        with open(f'csv/{ex.split("/")[-2]}.csv', 'w') as f:
            f.write("Library;# Unused Functions;% Unused Functions;# Total Functions;Direct\n")
            for lib in ldd_output:
                exported = get_exported(lib)
                print(lib, len(exported))
                direct = 1 if lib in direct_deps else 0  # Assuming you have a function is_direct_dependency(lib)
                try:
                    numbers = str(len(exported) - check_intersection(exported, names)).replace(".", ",")
                    percentage = str(((len(exported) - check_intersection(exported, names))/len(exported))*100).replace(".", ",")
                    f.write(f"{lib};{numbers};{percentage}%;{len(exported)};{direct}\n")
                except ZeroDivisionError:
                    f.write(f"{lib};NA;NA;NA;{direct}\n")

        # print only if the table argument is passed
        if args.table:
            table_tex = open(f"tables/{ex.split('/')[-1]}.tex", "w")
            escape = '\_'
            # Generate a latex table with the bloating factor of each library
            table_tex.write("\\begin{table}[h]\n\n")
            table_tex.write("\\centering\n")
            table_tex.write(f"\\caption{'{'}{ex.split('/')[-1].replace('_', escape)}{'}'}\n")
            table_tex.write("\\footnotesize\n")
            table_tex.write("\\begin{tabular}{l|c|c}\n")
            table_tex.write("\\toprule\n")
            table_tex.write("Library & Bloating Factor & Bloating Factor \% \\\\ \\midrule\n")
            for lib in ldd_output:
                exported = get_exported(lib)
                try:
                    if lib in direct_deps:
                        table_tex.write(f"\colorbox{'{'}gray!20{'}{'}{lib.replace('_', escape)}{'}'} & {len(exported) - check_intersection(exported, names)} & {((len(exported) - check_intersection(exported, names))/len(exported))*100}\% \\\\ \\hline\n")
                    else:   
                        table_tex.write(f"{lib.replace('_', escape)} & {len(exported) - check_intersection(exported, names)} & {((len(exported) - check_intersection(exported, names))/len(exported))*100}\% \\\\ \\hline\n")
                except ZeroDivisionError:
                    table_tex.write(f"{lib} & NA & NA \\\\ \\hline\n")
            table_tex.write("\\bottomrule\n")
            table_tex.write("\\end{tabular}\n")
            table_tex.write("\\end{table}\n")
            table_tex.write("\n")


    ocurrences = dict((x, libs.count(x)) for x in set(libs))
    sorted_occurrences = dict(sorted(ocurrences.items(), key=lambda item: item[1]))
    print(sorted_occurrences)

    # generate a csv
    with open(f'csv/ocurrences.csv', 'w') as f:
        f.write("Library;# Occurrences\n")
        for lib in sorted_occurrences:
            f.write(f"{lib};{sorted_occurrences[lib]}\n")
