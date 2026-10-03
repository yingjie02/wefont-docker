# wefont Docker 镜像

基于 [wefont](https://github.com/wenzhenl/wefont) 的中文字体生成环境，已修复原项目的 macOS 兼容性、二维码识别、字体元数据等问题，并精简至约 487MB。

## 📖 简介

`wefont` 是一个中文个人手写字体制作工具，使用 FontForge 将手写扫描件转换为 TTF 字体。本项目将其封装为 Docker 镜像，开箱即用，无需手动配置复杂的 Python 2.7 / FontForge 环境。

### 主要特性

- **基础镜像**：Ubuntu 18.04 + venv（精简版，约 487MB）
- **国内加速**：所有 apt / pip / conda 源已替换为清华源
- **自动修复**：
  - `forge_my_font.sh` 的 macOS 路径问题
  - 二维码识别（多尺度放大 + 多阈值重试 + 原始灰度图回退）
  - 字体 name 表和 OS/2 表（支持中文，Word 可用）
- **精简优化**：删除 matplotlib，多阶段构建，运行阶段不含编译工具

## 🚀 快速开始

### 拉取镜像

```bash
docker pull ghcr.io/yingjie02/wefont-docker:latest
```

### 运行容器

```bash
docker run -it --rm -v "你的输出目录:/workspace/output" ghcr.io/yingjie02/wefont-docker:latest
```

> 将 `你的输出目录` 替换为宿主机上的实际路径，例如 `C:\Users\你的用户名\Desktop\font-output`。

### 生成字体

在容器内执行：

```bash
cd /workspace/wefont/src

# 生成模板 PDF（可选，使用项目自带的测试集）
python generate_template.py "config/gb2312_test_测试集_郭襄小诗_.txt"
cp *.pdf /workspace/output/

# 打印模板、手写、扫描后，将扫描件放入 output 目录
# 然后生成字体（自动修复元数据）
./forge_my_font.sh 我的字体 /workspace/output/扫描件.jpg

# 复制到宿主机
cp 我的字体.ttf /workspace/output/
```

## 🐳 镜像信息

| 项目 | 值 |
| :--- | :--- |
| 镜像大小 | ~487MB |
| 基础镜像 | Ubuntu 18.04 |
| Python 3 | 3.6 (venv) |
| Python 2 | 2.7 (FontForge 绑定) |
| 字体引擎 | FontForge |
| 矢量化 | Potrace |

## 🔧 修复说明

原项目在 Linux / Docker 环境下存在若干问题，本镜像已全部修复并固化到构建流程中。

| 文件 | 修复内容 |
| :--- | :--- |
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
| 镜像 Digest | `sha256:推送后填写` |
| tar 文件 SHA256 | `本地计算后填写` |

获取镜像 Digest：

```bash
docker buildx imagetools inspect ghcr.io/yingjie02/wefont-docker:latest
```

计算 tar 文件 SHA256：

```powershell
Get-FileHash wefont-cn-lite.tar -Algorithm SHA256
```

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