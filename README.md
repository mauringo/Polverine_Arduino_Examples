# Polverine Arduino JSON example

Maintained by **Mauro Riboni** ([@mauringo](https://github.com/mauringo)).

**Personal hobby work, made privately for fun and learning.** The unofficial BME690 library started from Bosch's official BME68x Arduino library; the unofficial BSEC3 wrapper started from Bosch's official BSEC2 Arduino library. This work is independent of Bosch Sensortec and is not endorsed, certified, or supported by Bosch. Original Bosch copyright notices and licenses are retained. These experimental projects carry no promise of reliability, continued maintenance, or support.

For **Arduino IDE**, open `Arduino_project/Arduino_project.ino` and follow [its setup instructions](Arduino_project/README.md).

One `src/main.cpp` reads BME690 through BSEC3 and BMV080 through the 7Semi wrapper, and prints one JSON object per line at 115200 baud. The application emits JSON for startup/errors too. ESP32 bootloader messages may appear before the application starts. ArduinoJson serializes non-finite sensor values as `null`.

```sh
python3 scripts/repos.py bootstrap
python3 scripts/install_bsec.py bsec_v3-3-0-1.zip
python3 scripts/install_bmv080.py bmv080-sdk-v11-2-0.zip
pio run
pio run -t upload
pio device monitor -b 115200
```

On this Mac, use `~/.platformio/penv/bin/pio` if `pio` is not on PATH. The default `polverine-full` environment includes both sensors. `pio run -e polverine-bsec3` builds without BMV080. Raw BME690 examples are provided in its library's `examples/` folder.

Example output (illustrative):

```json
{"type":"bme690","time_ms":3000,"raw_temperature_c":32.7,"temperature_c":23.5,"pressure_pa":101325,"raw_humidity_pct":30,"humidity_pct":45,"gas_resistance_ohm":120000,"iaq":25,"iaq_accuracy":0,"stabilized":0,"run_in":0}
{"type":"bmv080","time_ms":3200,"pm1_ug_m3":1.2,"pm2_5_ug_m3":1.4,"pm10_ug_m3":1.6,"obstructed":false,"out_of_range":false}
```

`temperature_c` and `humidity_pct` are BSEC-compensated values. `raw_temperature_c` and `raw_humidity_pct` are the original sensor readings. IAQ needs conditioning/calibration. Respect BMV080 obstruction and range flags. The example does not persist BSEC state; the BSEC library's `basic_config_state` example shows how.

## How the demo is configured

The reference is BlackIoT's **POLVERINE_DEMO**, pinned to commit `e75cb7adce5f9aa2b92c1f5565591db9b1cd24f1`.

| Setting | This example |
| --- | --- |
| BSEC profile | `bme690_iaq_33v_3s_4d`: 3.3 V, LP/3 seconds, 4-day history |
| BMV080 mode | Duty cycling, 30 seconds, mode 0 |
| Board compensation | Client/profile 1 + 30 seconds → BlackIoT table `tocp_cfg3` |
| Main temperature/humidity fields | Compensated by BSEC using the board table |
| Raw fields | Explicitly named `raw_temperature_c` and `raw_humidity_pct` |

Read `src/main.cpp` for the setup and JSON output. Pins and board choices are named in `include/polverine_settings.h`. The compensation calculation is in `include/polverine_compensation.h`; all six original coefficient tables are preserved in `include/polverine_temperature_tables.h`, with BlackIoT's MIT license alongside them.

For every BME690 sample, the selected polynomial computes a heat-source offset from the **current raw temperature**. The library sends that offset to BSEC before processing the sample. BSEC then returns compensated temperature and humidity. It is not a manual subtraction after the reading.

**Reference inconsistency corrected:** `POLVERINE_DEMO/include/polverine_cfg.h` declares a 30-second BMV080 cycle, while `src/bmv080_main.c` hardcodes 60 seconds. This example uses the declared **30 seconds consistently** for both the sensor and table selection. It preserves the reference's first-match boundary behavior and zero offset outside table ranges. The BSEC-only environment does not apply the BMV080-dependent board table; neither does a run where BMV080 initialization fails.

The example emits readings as they arrive. It does not reproduce the reference's output gating, moving averages, ESP-IDF low-power setup, or Wi-Fi/BLE workloads. Their thermal effects can differ; the copied compensation tables still need validation on your running hardware. CO2/VOC fields are BSEC equivalents, not direct gas concentration measurements.

## Maintain and release

Edit library source directly under `lib/`, test it with this project, then release each library separately. See [WORKFLOW.md](WORKFLOW.md) for the short workflow and Arduino Library Manager registration steps.

## Publish on macOS or Linux

```sh
./publish.sh            # Choose main project or libraries, then which library
./publish.sh libraries  # Publish both libraries
./publish.sh main       # Commit and publish the PlatformIO + Arduino project
./publish.sh main --commit-only  # Commit locally without pushing
```

Requires Bash (macOS’s built-in Bash 3.2 is supported), Git, and Python 3 on PATH. Run from a normal shell or VS Code’s terminal; no macOS-specific paths or GitHub CLI are required.

The script shows repository status and destinations, audits forbidden files, stages all changes in the selected repository and commits them before asking to push. Enter a commit message or press Enter for the suggested message. If that repository is already clean, it explicitly says the existing commit is ready to push. Main-project changes and library changes are committed separately. It inherits Git authentication from your terminal; VS Code being signed in must also provide Git access to your repositories. If needed, complete VS Code's GitHub authentication prompt. After each successful library push, the project pins that published commit. The script also offers to publish an Arduino version tag, independently for each library. The main project publishes to `https://github.com/mauringo/Polverine_Arduino_Examples.git`.

For a read-only check: `./publish.sh libraries --check`. A failed push leaves local commits intact and can be retried.

## Three independent repositories

| Repository folder | GitHub destination |
| --- | --- |
| Project root (`.`) | [Polverine_Arduino_Examples](https://github.com/mauringo/Polverine_Arduino_Examples) |
| `lib/BME690_unofficial` | [BME690-Arduino-lib-unofficial](https://github.com/mauringo/BME690-Arduino-lib-unofficial) |
| `lib/BSEC3_unofficial` | [Bsec3-ArduinoLibrary-Unofficial](https://github.com/mauringo/Bsec3-ArduinoLibrary-Unofficial) |

The root project and your two libraries each have their own Git history and origin. The 7Semi BMV080 source is also editable locally as a third-party dependency. Publishing the root project does not include any of these library sources. Run `./publish.sh` to select the destination.

## Libraries in this workspace

| Folder | Ownership |
| --- | --- |
| `lib/BME690_unofficial` | Separate Git clone of your BME690 library; Arduino metadata and sources at the repository root |
| `lib/BSEC3_unofficial` | Separate Git clone of your BSEC3 library |
| `lib/7Semi_BMV080` | Local 7Semi dependency downloaded by bootstrap; not published with this project |

All three libraries live locally under `lib/` as editable source. Edit their `.h`, `.cpp`, and `.c` files directly; PlatformIO builds those sources in place. The entire `lib/` folder and generated Arduino library copies are excluded from the root project. The project contains only application code, board compensation tables, setup scripts, and dependency references. `libraries.json` records dependency URLs and starting commits. Bootstrap only downloads missing libraries and never overwrites existing source edits. It does not apply transformations or modify your source. **Publish both updated libraries before publishing the main project**, so its pinned commits are available to fresh clones. The GitHub repository names remain unchanged; install/clone them under the folder names above for Arduino IDE use.

```sh
python3 scripts/repos.py status
python3 scripts/repos.py diff bsec3
python3 scripts/repos.py commit bsec3 -m "Describe your change"
python3 scripts/repos.py push bsec3
# Other targets: bme690 or example
python3 scripts/repos.py audit all
```

Commit and push require an explicit target. Push checks the index and reachable Git history for ZIPs and binary files, then pushes only the current branch. The root project origin is `https://github.com/mauringo/Polverine_Arduino_Examples.git`. After future library changes, publish those changes first; the publisher automatically updates `libraries.json` only after successful library pushes.

## Bosch SDK files

Obtain SDKs directly from Bosch and accept their terms. The supplied ZIPs are retained locally. The BSEC installer selects the **BSEC 3.3.0.1 IAQ ESP32-S3** archive and installs all eight matching BME690 profiles locally. Legacy BME680/BME688 configurations are removed. The example explicitly selects `bme690_iaq_33v_3s_4d` (3.3 V, 3 seconds, 4-day calibration history) in `platformio.ini`, matching [BlackIoT’s reference firmware configuration](https://github.com/BlackIoT/Polverine/blob/main/deps/bsec3_lib.ini); see the BSEC3 library README for 1.8 V, 300-second, and 28-day options. The profile choice is fixed explicitly for this board rather than relying on library defaults. BMV080 uses SDK **11.2.0** headers and ESP32-S3 archives under ignored `private/bmv080/`. ZIPs, proprietary archives, and generated firmware are never committed.

BME690 uses SDA 14, SCL 21, 100 kHz, address `0x76`. BMV080 uses SCK 12, MISO 13, MOSI 11, CS 10, 1 MHz. These match the [BlackIoT reference firmware](https://github.com/BlackIoT/Polverine). The board definition and its license are in `boards/`.

Validated by compilation with PlatformIO `espressif32@7.1.2` and Arduino ESP32 2.0.17: full JSON firmware, BSEC-only JSON firmware, BME690 custom-pin I2C example, BSEC IAQ basic example, and BSEC state persistence example. Physical sensor communication and long-term calibration still need validation on a connected board. The Arduino IDE sketch also compiles with Espressif ESP32 core 3.3.11; other MCU architectures were not tested.

Sources: [BME690](https://github.com/mauringo/BME690-Arduino-lib-unofficial), [BSEC3](https://github.com/mauringo/Bsec3-ArduinoLibrary-Unofficial), [7Semi BMV080](https://github.com/7semi-solutions/7Semi-BMV080-Particulate-Matter-Sensor).

## VS Code controls

Open this project folder in VS Code and enable the installed PlatformIO IDE extension. Run **Developer: Reload Window** from the Command Palette if its toolbar has not appeared. The status bar provides labeled Build, Upload, Serial, and Debug controls. Upload uses `polverine-full`; Debug uses `polverine-debug` and stops at `setup()` through the ESP32-S3 built-in USB JTAG interface. The same commands are available under Terminal → Run Task. Debug is also available through Run and Debug → Polverine USB JTAG → F5. Debugging has been compiled but not tested on attached hardware.

## Generic library examples

For your own wiring/board, start with each library's `examples/generic_i2c/generic_i2c.ino` rather than the Polverine-specific application. Both sketches explain board-default SDA/SCL pins, custom ESP32 GPIOs, the difference between pin numbers and I2C addresses, and measurement setup. Their READMEs distinguish raw-driver portability from BSEC's required platform-specific algorithm archive and RAM.

Prepared releases: BME690 **1.4.1**, BSEC3 **1.13.0**. The generic raw sketch compiles on Arduino Uno and ESP32-S3; the generic BSEC sketch compiles on ESP32, S2, S3 and C3. Physical measurements remain unvalidated. Publish the libraries through `./publish.sh libraries`, then the main project, to update its pinned revisions.
