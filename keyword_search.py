from __future__ import print_function
from __future__ import unicode_literals

import sys
import argparse
from Registry import Registry, RegistryParse
import pandas as pd

def keyword(registry_hive, query, case_insensitive):
    paths = []
    value_names = []
    values = []

    def rec(key, depth, needle):
        try:
            for value in key.values():
                if (case_insensitive and needle in value.name().lower()) or needle in value.name():
                    value_names.append((key.path(), value.name()))
                try:
                    if (case_insensitive and needle in str(value.value()).lower()) or needle in str(value.value()):
                        values.append((key.path(), value.name()))
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass

            for subkey in key.subkeys():
                if needle in subkey.name():
                    paths.append(subkey.path())
                rec(subkey, depth + 1, needle)
        except RegistryParse.UnknownTypeException as e:
            # Ignore UnknownTypeException and continue
            sys.stderr.write(f"Ignoring UnknownTypeException: {e} at offset {key.offset()}\n")
        except Exception as ex:
            sys.stderr.write(f"Exception: {ex}\n")

    reg = Registry.Registry(registry_hive)
    needle = query
    if case_insensitive:
        needle = needle.lower()

    rec(reg.root(), 0, needle)

    result_dict = {
        "Paths": paths,
        "ValueNames": value_names,
        "Values": values
    }

    return result_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for a string in a Windows Registry hive")
    parser.add_argument("registry_hive", type=str,
                        help="Path to the Windows Registry hive to process")
    parser.add_argument("query", type=str,
                        help="Query for which to search")
    parser.add_argument("-i", action="store_true", dest="case_insensitive",
                        help="Query for which to search")
    args = parser.parse_args()

    results = keyword(args.registry_hive, args.query, args.case_insensitive)
    df = pd.DataFrame(results)