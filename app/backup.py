import subprocess
from util.timing_decorator import timing_decorator


@timing_decorator
def main(source_dir, dest_dir, newemt_age_string):
    rsync_cmd = f"rsync -az {source_dir}/ {dest_dir}/"
    subprocess.run(rsync_cmd, shell=True)

    find_cmd = f"find {dest_dir} -type f \! -newermt '{newemt_age_string}'"
    subprocess.run(find_cmd, shell=True)


if __name__ == "__main__":
    main()
