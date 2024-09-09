import os
import shutil
import subprocess
from glob import glob
from pathlib import Path
from util.timing_decorator import timing_decorator
from concurrent.futures import ThreadPoolExecutor
from common.files import buffer_dir, CONFIG_FILE_EXTENSION

executor = ThreadPoolExecutor(99)

processed_dir = None
backup_dir = None

@timing_decorator
def main(config_directory):
    prepare_directories(config_directory)
    copy_config_directory()
    remove_config_comments()
    compress_configs()
    delete_directories()
    executor.shutdown()


def prepare_directories(config_directory):
    global processed_dir, backup_dir
    backup_dir = f"{config_directory}(backup)"
    Path(config_directory).rename(Path(backup_dir))
    processed_dir = config_directory


def copy_config_directory():
    shutil.rmtree(processed_dir, ignore_errors=True)
    shutil.copytree(backup_dir, processed_dir)

@timing_decorator
def remove_config_comments():
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
def compress_configs():
    name = Path(processed_dir).name
    file = f"{buffer_dir}/{name}.7z"
    Path(file).unlink(missing_ok=True)
    command = [
        "7z",
        "a",
        "-t7z",
        "-mx=5",
        "-ms=on",
        "-m0=LZMA2",
        file,
        f"{processed_dir}/*",
    ]
    subprocess.run(command)

def delete_directories():
    shutil.rmtree(backup_dir, ignore_errors=True)
    shutil.rmtree(processed_dir, ignore_errors=True)

if __name__ == "__main__":
    main()