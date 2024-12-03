from ldd import get_names, get_exported, check_intersection, run_libtree
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

libs = []

if __name__ == "__main__":
    args = parser.parse_args()
    for ex in exs:
        ldd_output = run_libtree(ex)
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

        # for each library in ldd output, check the bloating factor of the library
        for lib in ldd_output:
            exported = get_exported(lib)
            # print(f"Exported functions from {lib}")
            # pprint(exported)
            print(f"Bloating in {lib}")
            try:
                print(f"Bloating factor: {len(exported) - check_intersection(exported, names)}, {((len(exported) - check_intersection(exported, names))/len(exported))*100}%")
                print("\n")
            except ZeroDivisionError:
                print(f"No exported functions: {lib}")
                print("\n")

        # generate a csv
        with open(f'csv/{ex.split("/")[-1]}.csv', 'w') as f:
            f.write("Library;# Unused Functions;% Unused Functions\n")
            for lib in ldd_output:
                exported = get_exported(lib)
                try:
                    numbers = str(len(exported) - check_intersection(exported, names)).replace(".", ",")
                    percentage = str(((len(exported) - check_intersection(exported, names))/len(exported))*100).replace(".", ",")
                    f.write(f"{lib};{numbers};{percentage}%\n")
                except ZeroDivisionError:
                    f.write(f"{lib};NA;NA\n")
        



        # print only if the table argument is passed
        if args.table:
            escape = '\_'
            # Generate a latex table with the bloating factor of each library
            print("\\begin{table}[]")
            print("\\begin{tabular}{|l|l|l|}")
            print("\\hline")
            print("Library & Bloating Factor & Bloating Factor \% \\\\ \\hline")
            for lib in ldd_output:
                exported = get_exported(lib)
                try:
                    print(f"{lib.replace('_', escape)} & {len(exported) - check_intersection(exported, names)} & {((len(exported) - check_intersection(exported, names))/len(exported))*100}\% \\\\ \\hline")
                except ZeroDivisionError:
                    print(f"{lib} & NA & NA \\\\ \\hline")
            print("\\end{tabular}")
            print("\\end{table}")
            print("\n")


    ocurrences = dict((x, libs.count(x)) for x in set(libs))
    sorted_occurrences = dict(sorted(ocurrences.items(), key=lambda item: item[1]))
    print(sorted_occurrences)
