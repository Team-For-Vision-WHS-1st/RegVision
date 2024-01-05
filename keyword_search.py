from __future__ import print_function
from __future__ import unicode_literals

import sys

import argparse
from Registry import Registry

def keyword():
    parser = argparse.ArgumentParser(
        description="Search for a string in a Windows Registry hive")
    parser.add_argument("registry_hive", type=str,
                        help="Path to the Windows Registry hive to process")
    parser.add_argument("query", type=str,
                        help="Query for which to search")
    parser.add_argument("-i", action="store_true", dest="case_insensitive",
                        help="Query for which to search")
    args = parser.parse_args()

    paths = []
    value_names = []
    values = []

    def rec(key, depth, needle):
        try:
            for value in key.values():
                if (args.case_insensitive and needle in value.name().lower()) or needle in value.name():
                    value_names.append((key.path(), value.name()))
                    sys.stdout.write("n")
                    sys.stdout.flush()
                try:
                    if (args.case_insensitive and needle in str(value.value()).lower()) or needle in str(value.value()):
                        values.append((key.path(), value.name()))
                        sys.stdout.write("v")
                        sys.stdout.flush()
                except (UnicodeEncodeError, UnicodeDecodeError):
                    pass

            for subkey in key.subkeys():
                if needle in subkey.name():
                    paths.append(subkey.path())
                    sys.stdout.write("p")
                    sys.stdout.flush()
                rec(subkey, depth + 1, needle)
        except Registry.RegistryParse.UnknownTypeException as e:
            # Ignore UnknownTypeException and continue
            sys.stderr.write(f"Ignoring UnknownTypeException: {e}\n")

    reg = Registry.Registry(args.registry_hive)
    needle = args.query
    if args.case_insensitive:
        needle = needle.lower()

    rec(reg.root(), 0, needle)
    print("")

    print("[Paths]")
    for path in paths:
        print("  - %s" % (path))
    if len(paths) == 0:
        print("  (none)")
    print("")

    print("[Value Names]")
    for pair in value_names:
        print("  - %s : %s" % (pair[0], pair[1]))
    if len(value_names) == 0:
        print("  (none)")
    print("")

    print("[Values]")
    for pair in values:
        print("  - %s : %s" % (pair[0], pair[1]))
    if len(values) == 0:
        print("  (none)")
    print("")


if __name__ == "__main__":
    keyword()
