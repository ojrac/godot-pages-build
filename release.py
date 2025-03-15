#!/usr/bin/env python
import os
import shutil
import sys
from argparse import ArgumentParser
from os.path import join
from subprocess import run
from tempfile import TemporaryDirectory

PROJECT_NAME = "Build Test"
EXPORT_DIR = "Export"
EXPORT_PRESET = "Windows"
EXE_NAME = "ExportBuild.exe"

parser = ArgumentParser()
parser.add_argument("version", help="three numbers separated by dots, e.g. '1.7.13'")

def usage(msg):
    if msg:
        print(msg)
    parser.print_help()
    sys.exit(1)

def parse_version():
    args = parser.parse_args()

    try:
        version_parts = list(map(int, args.version.split(".")))
    except ValueError:
        usage()
    if len(version_parts) > 3:
        usage()
    return [version_parts[i] if i < len(version_parts) else 0
            for i in range(3)]


def remove(*paths):
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    
def export(platform: str, version_str: str):
    shutil.rmtree(EXPORT_DIR)
    os.makedirs(EXPORT_DIR, exist_ok=True)
    out_path = join(EXPORT_DIR, EXE_NAME)
    run(["godot", "--headless", "--verbose", "--export-release", platform, out_path])

    # TODO: Glob?
    files = [
        EXE_NAME,
        EXE_NAME.replace(".exe", ".pck"),
    ]

    with TemporaryDirectory() as dir:
        temp_path = join(dir, EXE_NAME.replace(".exe", ".zip"))
        run(["tar", "-c", "-a", "-f", temp_path, "-C", EXPORT_DIR, *files])
        archive_path = out_path.replace(".exe", f"-{version_str}.zip")
        os.rename(temp_path, archive_path)

        return archive_path

def release(build_path, version):
    args = [
        "bin/gh.exe",
        "release", "create",
        f"v{version}",
        build_path,
        "--title", f"{PROJECT_NAME} {version}",
        "--notes", "", # Disables interactive prompt for... title
    ]
    print(args)
    run(args)


def main():
    version = parse_version()
    version_str = ".".join(map(str, version))

    # Build
    build_path = export(EXPORT_PRESET, version_str)

    # Upload release
    release(build_path, version_str)

if __name__ == "__main__":
    main()