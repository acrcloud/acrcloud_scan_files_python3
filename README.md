# ACRCloud Scan Tool (Python3)

## Overview
  [ACRCloud](https://www.acrcloud.com/) provides [Automatic Content Recognition](https://www.acrcloud.com/docs/introduction/automatic-content-recognition/) services for [Audio Fingerprinting](https://www.acrcloud.com/docs/introduction/audio-fingerprinting/) based applications such as **[Audio Recognition](https://www.acrcloud.com/music-recognition)** (supports music, video, ads for both online and offline), **[Broadcast Monitoring](https://www.acrcloud.com/broadcast-monitoring)**, **[Second Screen](https://www.acrcloud.com/second-screen-synchronization)**, **[Copyright Protection](https://www.acrcloud.com/copyright-protection-de-duplication)** and etc.<br>
  
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

X86: [download and install Library(windows/vcredist_x86.exe)](https://www.microsoft.com/en-us/download/details.aspx?id=5555)
 
X64: [download and install Library(windows/vcredist_x64.exe)](https://www.microsoft.com/en-us/download/details.aspx?id=14632)
 

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
  -s, --split-results / --no-split
                                  Each audio/video file generate a report
  -c, --scan-type [music|custom|both]
                                  scan type
  -s, --start-time-ms INTEGER     scan start time
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
  - If you are using Windows: Download [Docker Desktop for Windows](https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe) and install.
  - If you are using MacOs: Download [Docker Desktop for Mac](https://download.docker.com/mac/stable/Docker.dmg) and install.
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
  
