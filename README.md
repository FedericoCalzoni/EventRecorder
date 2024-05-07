# Install
## Linux
1. Download [EventRecorder.flatpak](https://github.com/FedericoCalzoni/EventRecorder/releases)
2. Double click and follow GUI install or run
```bash
flatpak install EventRecorder.flatpak
```

## Windows
1. Download [EventRecorder.exe](https://github.com/FedericoCalzoni/EventRecorder/releases)
2. Double click to start app

# Build
## Linux flatpak Build
``` bash
flatpak-builder --repo=repo --force-clean build-dir com.UBM.EventRecorder.json
flatpak build-export repo build-dir 
flatpak build-bundle repo EventRecorder.flatpak com.UBM.EventRecorder
```


## Windows Build
```bash
pyinstaller --onefile --noconsole .\EventRecorder\EventRecorder.py
```
