# Use Polverine with PlatformIO and VS Code

Use this guide to build, upload and read the Polverine BMV080/BME690 Serial JSON example, or to develop the two unofficial Arduino libraries in the same workspace. The commands work on macOS and Linux.

This is Mauro Riboni's personal hobby work, made for fun and learning. The BME690 and BSEC3 wrappers are unofficial adaptations of Bosch Sensortec's BME68x and BSEC2 Arduino libraries. Original attribution and licenses are retained. Bosch SDK binaries must be obtained separately under Bosch's terms.

## Why use PlatformIO for this project?

**PlatformIO is the recommended workflow for maintaining this project and its libraries.** It records build settings in the repository and lets you select a released or development build explicitly. Arduino IDE is a convenient choice for opening a basic `.ino` example and trying a sensor.

The firmware still uses the **Arduino framework**: `setup()`, `loop()`, `Wire`, `SPI` and Arduino libraries. PlatformIO manages the build tools, dependencies, upload and debugging around that code. Choosing PlatformIO does not change the sensor algorithms or inherently improve measurement accuracy or firmware speed.

| Need in this project | How PlatformIO helps | Typical Arduino IDE workflow |
| --- | --- | --- |
| Repeat the build on another computer | Board, platform version, dependency references and compiler flags are recorded in `platformio.ini`. | Install the core/libraries and select the documented Tools options. |
| Keep dependencies separate between projects | Downloads are stored under this project's `.pio/libdeps/`. | Library Manager uses libraries in the configured sketchbook. |
| Switch sensor/build configurations | Select a named environment for both sensors, BSEC-only, debugging or library development. | Change sketch defines/settings or keep separate sketches. |
| Edit the two libraries alongside the example | `polverine-dev` builds the nested library sources directly. | Manage development library copies in the sketchbook and avoid duplicates. |
| Automate validation | The same build commands can run in VS Code, a shell or CI. | Arduino CLI can also automate builds, with its configuration/dependency setup managed separately. |

The practical advantage here is a controlled, repeatable maintenance workflow. Arduino IDE also has debugging support for compatible setups, so debugging alone is not the reason to choose PlatformIO. See the official [PlatformIO VS Code guide](https://docs.platformio.org/en/latest/integration/ide/vscode.html), [project configuration reference](https://docs.platformio.org/en/latest/projectconf/index.html) and [dependency management guide](https://docs.platformio.org/en/latest/librarymanager/dependencies.html).

## 1. Install and open the project

1. Install **Visual Studio Code**, **Git** and **Python 3**.
2. In VS Code's Extensions panel, search for **PlatformIO IDE** and install the extension published by PlatformIO. Its command-line tools are included; a separate PlatformIO Core installation is not required.
3. Clone this repository in a terminal:

   ```sh
   git clone https://github.com/mauringo/Polverine_Arduino_Examples.git
   cd Polverine_Arduino_Examples
   ```

4. In VS Code, choose **File → Open Folder** and open that checkout's root folder, containing `platformio.ini`. For PlatformIO, open the project root rather than just `src/` or `Arduino_project/`.
5. Allow the extension to finish initializing. Open the PlatformIO icon in the Activity Bar to find **Project Tasks**. To open its terminal, use **Quick Access → Miscellaneous → PlatformIO Core CLI**.

If you already have a checkout, open it directly. Keep local edits instead of cloning over them. Run the commands below from the project root.

## 2. Prepare dependencies and Bosch SDKs

For a normal user build, PlatformIO downloads the published Arduino library releases automatically. You do not need to install them through Arduino IDE's Library Manager or clone their repositories into `lib/`.

Obtain **BSEC 3.3.0.1 IAQ** and **BMV080 SDK 11.2.0** from Bosch and accept the applicable terms. Download links and SDK details are in [Arduino setup, step 4](../Arduino_project/README.md#4-install-the-bosch-sdk-files-locally); the PlatformIO installation command is different:

```sh
python3 scripts/setup_platformio.py \
  --bsec-zip "/path/to/bsec_v3-3-0-1.zip" \
  --bmv-zip "/path/to/bmv080-sdk-v11-2-0.zip"
```

Replace the paths with your local SDK ZIP files. Quoting paths also handles spaces. The helper first downloads the published dependencies, then installs the local Bosch binary and BME690 profiles into the downloaded BSEC3 package and prepares BMV080 SDK files under ignored `private/bmv080/`.

The source wrappers do not include Bosch's proprietary algorithms. Skipping this step causes errors such as **“BSEC3 archive missing for esp32s3”**. Repeat preparation after removing `.pio/libdeps/`, reinstalling dependencies or changing library versions. A normal Clean build removes build products; it does not require reinstalling the SDKs.

If `pio` is not found in your shell, use the PlatformIO Core CLI terminal. On macOS/Linux you can also use `~/.platformio/penv/bin/pio` in place of `pio`; the setup helper checks that location automatically.

## 3. Build, upload and monitor

Connect Polverine using a USB data cable. In the PlatformIO sidebar, expand **Project Tasks → polverine-full → General**.

| Action | VS Code control | Equivalent terminal command |
| --- | --- | --- |
| Build: compile and link, without writing the board | **Build** | `pio run -e polverine-full` |
| Upload: build if needed and write firmware to the board | **Upload** | `pio run -e polverine-full -t upload` |
| Monitor: read Serial JSON at 115200 baud | **Monitor** | `pio device monitor -b 115200` |
| Clean: remove this environment's compiled build products | **Clean** | `pio run -e polverine-full -t clean` |

The status bar offers shortcuts for the selected environment. Choose `polverine-full` for the normal example. The explicit sidebar tasks or `-e` terminal option make the selected environment clear.

This repository also provides **Terminal → Run Task → Build Polverine**, **Upload Polverine** and **Serial JSON**. The first two explicitly use `polverine-full`, independently of the status-bar environment selection.

Build first to check for errors, upload after it succeeds, then start Monitor. Close other Arduino/VS Code Serial Monitors using the same port before uploading or opening another monitor. Exit the terminal monitor with **Ctrl+C**.

If automatic port selection picks the wrong device, list connected ports and specify one:

```sh
pio device list
pio run -e polverine-full -t upload --upload-port /dev/cu.usbmodemXXXX
pio device monitor --port /dev/cu.usbmodemXXXX -b 115200
```

Replace the example port with the actual result. macOS ports commonly start with `/dev/cu.usbmodem`; Linux ports commonly start with `/dev/ttyACM`. If the board needs download mode, hold BOOT, press/release RESET, release BOOT, then select the resulting port and retry Upload.

## 4. Read the output

The application emits one JSON object per line, including startup/error status. ESP32 boot messages can appear before application JSON begins.

- `type: "status"` reports initialization or diagnostics. BME690 status includes `stage`, `ready`, `bsec_status`, `sensor_status` and `output_count`.
- `type: "bme690"` contains physical readings and BSEC outputs such as compensated temperature, humidity and IAQ. Its selected sample period is 3 seconds.
- `type: "bmv080"` contains PM1, PM2.5 and PM10 mass concentrations plus obstruction/range flags. Its 60-second duty cycle makes output less frequent.

For units, sample JSON and compensation details, see [Serial JSON output](../README.md#serial-json-output). Review `TEMPERATURE_CALIBRATION_EXTRA_C` before interpreting temperature: the committed 14 °C adjustment is provisional for the maintainer's board; another setup should start at zero and be checked against a reference thermometer.

## 5. Know which files to edit

| File/folder | Purpose |
| --- | --- |
| [`src/main.cpp`](../src/main.cpp) | PlatformIO application's `setup()`, `loop()`, sensor handling and JSON output |
| [`include/polverine_settings.h`](../include/polverine_settings.h) | Pins, BMV080 cycle and local temperature correction |
| [`include/polverine_compensation.h`](../include/polverine_compensation.h) | Board heat-offset callback |
| [`include/polverine_temperature_tables.h`](../include/polverine_temperature_tables.h) | Original BlackIoT compensation coefficients |
| [`platformio.ini`](../platformio.ini) | Board, Arduino framework, dependencies, flags and environments |
| `lib/` | Optional editable library checkouts for `polverine-dev`; ignored by the main repository |
| `.pio/` | Generated build files and downloaded dependencies; ignored by Git |
| `private/` | Local SDK files; ignored by Git |
| [`Arduino_project/`](../Arduino_project/README.md) | Companion `.ino` and headers for Arduino IDE |

For PlatformIO application changes, edit `src/main.cpp` and `include/`. Keep the companion `.ino` and its headers aligned when changing shared behavior. For lasting library changes, use the maintained sources under `lib/`; edits inside `.pio/libdeps/` can disappear when packages are reinstalled.

## 6. Choose a build environment

An environment is a named group of build settings in `platformio.ini`. It selects dependencies/flags for the same application source.

| Environment | Purpose | Library source |
| --- | --- | --- |
| `polverine-full` (default) | Both sensors, Serial JSON | Published releases |
| `polverine-bsec3` | BME690/BSEC3 only; no BMV080-dependent board compensation table | Published releases |
| `polverine-debug` | Both sensors, debug build, ESP32-S3 built-in USB JTAG | Published releases |
| `polverine-dev` | Maintain the nested libraries directly | Editable sources under `lib/` |

Each release environment has its own dependency directory. Before using another one for the first time, prepare it explicitly. For BSEC-only operation, the BMV080 SDK argument can be omitted:

```sh
python3 scripts/setup_platformio.py -e polverine-bsec3 \
  --bsec-zip "/path/to/bsec_v3-3-0-1.zip"
pio run -e polverine-bsec3
pio run -e polverine-bsec3 -t upload
```

For the debug environment:

```sh
python3 scripts/setup_platformio.py -e polverine-debug \
  --bsec-zip "/path/to/bsec_v3-3-0-1.zip" \
  --bmv-zip "/path/to/bmv080-sdk-v11-2-0.zip"
pio run -e polverine-debug
```

Building a debug environment compiles firmware; it does not start a debugger. Breakpoint debugging additionally requires a working JTAG connection and matching debugger configuration. Select `polverine-debug` for debugging and follow [PlatformIO's debugger instructions](https://docs.platformio.org/en/latest/integration/ide/vscode.html#debugging). If VS Code has generated `launch.json`, ensure its executable is `.pio/build/polverine-debug/firmware.elf` for this environment rather than a release ELF or another checkout's absolute path. The configured debug build stops at `setup()` when a session starts; hardware JTAG operation has not been verified for this project.

## 7. Develop and test the libraries here

Default release builds intentionally use published packages. To test an unpublished library change, prepare the independent source checkouts and build the development environment:

```sh
python3 scripts/repos.py bootstrap
python3 scripts/install_bsec.py "/path/to/bsec_v3-3-0-1.zip" \
  --library-dir lib/Bsec3-ArduinoLibrary-Unofficial
python3 scripts/install_bmv080.py "/path/to/bmv080-sdk-v11-2-0.zip"
pio run -e polverine-dev
```

Edit the actual `.h`, `.cpp` and `.c` files under the nested library folders. Build again with `polverine-dev`, and use `pio run -e polverine-dev -t upload` when testing that development firmware on the board. No source patches or generated library copies are involved in this PlatformIO workflow.

**Use `polverine-dev` to test your library edits; use `polverine-full` to test the published releases.** This distinction lets you check both the next change and the version users install. See [WORKFLOW.md](../WORKFLOW.md) for publishing the two libraries separately and updating the main project's release references.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Build/Upload buttons are missing | Enable PlatformIO IDE, open the root folder containing `platformio.ini`, wait for initialization, then run **Developer: Reload Window**. Use Project Tasks or Terminal → Run Task as an alternative. |
| `pio: command not found` | Open PlatformIO Core CLI or use `~/.platformio/penv/bin/pio`. |
| BSEC3 archive/profile missing | Run `scripts/setup_platformio.py` for the selected release environment. SDK files installed in Arduino's sketchbook are separate from PlatformIO's packages. |
| `bmv080.h` or BMV080 archives missing | Prepare the BMV080 SDK using the helper and the correct SDK ZIP. |
| My library edits do not affect the firmware | Prepare/build/upload `polverine-dev`; release environments ignore the development `lib/` folder. |
| Upload/monitor reports a busy port | Close other Serial Monitors and retry. |
| Several USB ports are present | Run `pio device list`, then use `--upload-port` or Monitor's `--port`. |
| No Serial JSON | Check the port, 115200 baud and USB data cable, then press RESET. Inspect startup status lines. |
| BME690/BMV080 values are missing | Read device startup/status JSON; allow a complete BMV080 duty cycle. See [sensor troubleshooting](../Arduino_project/README.md#9-troubleshooting). |

The project keeps SDK ZIPs, proprietary archives, generated firmware and development library sources out of the main Git repository. Build and upload are local operations; publishing remains a separate action through `publish.sh`.
