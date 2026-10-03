# ============================================================
# wefont 中文字体生成环境（精简版）
# 优化：venv 替代 conda + 删除 matplotlib + 多阶段构建
# ============================================================

# ---------- 构建阶段 ----------
FROM ubuntu:18.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# 1. 换源 + 安装系统依赖（含 Python 3 的 C 扩展包，从 apt 装比 pip 省空间）
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python2.7 \
        python-fontforge \
        fontforge \
        potrace \
        libgl1-mesa-glx \
        python3 \
        python3-venv \
        python3-pip \
        python3-numpy \
        python3-opencv \
        python3-pil \
        python3-fonttools \
        libzbar0 \
        git \
        wget \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. 创建 venv（--system-site-packages 继承 apt 装的 numpy/opencv/pil）
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# 3. pip 安装纯 Python 小包（用清华源，不缓存）
RUN pip install --no-cache-dir \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        pyzbar fpdf qrcode

# 4. 克隆项目
WORKDIR /workspace
RUN git clone https://github.com/wenzhenl/wefont.git

# 5. 应用修复补丁
COPY patch_parse_template.py /tmp/patch_parse_template.py
COPY fix_font.py /workspace/wefont/src/fix_font.py

RUN sed -i 's|\$(brew --prefix)/bin/python3|python2.7|g' /workspace/wefont/src/forge_my_font.sh && \
    echo 'python fix_font.py $OUTPUT.ttf /tmp/fixed.ttf $OUTPUT' >> /workspace/wefont/src/forge_my_font.sh && \
    echo 'mv /tmp/fixed.ttf $OUTPUT.ttf' >> /workspace/wefont/src/forge_my_font.sh && \
    python /tmp/patch_parse_template.py && \
    rm /tmp/patch_parse_template.py

# ---------- 运行阶段 ----------
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# 只装运行必需的包（不包含 git、wget、pip、编译工具）
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python2.7 \
        python-fontforge \
        fontforge \
        potrace \
        libgl1-mesa-glx \
        python3 \
        python3-numpy \
        python3-opencv \
        python3-pil \
        python3-fonttools \
        libzbar0 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 venv 和项目
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /workspace /workspace

ENV PATH=/opt/venv/bin:$PATH
WORKDIR /workspace

CMD ["/bin/bash"]