import time
import download_configs, compress

while True:
    download_configs.main()
    compress.main()
    time.sleep(25)