# Polverine Arduino IDE tutorial: BMV080 + BME690 + BSEC3

This guide takes a fresh checkout through a basic BME690 check and the combined **Serial JSON** example on BlackIoT's Polverine ESP32-S3 board. No PlatformIO installation or library source clone is needed for Arduino IDE.

If you prefer VS Code or want to maintain the libraries alongside the example, follow the **[PlatformIO usage guide](../docs/PLATFORMIO.md)**. It covers the same Arduino framework application and explains the practical differences between the two workflows.

This is **Mauro Riboni's personal hobby work, made for fun and learning**, based on Bosch Sensortec's BME68x/BSEC2 Arduino libraries and BlackIoT's Polverine reference. It is unofficial and is not endorsed or supported by Bosch or BlackIoT. The BMV080 Arduino wrapper is maintained by 7Semi. Retained source licenses and separately obtained Bosch SDK terms apply.

## 1. Get the example repository

Install Arduino IDE 2, Git and Python 3, then open a terminal:

```sh
git clone https://github.com/mauringo/Polverine_Arduino_Examples.git
cd Polverine_Arduino_Examples
```

Keep this terminal at the repository root. On macOS/Linux, `python3 --version` should report Python 3. The commands below work in VS Code's terminal too. If you already cloned the project, use your existing checkout; do not overwrite local work with a second clone in the same folder.

The main files are:

| File | What to edit/read |
| --- | --- |
| `Arduino_project/Arduino_project.ino` | The full sensor setup, loop and JSON output |
| `Arduino_project/polverine_settings.h` | Pins, 60-second BMV080 cycle, temperature correction |
| `Arduino_project/polverine_compensation.h` | Callback that computes the BSEC heat offset |
| `Arduino_project/polverine_temperature_tables.h` | Original BlackIoT compensation coefficients |

Keep these files together in the `Arduino_project` folder. Arduino requires the main `.ino` filename to match its containing folder. Do not open `src/main.cpp` as an Arduino sketch.

## 2. Install the ESP32 board core

1. Open Arduino IDE → **Settings/Preferences**.
2. Add the official stable Espressif board index under **Additional Boards Manager URLs**:

   ```text
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```

3. Open **Tools → Board → Boards Manager**, search **esp32**, and install **esp32 by Espressif Systems**. This guide was compiled with **3.3.11**; select that version to reproduce the test.
4. Select **Tools → Board → esp32 → ESP32S3 Dev Module**.
5. Apply these options (labels can vary slightly with the core version):

| Tools option | Value |
| --- | --- |
| USB Mode | Hardware CDC and JTAG |
| USB CDC On Boot | Enabled |
| Flash Size | 8MB (64Mb) |
| Partition Scheme | 8M with spiffs (3MB APP/1.5MB SPIFFS) |
| PSRAM | Disabled |
| CPU Frequency | 240MHz |
| Port | The Polverine USB serial port |

Use a USB data cable. On macOS the port is often `/dev/cu.usbmodem…`; on Linux, often `/dev/ttyACM…`. The exact suffix varies. Select the port in Arduino IDE rather than copying an example port name. Espressif's [installation guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html) explains board core installation.

## 3. Install the published Arduino libraries

Open **Tools → Manage Libraries** (or the Library Manager sidebar). Search for each exact name below and select the tested version before clicking **Install**:

| Exact Library Manager name | Version |
| --- | --- |
| `BME690-Arduino-lib-unofficial` | **0.0.1** |
| `Bsec3-ArduinoLibrary-Unofficial` | **0.0.1** |
| `7Semi BMV080` | **1.0.0** |
| `ArduinoJson` | **7.0.4** |

Accept the BSEC3 dependency installation if prompted. `Wire` and `SPI` come with the ESP32 core; do not replace them with unrelated libraries. See [Arduino's Library Manager instructions](https://docs.arduino.cc/software/ide-v2/tutorials/ide-v2-installing-a-library/).

Install these through Library Manager. Do not copy the maintained `lib/` sources or old `Arduino_project/libraries/` copies into the sketchbook for this workflow. If migrating from the earlier instructions, move manually installed duplicates outside the sketchbook's `libraries` folder, then install the published versions. A folder rename alone does not remove an Arduino library: the IDE discovers its `library.properties`.

Find **Sketchbook location** in Settings/Preferences. The installed libraries are directly under its `libraries` subfolder, for example:

- macOS: `~/Documents/Arduino/libraries`
- Linux: `~/Arduino/libraries`

Your configured sketchbook can be different. Folder names may contain underscores instead of hyphens; the setup helper reads the Arduino library name from metadata, so you do not need to rename folders.

## 4. Install the Bosch SDK files locally

The raw BME690 driver needs no proprietary archive. **BSEC3 and BMV080 do.** Library Manager installs source wrappers without Bosch's algorithm binaries.

1. Obtain **BSEC 3.3.0.1**, including its IAQ ESP32-S3 binary and BME690 configurations, from [Bosch's BME690 software page](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme690/).
2. Obtain **BMV080 SDK 11.2.0** from [Bosch's BMV080 software page](https://www.bosch-sensortec.com/products/environmental-sensors/particulate-matter-sensor/bmv080/).
3. Accept Bosch's applicable terms and retain the original ZIP files locally. These scripts do not download SDKs or accept terms for you. Do not add them to Git.
4. Close Arduino IDE while the helper updates the installed library files. From the repository root, run the command for your system, replacing SDK paths and the sketchbook location if needed.

macOS:

```sh
python3 scripts/setup_arduino.py \
  --libraries-dir "$HOME/Documents/Arduino/libraries" \
  --bsec-zip "$HOME/Downloads/bsec_v3-3-0-1.zip" \
  --bmv-zip "$HOME/Downloads/bmv080-sdk-v11-2-0.zip"
```

Linux:

```sh
python3 scripts/setup_arduino.py \
  --libraries-dir "$HOME/Arduino/libraries" \
  --bsec-zip "$HOME/Downloads/bsec_v3-3-0-1.zip" \
  --bmv-zip "$HOME/Downloads/bmv080-sdk-v11-2-0.zip"
```

The helper verifies the four installed library versions. It delegates BSEC installation to the published library's own installer, which checks SDK headers and all eight BME690 profiles. It installs:

| Installed library | Local SDK additions |
| --- | --- |
| BSEC3 wrapper | `src/esp32s3/libalgobsec.a` and `src/config/bme690/*.h` |
| 7Semi BMV080 | `src/bmv080.h`, `src/bmv080_defs.h`, `src/esp32s3/lib_bmv080.a`, `src/esp32s3/lib_postProcessor.a` |

It also stores a local BMV080 SDK copy in the project's ignored `private/bmv080/` for PlatformIO. No library source is patched. Restart Arduino IDE after the helper reports **Arduino libraries ready**. Re-run this step after reinstalling or upgrading a wrapper because Library Manager may replace its local SDK additions. The helper intentionally checks the documented versions; a future release needs a compatibility check before changing these pins.

## 5. Try the basic BME690 and BSEC3 examples

This isolates I2C or SDK problems before running both sensors.

**Raw BME690 (no BSEC):**

1. Open **File → Examples → BME690-Arduino-lib-unofficial → generic_i2c**.
2. Save a personal copy if you want to keep your pin edits.
3. In the ESP32 pin section, change:

   ```cpp
   constexpr int I2C_SDA_PIN = 14;
   constexpr int I2C_SCL_PIN = 21;
   ```

4. Leave the address at `BME69X_I2C_ADDR_LOW` (`0x76`) for Polverine. The address is separate from the GPIO numbers.
5. Verify, Upload, then open Serial Monitor at **115200**. Expect a CSV header followed by temperature, pressure in Pa, humidity, gas resistance and a gas-valid flag. This simple library example prints CSV, while the combined project prints JSON. Raw temperature can be elevated by board and sensor heating.

The generic sketch explains `Wire.begin(sda, scl)` for ESP32. On other Arduino cores it uses `Wire.begin()` and the board's default SDA/SCL pins; ESP32 pin arguments must not be copied blindly to other architectures. The raw driver can be portable while the full Polverine/BSEC3 application remains an ESP32-S3 project.

**Basic BSEC3 IAQ:**

1. Close Serial Monitor, then open **File → Examples → Bsec3-ArduinoLibrary-Unofficial → basic**.
2. This example already uses Polverine GPIO14/21 and address `0x76`. Its profile defaults to the same 3.3 V / 3-second / 4-day BME690 configuration.
3. Verify, Upload, reopen Serial Monitor at **115200**. Expect `IAQ: …, accuracy: …` lines. Error messages include BSEC and BME690 status codes.
4. For custom wiring and a longer explanation, open the BSEC3 library's `generic_i2c` example instead and set GPIO14/21 as above. BSEC requires a matching Bosch binary and sufficient memory; support for `Wire` alone does not mean every Arduino board can run BSEC.

These minimal library examples do not run BMV080 or the Polverine board compensation table. They confirm the basic driver/algorithm path; use the full sketch below for the selected board heat compensation and JSON output.

## 6. Open, configure and upload the full JSON sketch

1. Choose **File → Open**, then select `Arduino_project/Arduino_project.ino` in this checkout.
2. Check that the adjacent settings/compensation headers appear in the sketch tabs.
3. Open `polverine_settings.h`. It already selects Polverine's pins, a **60-second BMV080 duty cycle** and BlackIoT's **Wi-Fi profile 0** compensation table (`tocp_cfg2`). Do not change these independently without reviewing the table selection.
4. Review **`TEMPERATURE_CALIBRATION_EXTRA_C`**. The committed **14.0f** is a provisional adjustment for the maintainer's board. For a different board/setup, start at **0.0f**, then refine against a reference thermometer after thermal stabilization. This extra offset is added to the unchanged upstream table and changes both BSEC temperature and humidity. It does not reduce physical board heating.
5. Keep these defines at the top of the `.ino` for the full board example:

   ```cpp
   #define USE_BMV080
   #define BSEC3_SUPPLY_MV 3300
   #define BSEC3_SAMPLE_PERIOD_S 3
   #define BSEC3_HISTORY_DAYS 4
   ```

   They select **`bme690_iaq_33v_3s_4d`**, the profile used by the board reference. Supply voltage is the sensor's supply, not USB's 5 V. The 4-day setting is calibration history, not a wait before readings. Removing `USE_BMV080` makes the application BSEC-only and disables the BMV-dependent board table; installed libraries/SDKs may still be discovered by the IDE.

6. Confirm the board options and USB port from step 2.
7. Click **Verify**. Once successful, close any other Serial Monitor using the port and click **Upload**.
8. If the board is not detected, hold **BOOT**, press/release **RESET**, release BOOT, select the resulting port, and upload. Reset afterward if necessary.

## 7. Read the Serial JSON data

Open Serial Monitor at **115200 baud**. Startup status lines report BMV080 initialization, BME690 `begin`, BSEC `set_config`, and output `subscription`. Normal BSEC/BME initialization reports status `0`. The application then emits one JSON object per line. ESP32 ROM/boot messages may appear before JSON starts.

Illustrative output:

```json
{"type":"status","device":"bme690","stage":"subscription","ready":true,"bsec_status":0,"sensor_status":0,"data_status":0,"output_count":0}
{"type":"bme690","time_ms":3000,"raw_temperature_c":39,"temperature_c":25,"pressure_pa":101325,"raw_humidity_pct":30,"humidity_pct":50,"gas_resistance_ohm":120000,"iaq":25,"iaq_accuracy":0}
{"type":"bmv080","time_ms":60000,"cycle_seconds":60,"pm1_ug_m3":1.2,"pm2_5_ug_m3":1.4,"pm10_ug_m3":1.6,"obstructed":false,"out_of_range":false}
```

| JSON field | Meaning |
| --- | --- |
| `type` | `status`, `bme690` or `bmv080` |
| `time_ms` | Reading timestamp in milliseconds since startup |
| `raw_temperature_c`, `raw_humidity_pct` | Original BME690 readings |
| `temperature_c`, `humidity_pct` | BSEC-compensated temperature and humidity |
| `heat_source_offset_c` | Total table + local calibration input to BSEC, when BMV080 is active |
| `temperature_calibration_extra_c` | Additional local correction selected in the settings header |
| `pressure_pa`, `gas_resistance_ohm` | Pressure in Pa and raw gas resistance in ohms |
| `iaq`, `iaq_accuracy` | BSEC IAQ estimate and its 0–3 accuracy indicator |
| `static_iaq`, `co2_equivalent_ppm` | Additional BSEC estimates; CO2 equivalent is not a direct CO2 measurement |
| `stabilized`, `run_in` | Algorithm status indicators |
| `pm1_ug_m3`, `pm2_5_ug_m3`, `pm10_ug_m3` | BMV080 mass concentrations in µg/m³ |
| `obstructed`, `out_of_range` | BMV080 flags to consider when interpreting readings |

BME690 normally produces processed readings around the 3-second sample schedule. BMV080 readings are less frequent with its 60-second duty cycle; allow at least a complete cycle before diagnosing missing particulate output. IAQ conditioning and temperature stabilization are separate from receiving the first packet. There is no universal fixed settling time for every enclosure/workload. The sketch does not persist BSEC state between resets; use the library's `basic_config_state` example to add that behavior.

## 8. Get the Polverine 3D reference model

From the repository root:

```sh
python3 scripts/fetch_3d_models.py
```

This sparse-clones only selected CAD documentation from [BlackIoT/Polverine](https://github.com/BlackIoT/Polverine/tree/main/DOCS) and extracts `hardware/Polverine/DOCS/Polverine.stp`. It keeps the source license and writes the exact upstream commit to `SOURCE.txt`. The destination is ignored by Git, so CAD ZIPs and models are not added to this project when publishing.

Read **[3D_MODELS.md](../docs/3D_MODELS.md)** for manual commands and BlackIoT's community printable-cover link. The STEP file describes the board assembly; it is not a ready-to-print enclosure. A new enclosure can change heating and requires a new temperature comparison.

## 9. Troubleshooting

| Symptom | Check / fix |
| --- | --- |
| Library not found in Library Manager | Search the exact names in step 3; refresh the index/restart IDE. Do not install Bosch BSEC2 or BME68x as substitutes for these BME690 wrappers. |
| `bsec3.h`, `bme69xLibrary.h`, `7Semi_BMV080.h`, or `ArduinoJson.h` missing | Install the matching Library Manager package; check the configured sketchbook location. |
| `bmv080.h` missing, or `cannot find -l_bmv080` / `-l_postProcessor` | Run step 4 against the actual installed 7Semi library, then restart IDE. |
| `libalgobsec.a` / BME690 profile missing | Run step 4; Library Manager installs the wrapper without SDK data. For PlatformIO use `scripts/setup_platformio.py`, not the Arduino sketchbook helper. |
| Helper cannot find a library, or finds duplicates | Use the Preferences sketchbook location plus `/libraries`; move old copies outside that folder. The helper checks `library.properties`, not folder names. |
| SDK/header mismatch | Use BSEC **3.3.0.1 IAQ** with wrapper **0.0.1**; do not mix SDK releases. |
| Multiple libraries found | Keep one installed version of each dependency in the sketchbook. Check verbose compiler output for selected paths. |
| No Serial output | Enable USB CDC On Boot, choose Hardware CDC and JTAG, select the correct port, use 115200, press RESET. |
| Upload/monitor says port busy | Close Arduino/VS Code/PlatformIO monitors using the same port, then retry. |
| BME `begin` fails | Confirm Polverine GPIO14/21, I2C address `0x76`, board selection and power; try the raw generic example. |
| No BME JSON | Read `stage`, `bsec_status`, `sensor_status`, `data_status`, `ready`, `output_count`; periodic diagnostics appear after 10 seconds without data. |
| BSEC `-35` | This profile rejects unsupported outputs such as breath-VOC equivalent. Keep the output subscription supplied by this project. |
| No BMV JSON | Check its startup status, wait a full 60-second cycle, and verify SPI pins/SDK. Respect obstruction/range flags. |
| High temperature / changed humidity | Inspect raw versus compensated values, table selection and the provisional extra 14 °C setting; calibrate for your own board, workload and enclosure. |

## Optional: reproduce with Arduino CLI

After installing `esp32:esp32@3.3.11`, the four libraries and the SDKs as above, run from the repository root:

```sh
arduino-cli compile \
  --fqbn 'esp32:esp32:esp32s3:FlashSize=8M,PartitionScheme=default_8MB,CDCOnBoot=cdc,USBMode=hwcdc,PSRAM=disabled' \
  Arduino_project
```

For an isolated library collection, add `--libraries /path/to/libraries`. The published packages were compiled successfully with this board configuration, including the BSEC3 and BMV080 ESP32-S3 archives. This verifies compilation/linking; it does not establish long-term measurement accuracy.

Library development and separate publishing are documented in [WORKFLOW.md](../WORKFLOW.md). Generated development copies from `prepare_libraries.py` are an optional maintainer workflow, not part of the Library Manager installation above.
