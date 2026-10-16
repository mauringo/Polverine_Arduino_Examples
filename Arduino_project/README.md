# Polverine in Arduino IDE

Open **Arduino_project.ino**. It runs the same sensors, profile, compensation tables, and Serial JSON output as the PlatformIO example.

## 1. Prepare the libraries

Prepared locally under `Arduino_project/libraries/` (excluded from the project repository):

- `BME690_unofficial`
- `BSEC3_unofficial`
- `7Semi_BMV080`

Copy these **three folders** into your Arduino sketchbook's `libraries` folder. Find your sketchbook location in Arduino IDE → Settings/Preferences. Restart the IDE after copying. The folders must sit directly under `libraries`, without an extra nesting level.

Install **ArduinoJson 7.0.4** using Arduino IDE's Library Manager.

The generated library folders contain your locally installed Bosch SDK files and are ignored by Git. Do not publish or redistribute them. For a fresh checkout, run these commands from the project root:

```sh
python3 scripts/repos.py bootstrap
python3 scripts/install_bsec.py bsec_v3-3-0-1.zip
python3 scripts/install_bmv080.py bmv080-sdk-v11-2-0.zip
python3 Arduino_project/prepare_libraries.py
```

The preparation script never overwrites an existing generated library folder. Move/remove `Arduino_project/libraries` before regenerating it after library changes.

## 2. Select the board

Install **esp32 by Espressif Systems** from Boards Manager, then choose:

| Arduino IDE option | Value |
| --- | --- |
| Board | ESP32S3 Dev Module |
| USB Mode | Hardware CDC and JTAG |
| USB CDC On Boot | Enabled |
| Flash Size | 8MB (64Mb) |
| Partition Scheme | 8M with spiffs (3MB APP/1.5MB SPIFFS) |
| PSRAM | Disabled |
| Port | Your connected Polverine USB port |

## 3. Upload and read JSON

Click **Verify**, then **Upload**. Open Serial Monitor at **115200 baud**.

If the upload port does not appear: hold BOOT, press/release RESET, release BOOT, then select the port and upload. Reset the board after uploading if needed.

## What the sketch does

1. Starts BMV080 through the 7Semi library with a **30-second duty cycle**.
2. Applies BME690's **3.3 V / 3-second / 4-day** BSEC IAQ profile.
3. Uses BlackIoT's **client/profile 1 + 30-second** temperature compensation table before BSEC processes each reading.
4. Prints one JSON object per line. `temperature_c` and `humidity_pct` are compensated; fields starting with `raw_` are the original sensor readings.

The BMV080 cycle and compensation selector deliberately both use 30 seconds, correcting the reference demo's declared-30/hardcoded-60 discrepancy. Hardware calibration still needs validation.

The four defines at the top of the `.ino` replace PlatformIO build flags. Board pins and settings are in `polverine_settings.h`. The compensation calculation and original BlackIoT tables are in the adjacent headers, with their MIT license.

This is Mauro Riboni's personal hobby work, made for fun and learning, based on Bosch's BME68x/BSEC2 libraries and BlackIoT's Polverine demo. It is unofficial and is not endorsed or supported by Bosch. Original licenses are retained.

Verified with the Arduino IDE bundled CLI and Espressif ESP32 core **3.3.11**, using the board options above. The `.ino` compiles and links both local Bosch libraries successfully. No firmware was uploaded.

BME output fix: the sketch uses the verified BME690 IAQ output list, without the breath-VOC request rejected by this profile. Startup and periodic JSON diagnostics show the stage, actual BSEC/BME status codes, and callback count. The matching PlatformIO firmware has been verified on the connected board to produce BME and BMV readings.
