import os
import shutil
import subprocess
from PIL import Image
from pathlib import Path
from util.timing_decorator import timing_decorator
from concurrent.futures import ThreadPoolExecutor
from common.files import scratch_dir, buffer_dir, IMAGE_EXTENSIONS

backup_dir = None
processed_site_dir = None
cache_dir = None

executor = ThreadPoolExecutor(99)

@timing_decorator
def main(site_directory):
    prepare_directories(site_directory)
    copy_site_directory()
    unzip_site_cache()
    compress_site_images()
    compress_site()
    delete_directories()
    executor.shutdown()


def prepare_directories(site_directory):
    global backup_dir, processed_site_dir, cache_dir
    backup_dir = f"{site_directory}(backup)"
    Path(site_directory).rename(Path(backup_dir))
    processed_site_dir = site_directory
    cache_dir = f"{processed_site_dir}/hts-cache"''

def copy_site_directory():
    shutil.rmtree(processed_site_dir, ignore_errors=True)
    shutil.copytree(backup_dir, processed_site_dir)

# needed for better compression
def unzip_site_cache():
    zip_files = [os.path.join(cache_dir, filename) for filename in os.listdir(cache_dir) if filename.endswith('.zip')]
    for zip_file in zip_files:
        subprocess.run(['7z', 'x', zip_file, '-o' + cache_dir])
        os.remove(zip_file)

@timing_decorator
def compress_site_images():
    dir = Path(processed_site_dir)
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
    name = Path(processed_site_dir).name
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
        f"{processed_site_dir}/*",
    ]
    subprocess.run(command)

def delete_directories():
    shutil.rmtree(backup_dir, ignore_errors=True)
    shutil.rmtree(processed_site_dir, ignore_errors=True)

if __name__ == "__main__":
    main()