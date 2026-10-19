import pathlib
import sys

from governmental_core import ROOT
from governmental_core.records import all_record_files, check_file


def main() -> int:
    files = [pathlib.Path(a) for a in sys.argv[1:]] or all_record_files()
    failed = False
    for f in files:
        errs = check_file(f)
        shown = f.relative_to(ROOT) if f.resolve().is_relative_to(ROOT) else f
        print(f"{'FAIL' if errs else 'ok  '} {shown}")
        for e in errs:
            print(f"      {e}")
        failed |= bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
