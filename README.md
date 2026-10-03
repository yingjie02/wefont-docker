# wefont Docker 镜像

Docker image for **wefont** — 中文个人手写字体生成工具。已修复原项目的 macOS 兼容性、二维码识别、字体元数据、中文 locale 等问题，精简至约 487MB，开箱即用。

## 📖 简介

[wefont](https://github.com/wenzhenl/wefont) 是一个中文个人手写字体制作工具，使用 FontForge 将手写扫描件转换为 TTF 字体。本项目将其封装为 Docker 镜像，无需手动配置复杂的 Python 2.7 / FontForge 环境。

### 主要特性

- **基础镜像**：Ubuntu 18.04 + venv（精简版，约 487MB）
- **国内加速**：所有 apt / pip 源已替换为清华源
- **自动修复**：
  - `forge_my_font.sh` 的 macOS 路径问题
  - 二维码识别（多尺度放大 + 多阈值重试 + 原始灰度图回退）
  - 字体 name 表和 OS/2 表（支持中文，Word 可用）
  - Python 3 读取中文文件的 locale 编码问题
- **精简优化**：删除 matplotlib，多阶段构建，运行阶段不含编译工具

## 🚀 快速开始

### 从 GHCR 拉取镜像

```bash
docker pull ghcr.io/yingjie02/wefont-docker:latest
```

### 从 tar 文件加载（可选）

如果你拿到的是 `wefont-cn-lite.tar`：

```bash
docker load -i wefont-cn-lite.tar
docker tag wefont-cn-lite:latest ghcr.io/yingjie02/wefont-docker:latest
```

### 运行容器

```bash
docker run -it --rm -v "你的输出目录:/workspace/output" ghcr.io/yingjie02/wefont-docker:latest
```

> 将 `你的输出目录` 替换为宿主机上的实际路径，例如 `C:\Users\你的用户名\Desktop\font-output`。

---

## 📘 完整使用指南

### 流程概览

```
生成模板 PDF → 打印 → 手写 → 扫描 → 生成字体
```

支持**分批书写 + 逐步打补丁**，不需要一次写完所有汉字。

### 第一步：生成模板

进入容器后，选择要书写的字集：

```bash
cd /workspace/wefont/src

# 查看所有可选字集
ls config/gb2312_*.txt

# 生成模板（以 25mm 字格为例）
python generate_template.py config/gb2312.txt -cs 25 -o myfont_25.pdf

# 复制到宿主机 output 目录
cp myfont_25.pdf /workspace/output/
```

**参数说明**：

| 参数 | 说明 | 推荐值 |
| :--- | :--- | :--- |
| `-cs` | 字格大小（mm） | 25（易写），20（平衡），15（页数少） |
| `-f` | 模板中使用的字体 | 默认 `fireflysung`，一般不用改 |
| `-o` | 输出文件名 | 自定义 |
| `-rs` | 去掉格子里的序号 | 可选 |

**可用字集**：

| 文件 | 字数 | 用途 |
| :--- | :--- | :--- |
| `gb2312_test_测试集_郭襄小诗_.txt` | 53 | 先导测试，验证流程 |
| `gb2312_1k_常用一千字.txt` | 1000 | 日常基本够用 |
| `gb2312_2k_常用二千字.txt` | 2000 | 覆盖大部分场景 |
| `gb2312_3k_常用三千字.txt` | 3000 | 较完整 |
| `gb2312_4k_常用四千字.txt` | 4000 | 接近完整 |
| `gb2312.txt` | 6763 | GB2312 全集 |

### 第二步：打印、手写、扫描

1. **打印**：A4 纸，**100% 缩放**，不要选"适合页面"
2. **手写**：
   - 用**黑色签字笔**或**黑色中性笔**（色彩重的笔）
   - 每个字写在格子**中间**，不要压线
   - 保持字迹大小一致，力度均匀
3. **扫描**：
   - **推荐扫描仪**，300 DPI 以上，输出 **JPG**
   - 如果手机拍照：正对纸面、光线均匀、避免阴影
   - **绝对不要用截图**，会导致二维码无法识别
4. **命名**：按顺序命名，如 `1.jpg`、`2.jpg`、`3.jpg`
5. **放回**：将 JPG 文件放入宿主机的 output 目录

### 第三步：生成字体

回到容器内执行：

```bash
cd /workspace/wefont/src

# 单个扫描件
./forge_my_font.sh myfont /workspace/output/1.jpg

# 多个扫描件
./forge_my_font.sh myfont /workspace/output/1.jpg /workspace/output/2.jpg /workspace/output/3.jpg

# 或用通配符（注意文件顺序）
./forge_my_font.sh myfont /workspace/output/*.jpg

# 复制到宿主机
cp myfont.ttf /workspace/output/
```

> **字体名建议用英文**（如 `myfont`），因为 Python 2.7 脚本处理中文文件名会报编码错误。

### 第四步：安装字体（Windows）

1. 打开 `C:\Users\你的用户名\Desktop\font-output`
2. 右键 `myfont.ttf` → **"为所有用户安装"**
3. 打开 Word，输入文字，选中后字体设为 `myfont`

> 生成的字体已自动修复 name 表和 OS/2 表，Word 中可直接使用，不会回退到等线。

### 第五步：打补丁（写错字或补充新字）

**写错字**：

1. 把错字整理到一个文件 `错字集.txt`
2. 生成模板：

```bash
python generate_template.py 错字集.txt -cs 25 -o patch.pdf
cp patch.pdf /workspace/output/
```

3. 打印、手写、扫描后，用 `patch_my_font.sh` 覆盖：

```bash
./patch_my_font.sh myfont.ttf /workspace/output/补丁1.jpg
```

**补充新字**（推荐分批策略）：

| 批次 | 字集 | 操作 |
| :--- | :--- | :--- |
| 第 1 批 | `gb2312_1k_常用一千字.txt` | `./forge_my_font.sh myfont ...` 生成基础字体 |
| 第 2 批 | `gb2312_2k_` 中 1k 之后新增的字 | `./patch_my_font.sh myfont.ttf ...` 追加 |
| 第 3 批 | `gb2312_3k_` 中 2k 之后新增的字 | `./patch_my_font.sh myfont.ttf ...` 追加 |
| 第 4 批 | `gb2312_4k_` 中 3k 之后新增的字 | `./patch_my_font.sh myfont.ttf ...` 追加 |
| 第 5+ 批 | `gb2312.txt` 中 4k 之后剩余的字 | `./patch_my_font.sh myfont.ttf ...` 追加 |

分批策略的好处：每批工作量可控，任何一批出问题不影响已有成果，可以随时暂停。

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

## 🔧 修复说明

原项目在 Linux / Docker 环境下存在若干问题，本镜像已全部修复并固化到构建流程中。

| 文件 | 修复内容 |
| :--- | :--- |
| `Dockerfile` | 设置 `LANG=C.UTF-8` 和 `LC_ALL=C.UTF-8`，解决 Python 3.6 读取中文文件的 ASCII 解码错误 |
| `Dockerfile` | 用 venv 替代 conda，删除 matplotlib，多阶段构建 |
| `forge_my_font.sh` | macOS 路径 `$(brew --prefix)/bin/python3` → `python2.7` |
| `forge_my_font.sh` | 生成字体后自动调用 `fix_font.py` 修复元数据 |
| `parse_template.py` | 二值化阈值 `128` → `140` |
| `parse_template.py` | `decode_qrcode` 增加多尺度放大 + 多阈值重试 |
| `parse_template.py` | 保存原始灰度图，识别失败时回退 |
| `fix_font.py` | 修复 name 表（防止 `guox` 截断）和 OS/2 表（GB2312/GBK） |

## 📦 构建镜像

如需自行构建，请确保当前目录包含以下文件：

- `Dockerfile`
- `patch_parse_template.py`
- `fix_font.py`

然后执行：

```bash
docker build -t wefont-cn-lite .
```

## 🔐 哈希值校验

| 类型 | 值 |
| :--- | :--- |
| 镜像 Digest | `sha256:8104fcf3d482e53254f5cfd2225dd906ac1758a1538d00332c2f896ff52c3979` |
| tar 文件 SHA256 | `9D94C2A819078721ABC5B64FC40BFF5A6BF790E383969A111B35A98864AFAE94` |

### 验证镜像完整性

拉取镜像后，用以下命令验证 Digest：

```bash
docker buildx imagetools inspect ghcr.io/yingjie02/wefont-docker:latest
```

对比输出的 `Digest` 值是否与上表一致。

### 验证 tar 文件完整性

如果你下载了 `wefont-cn-lite.tar`，可以用以下命令校验：

**Windows PowerShell：**
```powershell
Get-FileHash wefont-cn-lite.tar -Algorithm SHA256
```

**Linux / macOS：**
```bash
sha256sum wefont-cn-lite.tar
```

## ❓ 常见问题

**Q：为什么生成的字体在 Word 里显示为等线？**
A：本镜像已自动修复字体的 name 表和 OS/2 表，正常情况下不会回退。如果仍然回退，请确认：
1. 字体已通过"为所有用户安装"安装
2. Word 已完全关闭并重启
3. 使用字体包含的字符测试（未写的字会回退）

**Q：为什么报 `CANNOT DECODE QRCODE`？**
A：扫描件二维码不清晰。请用扫描仪重新扫描（300 DPI 以上），或手机正对纸面拍照。**不要用截图**。

**Q：为什么生成的字体名是英文的？**
A：Python 2.7 脚本处理中文文件名会报 `UnicodeDecodeError`。用英文名生成后，可在字体安装时使用英文名，或在 FontForge 里改字体内部名称。

**Q：为什么 Python 3 脚本报 `UnicodeDecodeError: 'ascii' codec`？**
A：本镜像已设置 `LANG=C.UTF-8` 和 `LC_ALL=C.UTF-8`，正常情况下不会出现。如果你使用的是旧版镜像，请在命令前加 `LC_ALL=C.UTF-8`。

**Q：要写多少字才能日常使用？**
A：建议至少 1000 字（`gb2312_1k_常用一千字.txt`）。完整 GB2312 需要写 6763 字，建议分批进行。

## 📁 目录结构

```
.
├── Dockerfile                  # 镜像构建文件
├── patch_parse_template.py     # parse_template.py 修复补丁
├── fix_font.py                 # 字体元数据修复脚本
├── README.md                   # 本文件
└── .gitignore                  # Git 忽略规则
```

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。

## 📄 许可

本项目基于 [wefont](https://github.com/wenzhenl/wefont) 构建，遵循其原始许可。字体生成工具本身使用开源 FontForge，你拥有自己生成的字体完全版权。

## 🙏 致谢

- [wefont](https://github.com/wenzhenl/wefont) — 原始项目
- [FontForge](https://fontforge.org/) — 字体编辑引擎
- [Potrace](https://potrace.sourceforge.net/) — 位图矢量化工具

---
