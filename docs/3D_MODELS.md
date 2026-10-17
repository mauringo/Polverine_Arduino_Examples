# Polverine 3D board model and printable covers

The model is maintained by [BlackIoT/Polverine](https://github.com/BlackIoT/Polverine), separately from this Arduino example. Upstream [DOCS](https://github.com/BlackIoT/Polverine/tree/main/DOCS) contains `Polverine3D.zip`, holding **`Polverine.stp`**. This is a board assembly STEP model for mechanical CAD, not a ready-to-print case STL.

## Fetch only the CAD portion

From this project's root on macOS or Linux, with Git and Python 3 installed:

```sh
python3 scripts/fetch_3d_models.py
```

The helper uses Git's shallow partial clone and sparse checkout to fetch the selected CAD files and license, avoiding a full firmware/SDK checkout. It then extracts only the expected STEP file. Result:

```text
hardware/Polverine/
  LICENSE
  SOURCE.txt                 # Upstream URL and exact fetched commit
  DOCS/README.md
  DOCS/Polverine3D.zip        # Upstream archive, local only
  DOCS/Polverine.stp          # Extracted board model
```

The default destination is ignored by this repository. No downloaded ZIP, model or upstream library source is included when publishing the main project. Review upstream licensing and retain notices when reusing its CAD. The helper refuses to overwrite an existing destination, protecting local CAD edits. To fetch again, choose a new `--destination` outside this repository or move your existing folder first. A custom destination inside this project needs its own `.gitignore` entry.

The verified upstream revision is `e75cb7adce5f9aa2b92c1f5565591db9b1cd24f1`. The helper fetches the current default branch and records its actual revision; inspect `SOURCE.txt` if upstream changes later.

## Equivalent manual sparse clone

Run these sequentially from the main project root:

```sh
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/BlackIoT/Polverine.git hardware/Polverine
git -C hardware/Polverine sparse-checkout set --no-cone /DOCS/README.md /DOCS/Polverine3D.zip /LICENSE
git -C hardware/Polverine checkout
python3 - <<'PYCODE'
from pathlib import Path
from zipfile import ZipFile
folder = Path('hardware/Polverine/DOCS')
with ZipFile(folder / 'Polverine3D.zip') as archive:
    (folder / 'Polverine.stp').write_bytes(archive.read('Polverine.stp'))
print(folder / 'Polverine.stp')
PYCODE
git -C hardware/Polverine rev-parse HEAD
```

Open `Polverine.stp` in a CAD application supporting STEP to inspect the board and design around it. The commands select files from the upstream project; they do not change this project's dependencies or run upstream firmware.

## Printable Polverine cover

BlackIoT's [main README](https://github.com/BlackIoT/Polverine#3d-printed-cover) links a [community cover by skunkyprototypes on MakerWorld](https://makerworld.com/en/models/1806923-blackiot-polverine-cover#profileId-1988748). Download printable assets from their original author and check their separate license and board revision compatibility. They are not included in `Polverine3D.zip`.

Check sensor openings and mechanical clearance in any enclosure design. After adding a cover, compare temperature with a reference thermometer again: board heating/airflow differ from an open board, and this repository's provisional calibration may not suit that enclosure.
