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

## First Library Manager submission: exact steps

1. Run `./publish.sh libraries`. Commit the new example links and answer **yes** when asked to publish each Arduino version tag. Current prepared versions are BME690 `1.4.1` and BSEC3 `1.13.0`; keep `library.properties` and `library.json` aligned.
2. Run `./publish.sh main` to publish the examples project and the updated dependency references.
3. Fork `https://github.com/arduino/library-registry` and create a submission branch.
4. Edit `repositories.txt` in that fork. Add these two repository URLs on separate lines, leaving other entries unchanged:

```text
https://github.com/mauringo/BME690-Arduino-lib-unofficial
https://github.com/mauringo/Bsec3-ArduinoLibrary-Unofficial
```

5. Open a pull request from that branch to `arduino/library-registry:main`. Both libraries can be submitted in the same PR, as separate registry entries. Do not submit `Polverine_Arduino_Examples` as a library.
6. Follow the bot's checks and resolve any reported errors. After acceptance, search Arduino Library Manager for `BME690_unofficial` and `BSEC3_unofficial`.

For later releases: increase the version in both metadata files, commit, push, and publish a new version tag. No new registration PR is needed. Refer to [Arduino's current registration instructions](https://github.com/arduino/library-registry#adding-a-library-to-library-manager) and [release requirements](https://github.com/arduino/library-registry/blob/main/FAQ.md#update-requirements).

The library source packages exclude Bosch binaries and ZIPs. BSEC3 users must still download the SDK separately and follow its installation instructions, even after installing the wrapper through Library Manager. Registration is subject to Arduino's validation; a successful GitHub push alone does not complete it.

## Commit without publishing

Run `./publish.sh main --commit-only` for the main project or `./publish.sh libraries --commit-only` for both libraries. The script stages the selected repositories' source changes, accepts a message (Enter uses the suggested message), then commits locally without requiring a remote or authentication. A clean repository reports that it already has no uncommitted source changes. Library pushes update `libraries.json` in the main project; commit/publish the main project separately afterward.
