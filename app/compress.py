import os
import pathlib
import shutil
import subprocess
from glob import glob
from PIL import Image
from util.timing_decorator import timing_decorator
from concurrent.futures import ThreadPoolExecutor
from common.files import scratch_dir, download_dir, processed_dir, CONFIG_FILE_EXTENSION, site_dir, processed_site_dir, IMAGE_EXTENSIONS

CACHE_DIR = f"{processed_site_dir}/hts-cache"''

executor = ThreadPoolExecutor(99)

@timing_decorator
def main():
    copy_config_directory()
    remove_config_comments()
    compress_configs()

    copy_site_directory()
    unzip_site_cache()
    compress_site_images()
    compress_site()


def copy_config_directory():
    shutil.rmtree(processed_dir, ignore_errors=True)
    shutil.copytree(download_dir, processed_dir)

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
    name = "compressed-configs"
    file = f"{scratch_dir}/{name}.7z"
    pathlib.Path(file).unlink(missing_ok=True)
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


# needed for better compression
def unzip_site_cache():
    zip_files = [os.path.join(CACHE_DIR, filename) for filename in os.listdir(CACHE_DIR) if filename.endswith('.zip')]
    for zip_file in zip_files:
        subprocess.run(['7z', 'x', zip_file, '-o' + CACHE_DIR])
        os.remove(zip_file)

def copy_site_directory():
    shutil.rmtree(processed_site_dir, ignore_errors=True)
    shutil.copytree(site_dir, processed_site_dir)

@timing_decorator
def compress_site_images():
    dir = pathlib.Path(processed_site_dir)
    print("Started image compression")
    images = [f for f in dir.rglob('*') if f.is_file() and f.suffix in IMAGE_EXTENSIONS]
    executor.map(compress_image, images)
    print(f"Compressed {len(images)} in site backup")

def compress_image(image):
    if (os.stat(image).st_size <= 0): return

    with Image.open(image) as im:
        if im.format == 'PNG':
            low_color = im.convert("P", palette=Image.ADAPTIVE, colors=6)
            low_color.save(image, optimize=True)
        elif im.format == 'JPEG':
            im.save(image, im.format, quality=13, optimize=True)

@timing_decorator
def compress_site():
    name = "compressed-site"
    file = f"{scratch_dir}/{name}.7z"
    pathlib.Path(file).unlink(missing_ok=True)
    command = [
        "7z",
        "a",
        "-t7z",
        "-mx=5",
        "-ms=on",
        "-m0=LZMA2",
        file,
        f"{processed_site_dir}/*",
    ]
    subprocess.run(command)

if __name__ == "__main__":
    main()