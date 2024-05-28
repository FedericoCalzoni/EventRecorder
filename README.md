# EventRecorder
EventRecorder is a simple application to record timed events. It is useful to keep track of the time spent on different tasks, and to generate reports. 

# How to Install
## Linux
You can easily install EventRecorder via Flathub:
<p>
<a href="https://flathub.org/apps/io.github.FedericoCalzoni.EventRecorder">
  <img  alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png" width="150">
</a>
</p>

## Windows
1. Download the latest version of EventRecorder from the [releases page](https://github.com/FedericoCalzoni/EventRecorder/releases).
2. Double-click the downloaded `EventRecorder.exe` file to start the application.

**Note:** The Windows version of EventRecorder is not signed, so you may see a warning when you try to run the application. If this happens, you can proceed by selecting "More info" and then clicking "Run anyway".


# Build
## Linux Flatpak
1) Install Flatpak and Flatpak-builder from your distribution's repository.
2) Add the Flathub remote:
``` bash
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

3) Install required runtimes:
```bash
sudo flatpak install flathub org.kde.Platform//6.7
sudo flatpak install flathub org.kde.Sdk//6.7
sudo flatpak install flathub com.riverbankcomputing.PyQt.BaseApp//6.7
```

4) Build the application:
``` bash
flatpak-builder --repo=repo --force-clean build-dir io.github.FedericoCalzoni.EventRecorder.json
flatpak build-export repo build-dir
flatpak build-bundle repo EventRecorder.flatpak io.github.FedericoCalzoni.EventRecorder
```


## Windows
1) Install Pyhton 3.x
2) Install dependencies:
``` bash
pip install pyinstaller
pip install PyQt6
```
3) Build the application:
```bash
pyinstaller --onefile --noconsole .\EventRecorder\EventRecorder.py
```

