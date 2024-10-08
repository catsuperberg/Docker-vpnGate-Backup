import os
import schedule
import time
import importlib
import shutil
from pathlib import Path
import download_configs
import download_site
import compress_configs
import compress_site
import backup
from common.files import (
    scratch_dir,
    buffer_dir,
    buffer_config_dir,
    buffer_site_dir,
    backup_local_dir,
    backup_remote_dir,
    ERROR_POSTFIX,
    SITE_POSTFIX,
)

BUFFER_CONFIG_COUNT = 10
BUFFER_SITE_COUNT = 2
BUFFER_ERROR_COUNT = 10

CONFIG_UPDATE_INTERVAL_MINUTES = 15
SITE_UPDATE_INTERVAL_HOURS = 6

LOCAL_BACKUP_INTERVAL_HOURS = 2
REMOTE_BACKUP_INTERVAL_MINUTES = 30

LOCAL_BACKUP_MAX_AGE = "2 weeks ago"
REMOTE_BACKUP_MAX_AGE = "6 months ago"

SCRATCH_STALE_AGE_HOURS = 2


def main():
    print("Vpn backup script launched")
    create_ram_directories()
    schedule.every(CONFIG_UPDATE_INTERVAL_MINUTES).minutes.do(get_configs)
    schedule.every(SITE_UPDATE_INTERVAL_HOURS).hours.do(get_site)
    schedule.every(LOCAL_BACKUP_INTERVAL_HOURS).hours.do(local_backup)
    schedule.every(REMOTE_BACKUP_INTERVAL_MINUTES).minutes.do(remote_backup)

    while True:
        schedule.run_pending()
        time.sleep(1)


def get_configs():
    importlib.reload(download_configs)
    importlib.reload(compress_configs)
    directory = download_configs.main()
    compress_configs.main(directory)
    clear_stale_in_scratch()
    prune_buffer()


def get_site():
    importlib.reload(download_site)
    importlib.reload(compress_site)
    directory = download_site.main()
    compress_site.main(directory)
    clear_stale_in_scratch()
    prune_buffer()


def local_backup():
    backup.main(buffer_dir, backup_local_dir, LOCAL_BACKUP_MAX_AGE)


def remote_backup():
    backup.main(buffer_dir, backup_remote_dir, REMOTE_BACKUP_MAX_AGE)


def clear_stale_in_scratch():
    directory = Path(scratch_dir)
    folders_to_delete = [
        folder
        for folder in directory.iterdir()
        if folder.is_dir() and verify_is_old(folder, SCRATCH_STALE_AGE_HOURS)
    ]
    for folder in folders_to_delete:
        shutil.rmtree(folder)


def verify_is_old(directory, threshold_hours):
    hours_since_modification = (time.time() - directory.stat().st_mtime) / 3600
    return hours_since_modification >= threshold_hours


def prune_buffer():
    files = list(Path(buffer_dir).glob("*"))

    error_files = [str(file) for file in files if file.stem.endswith(ERROR_POSTFIX)]
    site_files = [str(file) for file in files if file.stem.endswith(SITE_POSTFIX)]
    config_files = [str(file) for file in files if file not in error_files + site_files]
    leave_only_latest(config_files, BUFFER_CONFIG_COUNT)
    leave_only_latest(site_files, BUFFER_SITE_COUNT)
    leave_only_latest(error_files, BUFFER_ERROR_COUNT)


def leave_only_latest(files_to_prune, count):
    files_by_age = sorted(
        files_to_prune, key=lambda file_path: os.path.getmtime(file_path), reverse=True
    )
    for file in files_by_age[count:]:
        os.remove(file)


def create_ram_directories():
    buffer = Path(buffer_dir)
    scratch = Path(scratch_dir)
    config = Path(buffer_site_dir)
    site = Path(buffer_config_dir)
    buffer.mkdir(exist_ok=True)
    scratch.mkdir(exist_ok=True)
    config.mkdir(exist_ok=True)
    site.mkdir(exist_ok=True)


if __name__ == "__main__":
    main()
