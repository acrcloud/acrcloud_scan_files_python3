FROM python:3.7.5-slim-buster

COPY . /acr_scan_tool
WORKDIR /acr_scan_tool
RUN chmod +x /acr_scan_tool/main.py

ENV PATH=${PATH}:/acr_scan_tool

RUN apt-get update \
&& apt-get install -y --no-install-recommends git ffmpeg\
&& apt-get purge -y --auto-remove \
&& rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt
RUN python3 /acr_scan_tool/main.py --help
ENTRYPOINT ["main.py"]
