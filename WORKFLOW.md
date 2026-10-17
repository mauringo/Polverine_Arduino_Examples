# Maintain here, publish the libraries separately

Normal users follow the [Arduino guide](Arduino_project/README.md) or the [PlatformIO usage guide](docs/PLATFORMIO.md). The PlatformIO guide explains everyday controls, why it fits library maintenance, and how release/development environments differ. Library Manager now includes both unofficial libraries at **0.0.1**. No registry submission is needed again for future versions.

## Three independent repositories

| Folder | GitHub repository |
| --- | --- |
| Project root | [mauringo/Polverine_Arduino_Examples](https://github.com/mauringo/Polverine_Arduino_Examples) |
| `lib/BME690-Arduino-lib-unofficial` | [mauringo/BME690-Arduino-lib-unofficial](https://github.com/mauringo/BME690-Arduino-lib-unofficial) |
| `lib/Bsec3-ArduinoLibrary-Unofficial` | [mauringo/Bsec3-ArduinoLibrary-Unofficial](https://github.com/mauringo/Bsec3-ArduinoLibrary-Unofficial) |

The two library folders contain real Git checkouts and editable source. The main repository ignores all of `lib/`. The third-party BMV080 wrapper is downloaded under `lib/Polverine_BMV080_Arduino` by the maintenance bootstrap for compatibility with the existing workspace; its public Arduino name is **7Semi BMV080**. It is not one of the two libraries published by this project's menu. No source patches are generated or applied.

`libraries.json` records the **development checkout** URLs and starting revisions. `platformio.ini` records the **user build** releases. Publishing a library updates its recorded development revision but does not silently change a released dependency version for end users.

## Build directly from library source

From the project root:

```sh
python3 scripts/repos.py bootstrap
python3 scripts/install_bsec.py /path/to/bsec_v3-3-0-1.zip --library-dir lib/Bsec3-ArduinoLibrary-Unofficial
python3 scripts/install_bmv080.py /path/to/bmv080-sdk-v11-2-0.zip
pio run -e polverine-dev
```

Bootstrap downloads missing clones and checks out recorded commits. It never overwrites an existing folder or local edits. Edit `.h`, `.cpp` and `.c` files directly under `lib/`; `polverine-dev` compiles those sources in place. Use `pio run -e polverine-dev -t upload` when intentionally testing development code on hardware. Default `polverine-full`, `polverine-bsec3` and `polverine-debug` use published packages under `.pio/libdeps/` and do not pick up `lib/` changes.

To inspect changes:

```sh
python3 scripts/repos.py status
python3 scripts/repos.py diff bsec3
python3 scripts/repos.py diff bme690
python3 scripts/repos.py audit all
```

Keep `src/main.cpp` and `Arduino_project/Arduino_project.ino` behavior aligned. The `.ino` has four leading defines replacing the PlatformIO build flags. Keep each copy of the three compensation/settings headers and BlackIoT license aligned too.

## Test development libraries with Arduino IDE

Library Manager is the normal installation method. For testing unpublished source changes only:

1. Prepare the development sources/SDKs using the commands above.
2. Run `python3 Arduino_project/prepare_libraries.py` to assemble local copies under ignored `Arduino_project/libraries/`.
3. Move the existing Library Manager copies of these libraries outside your sketchbook's `libraries/` folder to avoid duplicates; retain a backup.
4. Copy the generated folders directly into the sketchbook's `libraries/` folder and restart IDE.
5. Test the sketch. Keep editing the actual nested Git sources under `lib/`, not the generated copies.
6. To return to released packages, move development copies outside the sketchbook, reinstall the published versions through Library Manager and rerun `scripts/setup_arduino.py`.

The preparation script refuses to overwrite existing generated folders. Move the old `Arduino_project/libraries/` elsewhere before regenerating after changes. These copies contain local Bosch SDK files: do not distribute them.

## Publish a library release

1. Complete changes and test against editable source with `polverine-dev` and the relevant basic/generic Arduino examples.
2. Increase `version` in **both** `library.properties` and `library.json` in the changed library. Keep their names/versions equal. Update BSEC3's BME690 dependency requirement if necessary; publish BME690 first when introducing a new dependency requirement.
3. Run `./publish.sh`, choose **libraries**, then **BME690**, **BSEC3**, or **both**.
4. The script audits prohibited files, stages changes in each selected repository, asks for a commit message (Enter accepts its suggestion), and commits. It asks before pushing. Git authentication is inherited from your shell/VS Code environment.
5. After a successful library push, `libraries.json` in the main project records the pushed commit. The main project is committed separately.
6. Accept the script's offer to publish the version tag. The tag is derived from metadata, for example `v0.0.2`. Never move a published tag: use a new version for new source.
7. Arduino's registry periodically indexes eligible new tags for these already-registered repositories. Check [the live index](https://downloads.arduino.cc/libraries/library_index.json.gz) or Library Manager for the new name/version. A GitHub push is not proof that Arduino has indexed the release.
8. After the new version is indexed, update the release references in `platformio.ini`, expected versions in `scripts/setup_arduino.py`, and version tables/commands in the READMEs. If BSEC3's manifest changes its required BME690 tag, align the project's BME690 tag with it. Re-run SDK preparation and build against the actual downloaded release packages.
9. Run `./publish.sh main` to commit and push the updated example/documentation independently.

The libraries remain Mauro Riboni's personal unofficial hobby projects, adapted from Bosch BME68x and BSEC2. Preserve Bosch attribution, original licenses and the private-work disclaimer. Registry guidance: [Arduino release requirements](https://github.com/arduino/library-registry/blob/main/FAQ.md#update-requirements).

## Commit or audit without pushing

```sh
./publish.sh                         # Interactive destination selector
./publish.sh main --commit-only      # Local commit of the main project
./publish.sh libraries --commit-only # Local commits in both libraries
./publish.sh libraries --check       # Read-only status and forbidden-file audit
```

Bash 3.2+, Git and Python 3 are sufficient on macOS/Linux; GitHub CLI is not required. A clean repository explicitly reports no pending changes. Failed pushes retain local commits for retry. The publisher audits tracked files and reachable history for ZIPs and compiled binaries. The root audit also rejects library sources/generated copies; `.gitignore` excludes the downloaded CAD subtree, SDKs and PlatformIO build products.
