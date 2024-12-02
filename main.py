from ldd import run_ldd, get_names, get_exported, check_intersection
from pprint import pprint
import configparser
from argparse import ArgumentParser

config = configparser.ConfigParser()
config.read('config.ini')
ex = config['DEFAULT']['executable']
# arg parser
parser = ArgumentParser()
# add an argument to print our the table
parser.add_argument("-t", "--table", help="Print out the bloating factor latex table", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    ldd_output = run_ldd(ex)
    # pprint(ldd_output)
    exported = []
    for lib in ldd_output:
        # print(f"Exported functions from {lib}")
        # pprint(get_exported(lib))
        exported.extend(get_exported(lib))
        # print("\n")

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
