import time
import download_configs, download_site, compress

while True:
    download_configs.main()
    download_site.main()
    compress.main()
    time.sleep(25)