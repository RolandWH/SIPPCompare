import os.path
import sys


# Returns the correct path for Nuitka onefile mode, standalone mode or normal Python
# Credit: https://nuitka.net/user-documentation/common-issue-solutions.html#onefile-finding-files
def get_res_path(relative_path):
    path_a = ""

    try:
        path_a = os.path.join(sys.__compiled__.containing_dir, relative_path)
    except AttributeError:
        pass

    path_b = os.path.join(os.path.dirname(__file__), relative_path)
    path_c = os.path.join(os.path.dirname(sys.argv[0]), relative_path)

    if os.path.isfile(path_a):
        return path_a
    elif os.path.isfile(path_b):
        return path_b
    elif os.path.isfile(path_c):
        return path_c
    else:
        return os.path.join(os.path.abspath("."), relative_path)
