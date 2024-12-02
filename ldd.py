from subprocess import check_output
from shlex import split
from re import findall

'''
    Run lddtree to get the shared libraries used by the executable and format them to have a flat list of shared libraries
'''
def run_ldd(program: str):
    output = check_output(split(f"lddtree {program}"))
    output = output.decode()
    output = output.split("\n")
    output = [x for x in output if "=>" in x]
    output = [x.split("=>")[1].strip().split(" ")[0] for x in output]
    return output


def get_exported(shared_lib: str):
    output = check_output(split(f"nm -D {shared_lib}"))
    output = output.decode()
    output = output.split("\n")
    output = [x.strip().split(" ") for x in output]
    result = []
    for x in output:
        if len(x) > 1:
            if x[1] == "T":
                result.append(x[2])
    return result
    
'''
    nm returns an output like:
                     w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
                 w __cxa_finalize@GLIBC_2.2.5
                 w __gmon_start__
                 U __isoc99_scanf@GLIBC_2.7
                 U __libc_start_main@GLIBC_2.34
                 U __stack_chk_fail@GLIBC_2.4
                 U cos@GLIBC_2.2.5
                 U printf@GLIBC_2.2.5

    This function extracts the function names tagged with U             
    '''

def get_names(program: str):
    output = check_output(split(f"nm -D {program}"))
    output = output.decode()
    output = output.split("\n")
    output = [x.strip().split(" ") for x in output]
    result = []
    for x in output:
        print(x)
        if len(x) > 1:
            if x[0] == "U":
                result.append(x[1])
    return result

'''
    Check how many functions match between the results of ldd and nm
    The check takes into consideration that it may happen the function exported has two @ in the name
'''

def check_intersection(ldd: list, nm: list):
    count = 0
    for x in nm:
        # if x in ldd or x.replace("@", "@@") in ldd:
        if x.split("@")[0] in ' '.join(ldd):
            count += 1
    return count
