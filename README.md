# ACRCloud Scan Tool (Python3)

## Overview
  [ACRCloud](https://www.acrcloud.com/) provides services such as **[Music Recognition](https://www.acrcloud.com/music-recognition)**, **[Broadcast Monitoring](https://www.acrcloud.com/broadcast-monitoring/)**, **[Custom Audio Recognition](https://www.acrcloud.com/second-screen-synchronization%e2%80%8b/)**, **[Copyright Compliance & Data Deduplication](https://www.acrcloud.com/copyright-compliance-data-deduplication/)**, **[Live Channel Detection](https://www.acrcloud.com/live-channel-detection/)**, and **[Offline Recognition](https://www.acrcloud.com/offline-recognition/)** etc.<br>

## Requirements
Follow one of the tutorials to create a project and get your host, access_key and access_secret.

 * [Recognize Music](https://docs.acrcloud.com/tutorials/recognize-music)
 * [Recognize Custom Content](https://docs.acrcloud.com/tutorials/recognize-custom-content)
 * [Broadcast Monitoring for Music](https://docs.acrcloud.com/tutorials/broadcast-monitoring-for-music)
 * [Broadcast Monitoring for Custom Content](https://docs.acrcloud.com/tutorials/broadcast-monitoring-for-custom-content)
 * [Detect Live & Timeshift TV Channels](https://docs.acrcloud.com/tutorials/detect-live-and-timeshift-tv-channels)
 * [Recognize Custom Content Offline](https://docs.acrcloud.com/tutorials/recognize-custom-content-offline)
 * [Recognize Live Channels and Custom Content](https://docs.acrcloud.com/tutorials/recognize-tv-channels-and-custom-content)

  
  This tool can scan audio/video files and detect audios you want to recognize such as music, ads.

Supported Format:
  
> Audio: mp3, wav, m4a, flac, aac, amr, ape, ogg ...
> Video: mp4, mkv, wmv, flv, ts, avi ...

## Features
-   [x] scan file
-   [x] scan folder
-   [x] export the report
-   [x] filter report result
-   [ ] custom report fields

## Notice

If you are using Windows. Please make sure you've installed Microsoft Visual C++ runtime

X86: [download and install Library(windows/vcredist_x86.exe)](https://github.com/acrcloud/acrcloud_sdk_python/blob/master/windows/vcredist_x86.exe)<br>
x64: [download and install Library(windows/vcredist_x64.exe)](https://github.com/acrcloud/acrcloud_sdk_python/blob/master/windows/vcredist_x64.exe)
 

## Getting Started
1. Install Python 3 **(64-bit)**
```
https://www.python.org/downloads/
```

2. Clone this repository / Download repository zip file
```bash
$ git clone https://github.com/acrcloud/acrcloud_scan_files_python3.git
```

3. Install requirements.txt:
```bash
$ python3 -m pip install -r requirements.txt
```


4. Copy `config.yaml.example` and save as `config.yaml`. Change the content of `config.yaml`, fill in your host, access_key and access_secret.


5. Run the script to scan your audio/video files:
```bash
$ python main.py -t ~/test/test.mp4
```
## Usage

```
Usage: main.py [OPTIONS]

Options:
  -t, --target TEXT               The target need to scan (a folder or a
                                  file).  [required]

  -o, --output TEXT               Output result to this folder. (Must be a
                                  folder path)

  --format [csv|json]             output format.(csv or json)
  -w, --with-duration / --no-duration
                                  Add played duration to the result
  --filter-results / --no-filter  Enable filter.(It must be used when the
                                  with-duration option is on)

  -p, --split-results / --no-split
                                  Each audio/video file generate a report
  -c, --scan-type [music|custom|both]
                                  scan type
  -s, --start-time-ms INTEGER     scan start time
  -e, --end-time-ms INTEGER       scan end time
  -f, --is-fp / --not-fp          scan fingerprint
  --help                          Show this message and exit.
```

## Results with played duration

**If you want your results to include played duration. Please email us (support@acrcloud.com) to get the usage and the permission**

- with played duration:

```bash
$ python main.py -t ~/test/test.mp4 -w
```
- with played duration and filter results

```bash
$ python main.py -t ~/test/test.mp4 -w --filter-results
```

## Using Docker
- Install Docker 
  - If you are using Windows or MacOS: Download [Docker Desktop](https://www.docker.com/products/docker-desktop) and install.
  - If you are using Linux: Open the Terminal and input `bash <(curl -s https://get.docker.com/)`
- Change the config file (config.yaml).
- Run following command 
  ```
  git clone https://github.com/acrcloud/acrcloud_scan_files_python3.git
  
  cd acrcloud_scan_files_python3
  
  sudo docker build -t acrcloud/acrscan .
  # Call it without arguments to display the full help
  sudo docker run --rm acrcloud/acrscan
  
  # Basic usage
  sudo docker run --rm -v $(pwd):/tmp -v /Users/acrcloud/:/music/ acrcloud/acrscan -t /test/test.mp4 -o /tmp
  
  You need to change /Users/acrcloud/ to the directory where your audio/video file is.
  And the report file will in the acrcloud_scan_files_python3 directory.
  
