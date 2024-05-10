# EventRecorder
EventRecorder is a simple application to record timed events. It is useful to keep track of the time spent on different tasks, and to generate reports. 

# How to Install
## Linux
1. Download [EventRecorder.flatpak](https://github.com/FedericoCalzoni/EventRecorder/releases)
2. Double click and follow GUI installation or run
```bash
flatpak install EventRecorder.flatpak
```

## Windows
1. Download [EventRecorder.exe](https://github.com/FedericoCalzoni/EventRecorder/releases)
2. Double click to start the app

# Build
## Linux flatpak
Install runtimes:
```bash
sudo flatpak install flathub org.kde.Platform//6.7
sudo flatpak install flathub org.kde.Sdk//6.7
```
build:
``` bash
mkdir pyqt6
flatpak-builder --repo=repo --force-clean build-dir io.github.FedericoCalzoni.EventRecorder.json
flatpak build-export repo build-dir
flatpak build-bundle repo EventRecorder.flatpak io.github.FedericoCalzoni.EventRecorder
```


## Windows
```bash
pyinstaller --onefile --noconsole .\EventRecorder\EventRecorder.py
```
