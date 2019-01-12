# AutoFgo
可以在Unix运行的Fgo自动肝素材/狗粮/活动/脚本。

---

### 使用方法

- 使用自己咕哒子的头像替换掉`./data/menu_sample.jpg`：
  - 在`Fgo.debug()`中调用`self.grab(self.area['menu'], fname='menu_sample')`
  - 以`debug`模式启动程序（`python main.py -d`）
- 编辑`config.py`，该文件用于记载没有命令行参数时，各参数的默认值。
- 启动`main.py`。
- 更多细节参见`main.py`中的参数注释和`config.py`。

### 依赖库

- **On Unix(Linux):**
  - pillow 
  - pyuserinput
  - numpy 
  - autopy
- **Or Other**
  - pywin32
  - pillow
  - numpy

---

### Usage 

- Replace the screenshot in `./data/menu_sample.jpg` with your own image (of the right area).
  - Run `Fgo.grab(fgo.area['menu'])` to replace files.
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
