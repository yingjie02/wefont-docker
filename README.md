# wefont Docker 镜像

Docker image for **wefont** — 中文个人手写字体生成工具。已修复原项目的 macOS 兼容性、二维码识别、噪点干扰、字体元数据、中文 locale 等问题，精简至约 487MB，开箱即用。

## 📖 简介

[wefont](https://github.com/wenzhenl/wefont) 是一个中文个人手写字体制作工具，使用 FontForge 将手写扫描件转换为 TTF 字体。本项目将其封装为 Docker 镜像，无需手动配置复杂的 Python 2.7 / FontForge 环境。

### 主要特性

- **基础镜像**：Ubuntu 18.04 + venv（精简版，约 487MB）
- **国内加速**：所有 apt / pip 源已替换为清华源
- **双版本**：
  - **基础版**：保留所有笔画细节，不误伤点、顿等小笔画
  - **去噪版**：追加连通域去噪，解决扫描件噪点导致字变小的问题
- **自动修复**：
  - `forge_my_font.sh` 的 macOS 路径问题
  - 二维码识别（多尺度放大 + 多阈值重试 + 原始灰度图回退）
  - 字体 name 表和 OS/2 表（支持中文，Word 可用）
  - Python 3 读取中文文件的 locale 编码问题
- **精简优化**：删除 matplotlib，多阶段构建，运行阶段不含编译工具

## 🚀 快速开始

### 拉取镜像

本项目提供两个版本：

| 版本 | 标签 | 使用场景 |
| :--- | :--- | :--- |
| **基础版** | `latest`, `v1.0.3-base` | 扫描件质量好，或担心降噪误伤笔画 |
| **去噪版** | `v1.0.3-denoise` | 扫描件有噪点，导致字体里某些字偏小 |

```bash
# 基础版
docker pull ghcr.io/yingjie02/wefont-docker:latest

# 去噪版
docker pull ghcr.io/yingjie02/wefont-docker:v1.0.3-denoise
```

### 运行容器

**基础版：**

```bash
docker run -it --rm \
  -v "你的输出目录:/workspace/output" \
  -v "你的输出目录/input:/workspace/input" \
  ghcr.io/yingjie02/wefont-docker:latest
```

**去噪版：**

```bash
docker run -it --rm \
  -v "你的输出目录:/workspace/output" \
  -v "你的输出目录/input:/workspace/input" \
  ghcr.io/yingjie02/wefont-docker:v1.0.3-denoise
```

---

## 📘 完整使用指南

### 流程概览

```
生成模板 PDF → 打印 → 手写 → 扫描 → 生成字体
```

支持**分批书写 + 逐步打补丁**，不需要一次写完所有汉字。

### 第一步：生成模板

进入容器后：

```bash
cd /workspace/wefont/src

# 生成模板（以 25mm 字格为例）
python generate_template.py config/gb2312.txt -cs 25 -o myfont_25.pdf

# 复制到宿主机 output 目录
cp myfont_25.pdf /workspace/output/
```

**参数说明**：

| 参数 | 说明 | 推荐值 |
| :--- | :--- | :--- |
| `-cs` | 字格大小（mm） | 25（易写），20（平衡），15（页数少） |
| `-o` | 输出文件名 | 自定义 |

**可用字集**：

| 文件 | 字数 |
| :--- | :--- |
| `gb2312_test_测试集_郭襄小诗_.txt` | 53 |
| `gb2312_1k_常用一千字.txt` | 1000 |
| `gb2312_2k_常用二千字.txt` | 2000 |
| `gb2312_3k_常用三千字.txt` | 3000 |
| `gb2312_4k_常用四千字.txt` | 4000 |
| `gb2312.txt` | 6763 |

### 第二步：打印、手写、扫描

1. **打印**：A4 纸，**100% 缩放**，不要选"适合页面"
2. **手写**：黑色签字笔，字写在格子中间，不压线
3. **扫描**：推荐扫描仪 300 DPI 以上；手机拍照需正对、光线均匀、**不要截图**
4. **命名**：按顺序命名，如 `1.jpg`、`2.jpg`
5. **放回**：将 JPG 放入宿主机 `output/input/` 目录

### 第三步：生成字体

**基础版生成：**

```bash
cd /workspace/wefont/src
./forge_my_font.sh myfont_base /workspace/input/*.jpg
cp myfont_base.ttf /workspace/output/
```

**去噪版生成：**

```bash
cd /workspace/wefont/src
./forge_my_font.sh myfont_denoise /workspace/input/*.jpg
cp myfont_denoise.ttf /workspace/output/
```

> **字体名建议用英文**，因为 Python 2.7 脚本处理中文文件名会报编码错误。

### 第四步：安装字体（Windows）

1. 打开 `output` 目录
2. 右键 `myfont_base.ttf` → **"为所有用户安装"**
3. 在 Word 里输入文字，选中后字体设为 `myfont_base`

### 第五步：合并筛选（高级用法）

如果你发现基础版字体中某些字偏小，可以用去噪版替换这些字：

#### 5.1 找出偏小的字

安装 `myfont_base.ttf`，在 Word 里逐个输入你写过的字，记下偏小的字。

#### 5.2 写入筛选文件

创建 `output/replace.json`：

```json
["的", "我", "了", "好", "一", "字"]
```

#### 5.3 合并

运行容器，挂载工具目录：

```bash
docker run -it --rm \
  -v "你的输出目录:/workspace/output" \
  -v "项目根目录:/workspace/tools" \
  ghcr.io/yingjie02/wefont-docker:latest
```

容器内：

```bash
python /workspace/tools/replace_glyphs.py \
    /workspace/output/myfont_base.ttf \
    /workspace/output/myfont_denoise.ttf \
    /workspace/output/replace.json \
    /workspace/output/myfont_final.ttf
exit
```

#### 5.4 安装 final 字体

卸载 `myfont_base`，安装 `myfont_final.ttf`。验证：

- 偏小的字应该恢复正常（来自去噪版）
- 其他字保持原样（来自基础版，笔画未被误伤）

### 第六步：打补丁（写错字或补充新字）

**写错字：**

```bash
python generate_template.py 错字集.txt -cs 25 -o patch.pdf
cp patch.pdf /workspace/output/
# 打印、手写、扫描后
./patch_my_font.sh myfont_final.ttf /workspace/input/补丁1.jpg
```

**补充新字**（分批策略）：

| 批次 | 字集 | 操作 |
| :--- | :--- | :--- |
| 第 1 批 | `gb2312_1k_常用一千字.txt` | `./forge_my_font.sh` 生成基础字体 |
| 第 2+ 批 | 后续字集新增的字 | `./patch_my_font.sh` 追加 |

---

## 🐳 镜像信息

| 项目 | 值 |
| :--- | :--- |
| 镜像大小 | ~487MB |
| 基础镜像 | Ubuntu 18.04 |
| Python 3 | 3.6 (venv) |
| Python 2 | 2.7 (FontForge 绑定) |
| 字体引擎 | FontForge |
| 矢量化 | Potrace |
| 默认 locale | `C.UTF-8` |

| 版本 | 标签 | 修复内容 |
| :--- | :--- | :--- |
| **基础版** | `latest`, `v1.0.3-base` | QR 修复、灰度回退、字体元数据修复 |
| **去噪版** | `v1.0.3-denoise` | 在基础版上追加连通域去噪 |

## 🔧 修复说明

| 文件 | 修复内容 |
| :--- | :--- |
| `Dockerfile.base` / `Dockerfile.denoise` | `LANG=C.UTF-8` 和 `LC_ALL=C.UTF-8`，解决中文文件读取 |
| `Dockerfile.base` / `Dockerfile.denoise` | venv 替代 conda，删除 matplotlib，多阶段构建 |
| `forge_my_font.sh` | macOS 路径 → `python2.7`，自动调用 `fix_font.py` |
| `parse_template.py` | 阈值 128 → 140，QR 多尺度重试，灰度回退 |
| `patch_parse_template_denoise.py` | 追加连通域去噪点 |
| `fix_font.py` | 修复 name 表（防止截断）和 OS/2 表（GB2312/GBK） |

## 📦 自行构建

确保当前目录包含以下文件：

- `Dockerfile.base`
- `Dockerfile.denoise`
- `patch_parse_template.py`
- `patch_parse_template_denoise.py`
- `fix_font.py`

```bash
# 基础版
docker build -f Dockerfile.base -t wefont-cn-base .

# 去噪版
docker build -f Dockerfile.denoise -t wefont-cn-denoise .
```

## ❓ 常见问题

**Q：为什么生成的字体在 Word 里显示为等线？**
A：字体已自动修复 name 表和 OS/2 表。如果仍回退，确认：1) 已"为所有用户安装"；2) Word 已重启；3) 使用字体包含的字符测试。

**Q：为什么报 `CANNOT DECODE QRCODE`？**
A：扫描件二维码不清晰。用扫描仪 300 DPI 以上重新扫描，或手机正对纸面拍照。**不要用截图**。

**Q：基础版和去噪版怎么选？**
A：先用基础版生成字体，安装后在 Word 里检查。如果所有字大小正常，就用基础版。如果某些字明显偏小，再用去噪版 + `replace_glyphs.py` 替换这些字。

**Q：为什么字体里有些字特别小？**
A：扫描件里混入了孤立小黑点（噪点），撑大了字形边界框，字体按边界框缩放时字被"稀释"。基础版不处理噪点；去噪版会用连通域分析去掉小噪点。推荐的流程是：基础版为主 + 去噪版替换偏小的字，既能修问题，又不误伤点、顿等笔画。

**Q：为什么生成的字体名是英文的？**
A：Python 2.7 脚本处理中文文件名会报 `UnicodeDecodeError`。用英文名生成即可。

**Q：要写多少字才能日常使用？**
A：建议至少 1000 字。完整 GB2312 需要写 6763 字，建议分批进行。

## 📁 目录结构

```
.
├── Dockerfile.base                  # 基础版镜像
├── Dockerfile.denoise               # 去噪版镜像
├── patch_parse_template.py          # 基础版补丁
├── patch_parse_template_denoise.py  # 去噪版补丁
├── fix_font.py                      # 字体元数据修复
├── replace_glyphs.py                # 合并脚本（运行时挂载）
├── README.md
└── .gitignore
```

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。

## 📄 许可

本项目基于 [wefont](https://github.com/wenzhenl/wefont) 构建，遵循其原始许可。字体生成工具本身使用开源 FontForge，你拥有自己生成的字体完全版权。

## 🙏 致谢

- [wefont](https://github.com/wenzhenl/wefont) — 原始项目
- [FontForge](https://fontforge.org/) — 字体编辑引擎
- [Potrace](https://potrace.sourceforge.net/) — 位图矢量化工具