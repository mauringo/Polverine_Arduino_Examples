# Maintain here, release separately

This project is the development and test workspace. Edit the actual source directly:

- `src/main.cpp`: PlatformIO example.
- `lib/BME690_unofficial/src/`: BME690 library source.
- `lib/BSEC3_unofficial/src/`: BSEC3 library source.
- `lib/7Semi_BMV080/src/`: third-party 7Semi dependency source.

The main repository and your two library repositories are independent. Library sources stay local under ignored `lib/`; the main project stores only dependency URLs and commit references. No patches are used.

## Normal work

1. Edit the library source here.
2. Build/test the project against that source: `pio run`.
3. For an Arduino release, update `version` in that library's **both** `library.properties` and `library.json`.
4. Run `./publish.sh` and choose libraries, then BME690, BSEC3, or both.
5. The script commits your source changes and pushes each selected repository separately. After a successful push it updates the main project's `libraries.json` to that exact commit.
6. Choose whether to publish an Arduino version tag when asked. The tag comes from the library's version (`v1.4.0`, for example). Existing tags are never moved to another commit.
7. Run `./publish.sh` again and choose the main project to publish the examples and updated dependency references.

Publish BME690 before BSEC3 when a release introduces a new BME690 dependency requirement. Keep BSEC3's dependency version in `library.properties` consistent with that requirement.

## Arduino IDE

Each of your library repositories is an independently installable Arduino library, with metadata, `src/`, examples and licenses at its root. BSEC3 still requires the user to obtain/install the Bosch SDK separately.

`Arduino_project/libraries/` contains generated local copies for Arduino IDE use, not a second source of truth. After editing libraries, regenerate those copies using `Arduino_project/prepare_libraries.py` and copy the result into your sketchbook. The script refuses to overwrite existing copies; move/remove the generated directory before regenerating. Always maintain source under `lib/`.

The `.ino` and PlatformIO example are separate application files. When changing their behavior, apply the same change to both, including the adjacent compensation headers if those change.

## Arduino Library Manager

Pushing source and a version tag to each GitHub repository is separate from inclusion in Arduino Library Manager. For first-time registration, submit **each library URL separately** to the [Arduino library registry](https://github.com/arduino/library-registry#adding-a-library-to-library-manager). After acceptance, Arduino indexes eligible tagged versions. This script does not submit registry pull requests or claim registration has completed.

GitHub releases contain source only. Bosch SDK binaries, ZIPs, generated Arduino library copies, and compiled firmware are excluded from all repository pushes.
