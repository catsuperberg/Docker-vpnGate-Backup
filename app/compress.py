import os
import pathlib
import shutil
import subprocess
from glob import glob
from util.timing_decorator import timing_decorator
from concurrent.futures import ThreadPoolExecutor
from common.files import scratch_dir, download_dir, processed_dir, CONFIG_FILE_EXTENSION

executor = ThreadPoolExecutor(99)

@timing_decorator
def main():
    copy_directory()
    remove_comments()
    compress_folder()

def copy_directory():
    shutil.rmtree(processed_dir, ignore_errors=True)
    shutil.copytree(download_dir, processed_dir)

@timing_decorator
def remove_comments():
    configs = [y for x in os.walk(processed_dir) for y in glob(os.path.join(x[0], f"*{CONFIG_FILE_EXTENSION}"))]
    config_updates = executor.map(strip_lines, configs)
    executor.map(write_config, config_updates)

def strip_lines(config):
    with open(config, 'r', errors='replace') as file:
        lines = file.readlines()
    return config, ''.join([line for line in lines if line.strip() and not line.startswith("#")])

def write_config(config_update):
    with open(config_update[0], 'w') as file:
        file.write(config_update[1])

@timing_decorator
def compress_folder():
    name = "compressed"
    file = f"{scratch_dir}/{name}.7z"
    file_zip = f"{scratch_dir}/{name}.zip"
    pathlib.Path(file).unlink(missing_ok=True)
    pathlib.Path(file_zip).unlink(missing_ok=True)
    commands = [
        [
            "7z",
            "a",
            "-t7z",
            "-mx=5",
            "-ms=on",
            "-m0=LZMA2",
            file,
            f"{processed_dir}/*",
        ],
        [
            "7z",
            "a",
            "-mx=5",
            "-mm=Deflate",
            file_zip,
            f"{processed_dir}/*",
        ]
    ]
    processes = [subprocess.Popen(command) for command in commands]
    for process in processes: process.wait()

if __name__ == "__main__":
    main()