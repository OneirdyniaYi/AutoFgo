# AutoFgo
Fgo自动肝素材/狗粮/活动/脚本。

---

### Usage 

- Replace the screenshot in ./data with your own image (of the right area).
  - Run `Fgo.grab(fgo.area[name])` to replace files.
- Edit `config.py`
- Then run `main.py`

### Requirements

- **On Unix(Linux):**
  - pillow 
  - pyuserinput
  - numpy 
  - autopy
- **Or Other**
  - pywin32
  - pillow
  - numpy

### TODO

- Use skill only per N turns (not every turm), N = min_CD_time
- Add `USED_SKILL` and `ULTIMATE_SKILL` to argparse.
