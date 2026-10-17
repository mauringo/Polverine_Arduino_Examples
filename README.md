# Polverine Arduino & PlatformIO: Bosch Sensortec BMV080, BME690 and BSEC3

Read **BMV080 particulate matter (PM1, PM2.5, PM10)** and **BME690 temperature, humidity, pressure, gas resistance and BSEC3 indoor air quality** on the [BlackIoT Polverine ESP32-S3 board](https://blackiot.swiss/products/polverine.html). This Arduino framework example prints one JSON object per line over USB Serial at **115200 baud**.

Maintained by **Mauro Riboni** ([@mauringo](https://github.com/mauringo)). **My personal hobby work, made privately for fun and learning.** My BME690 library started from Bosch Sensortec's BME68x Arduino library; my BSEC3 wrapper started from Bosch's BSEC2 Arduino library. This project is unofficial, independent of Bosch Sensortec and BlackIoT, and is not endorsed, certified or supported by them. Original notices and licenses are retained.

## Start with Arduino IDE

Follow the **[step-by-step Arduino guide](Arduino_project/README.md)**: clone this repository, install the published libraries in Library Manager, install your locally obtained Bosch SDKs, select the ESP32-S3 board, try a basic BME690 example, then upload **[Arduino_project.ino](Arduino_project/Arduino_project.ino)**.

**Library sources are installed separately.** You do not need to clone the library repositories or copy this workspace's development libraries into Arduino IDE.

| Arduino Library Manager search name | Tested version | Role / source |
| --- | --- | --- |
| `BME690-Arduino-lib-unofficial` | 0.0.1 | [Mauro's raw BME690 driver](https://github.com/mauringo/BME690-Arduino-lib-unofficial) |
| `Bsec3-ArduinoLibrary-Unofficial` | 0.0.1 | [Mauro's BSEC3 Arduino wrapper](https://github.com/mauringo/Bsec3-ArduinoLibrary-Unofficial) |
| `7Semi BMV080` | 1.0.0 | [7Semi's Bosch BMV080 wrapper](https://github.com/7semi-solutions/7Semi-BMV080-Particulate-Matter-Sensor) |
| `ArduinoJson` | 7.0.4 | [Serial JSON serialization](https://github.com/bblanchon/ArduinoJson) |

Both unofficial libraries are present in [Arduino's live library index](https://downloads.arduino.cc/libraries/library_index.json.gz) as version **0.0.1**. The public BME690 and BSEC3 `v0.0.1` tags match the commits recorded in `libraries.json`. The 7Semi Library Manager release is **1.0.0**; a previous local development copy called `Polverine_BMV080_Arduino` is not the package to install.

**Library Manager installs the wrappers, not Bosch's proprietary algorithm binaries.** Obtain **BSEC 3.3.0.1 IAQ** and **BMV080 SDK 11.2.0** from Bosch under their terms, then run the appropriate setup helper below or in the Arduino guide. This repository does not distribute SDK ZIPs, proprietary archives, generated Bosch profiles, firmware, or library sources.

## Start with PlatformIO / VS Code

**Recommended for maintaining this project and its libraries.** Follow the **[step-by-step PlatformIO usage guide](docs/PLATFORMIO.md)** for installation, Build/Upload/Monitor controls, source files, build environments and troubleshooting. It also explains [why PlatformIO fits this project](docs/PLATFORMIO.md#why-use-platformio-for-this-project) compared with Arduino IDE. The firmware still uses the Arduino framework; PlatformIO records the build configuration and manages dependencies around it.

Install PlatformIO IDE, Git and Python 3. Clone the project and open its root folder in VS Code:

```sh
git clone https://github.com/mauringo/Polverine_Arduino_Examples.git
cd Polverine_Arduino_Examples
python3 scripts/setup_platformio.py --bsec-zip /path/to/bsec_v3-3-0-1.zip --bmv-zip /path/to/bmv080-sdk-v11-2-0.zip
pio run -e polverine-full
pio run -e polverine-full -t upload
pio device monitor -b 115200
```

Replace `/path/to/` with your downloaded SDK locations; quote paths containing spaces. The helper works on macOS and Linux. It finds PlatformIO on PATH or in `~/.platformio/penv/bin/pio`. If your shell cannot find `pio`, use that full path for the remaining commands, or use VS Code's PlatformIO terminal.

The helper downloads the published Arduino releases first, then adds the SDK files locally. This order fixes **“BSEC3 archive missing for esp32s3”**. Re-run it after deleting `.pio/libdeps`, reinstalling packages, or changing library versions. No library bootstrap is needed for a normal build. PlatformIO uses the published BME690 tag required by BSEC3's metadata and Arduino's distributed ZIP packages for BSEC3 and 7Semi.

| Environment | Purpose |
| --- | --- |
| `polverine-full` (default) | Both sensors, Serial JSON |
| `polverine-bsec3` | BME690 + BSEC3 only; no BMV080 board heat table |
| `polverine-debug` | Both sensors, built-in ESP32-S3 USB JTAG, stops at `setup()` |
| `polverine-dev` | Opt-in build against editable nested library sources; see [WORKFLOW.md](WORKFLOW.md) |

Each environment has its own downloaded packages. Prepare another environment before its first build, for example:

```sh
python3 scripts/setup_platformio.py -e polverine-bsec3 -e polverine-debug --bsec-zip /path/to/bsec_v3-3-0-1.zip --bmv-zip /path/to/bmv080-sdk-v11-2-0.zip
pio run -e polverine-bsec3
```

VS Code's PlatformIO status bar / Project Tasks provides Build, Upload and Monitor. If missing, enable the PlatformIO IDE extension, open this folder containing `platformio.ini`, and run **Developer: Reload Window**. The included Terminal → Run Task entries also build/upload/monitor. See the [debug environment instructions](docs/PLATFORMIO.md#6-choose-a-build-environment) before starting a debugger. Close Serial Monitor before uploading or starting a different monitor. JTAG debugging has not been verified on hardware.

## BMV080, BME690 and BSEC3 configuration

The board configuration follows BlackIoT's [POLVERINE_FULL_MQTT_DEMO](https://github.com/BlackIoT/Polverine/tree/e75cb7adce5f9aa2b92c1f5565591db9b1cd24f1/POLVERINE_FULL_MQTT_DEMO). This application uses USB Serial; it does not start Wi-Fi or MQTT.

| Setting | Value |
| --- | --- |
| BME690 I2C | SDA GPIO14, SCL GPIO21, 100 kHz, address `0x76` |
| BMV080 SPI | SCK GPIO12, MISO GPIO13, MOSI GPIO11, CS GPIO10, 1 MHz |
| BSEC3 IAQ profile | `bme690_iaq_33v_3s_4d`: 3.3 V sensor supply, 3-second sample period, 4-day history |
| BMV080 operation | 60-second duty cycle, mode 0 |
| Board heat compensation | Wi-Fi client/profile 0 + 60 seconds → BlackIoT `tocp_cfg2` |

The 4-day setting is calibration history, not a startup delay. The sample period is 3 seconds; call `sensor.run()` frequently so the library can schedule measurements. IAQ accuracy evolves with conditioning and environmental variation. This example does not persist BSEC state; the library's `basic_config_state` example demonstrates persistence.

Pins and choices are in [polverine_settings.h](include/polverine_settings.h); the Arduino sketch has matching headers alongside its `.ino`. The original six BlackIoT coefficient tables and their MIT license are retained. A callback calculates the offset from each raw temperature before BSEC processes the sample, allowing BSEC to compensate **both temperature and humidity**. The board table is applied only when the matching BMV080 mode starts successfully. The sketch does not reproduce the reference's averaging, output gating, ESP-IDF power management or networking workload.

**Local calibration:** `TEMPERATURE_CALIBRATION_EXTRA_C` is currently **14.0 °C**, a provisional adjustment requested for the maintainer's board after an approximate 39 °C versus 25 °C room comparison. It is added to the original table without changing its coefficients. **For a new board, start with `0.0f` and calibrate against a reference thermometer after stabilization.** Positive values lower BSEC's reported temperature and also change humidity. This does not cool the board or establish accuracy across all temperatures or enclosures.

## Serial JSON output

Each application line is JSON, including initialization and error diagnostics. ESP32 ROM/boot messages can precede the application. Non-finite sensor values become `null`. Illustrative readings:

```json
{"type":"bme690","time_ms":3000,"raw_temperature_c":39.0,"temperature_c":25.0,"pressure_pa":101325,"raw_humidity_pct":30.0,"humidity_pct":50.0,"gas_resistance_ohm":120000,"iaq":25,"iaq_accuracy":0,"stabilized":0,"run_in":0}
{"type":"bmv080","time_ms":60000,"cycle_seconds":60,"pm1_ug_m3":1.2,"pm2_5_ug_m3":1.4,"pm10_ug_m3":1.6,"obstructed":false,"out_of_range":false}
```

`raw_` fields are physical sensor readings; `temperature_c` and `humidity_pct` are BSEC outputs. Pressure is in Pa, gas resistance in ohms, particulate mass concentration in µg/m³. CO2 equivalent is a BSEC estimate, not a direct CO2 measurement. Respect BMV080 obstruction/range flags. BMV080 output is less frequent because of duty cycling.

If BME690 output is missing, inspect `stage`, `ready`, `bsec_status`, `sensor_status`, `data_status` and `output_count` in status JSON. The sketch repeats a diagnostic after 10 seconds without BME output. This IAQ profile rejects breath-VOC equivalent output with BSEC `-35`, so the sketch requests only supported outputs. The [Arduino troubleshooting guide](Arduino_project/README.md#9-troubleshooting) covers common setup errors.

## Polverine 3D models and printable covers

Fetch just the upstream CAD files with a sparse clone:

```sh
python3 scripts/fetch_3d_models.py
```

The extracted board model is `hardware/Polverine/DOCS/Polverine.stp`. The helper records the upstream commit and keeps the license. It refuses to overwrite an existing folder. These downloaded files are ignored by the main repository. See **[3D model instructions](docs/3D_MODELS.md)** for manual sparse-clone commands and the community printable cover linked by BlackIoT. A STEP board model is a mechanical reference, not itself a printable enclosure.

## Maintain and publish independently

The main project and the two unofficial libraries remain three independent repositories. Default builds use releases; **[WORKFLOW.md](WORKFLOW.md)** explains how to opt into editable source builds under ignored `lib/`, release a library, then update the main project's dependency versions. No patches are applied. Publishing this project does not publish library sources.

```sh
./publish.sh                         # Menu: project or libraries, then which library
./publish.sh main --commit-only      # Commit the main project locally
./publish.sh main                    # Commit and push the main project
./publish.sh libraries --check       # Read-only status/audit
```

The publisher works with Bash 3.2+, Git and Python 3 on macOS/Linux. Library sources, SDK files, ZIPs and generated Arduino library copies stay out of the main repository. See [repository discovery metadata](docs/PROJECT_METADATA.md) for the suggested GitHub description and topics.

## Validation and credits

The registered release packages are tested with PlatformIO `espressif32@7.1.2` / Arduino ESP32 2.0.17 and Arduino ESP32 core 3.3.11. Compilation checks cover full JSON, BSEC-only and debug firmware, and the Arduino IDE sketch. Earlier hardware verification confirmed live BME690 and BMV080 output; a release-package rebuild does not establish long-term calibration accuracy.

Hardware, board definitions and compensation reference: [BlackIoT Polverine](https://github.com/BlackIoT/Polverine). Particulate wrapper: [7Semi BMV080](https://github.com/7semi-solutions/7Semi-BMV080-Particulate-Matter-Sensor). Bosch Sensortec owns the underlying BME68x/BSEC software and proprietary algorithms. Review the retained source licenses and Bosch SDK terms before reuse. This is personal experimental work provided as-is.
