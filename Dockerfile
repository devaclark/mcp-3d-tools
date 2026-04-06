FROM python:3.12-slim-bookworm

LABEL maintainer="Adam Clark <devaclark>"
LABEL description="MCP server for 3D modeling tools (OpenSCAD, Bambu Studio)"

# Prevent interactive prompts and set locale
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# System dependencies: OpenSCAD + xvfb + OpenGL for headless rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
        openscad \
        xvfb \
        xauth \
        libfuse2 \
        wget \
        ca-certificates \
        libgl1-mesa-glx \
        libgl1-mesa-dri \
        libegl1-mesa \
        libgles2-mesa \
        libosmesa6 \
        mesa-utils \
        libglib2.0-0 \
        libgtk-3-0 \
        libwebkit2gtk-4.0-37 \
    && rm -rf /var/lib/apt/lists/*

# Bambu Studio Linux CLI
# Download the AppImage, extract it, and make the CLI binary accessible.
# The version is pinned; update BAMBU_VERSION to upgrade.
ARG BAMBU_VERSION=v02.05.02.51
RUN mkdir -p /opt/bambu-studio && \
    wget -q -O /tmp/bambu.AppImage \
        "https://github.com/bambulab/BambuStudio/releases/download/${BAMBU_VERSION}/BambuStudio_linux_ubuntu_${BAMBU_VERSION}.AppImage" || \
    echo "WARN: Bambu Studio download skipped — CLI tools will be unavailable" && \
    if [ -f /tmp/bambu.AppImage ]; then \
        chmod +x /tmp/bambu.AppImage && \
        cd /opt/bambu-studio && \
        /tmp/bambu.AppImage --appimage-extract 2>/dev/null || true && \
        ln -sf /opt/bambu-studio/squashfs-root/usr/bin/bambu-studio /usr/local/bin/bambu-studio && \
        rm -f /tmp/bambu.AppImage; \
    fi

# Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY server.py .
COPY tools/ tools/
COPY utils/ utils/

# Default env (overridable via --env-file at runtime)
ENV WORKSPACE_ROOT=/workspace \
    LOG_LEVEL=INFO \
    MCP_TOOL_CATEGORIES=openscad,bambu,visual,mesh,format,workspace,education,system \
    OPENSCAD_BIN=/usr/bin/openscad \
    BAMBU_BIN=/usr/local/bin/bambu-studio \
    PYOPENGL_PLATFORM=osmesa

# Start a virtual framebuffer for OpenSCAD and pyrender headless rendering,
# then run the MCP server with clean stdout for stdio transport.
RUN printf '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 &\nexport DISPLAY=:99\nexec python server.py\n' > /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
