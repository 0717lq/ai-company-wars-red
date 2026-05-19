FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install build && python -m build --wheel

FROM python:3.11-slim

LABEL org.opencontainers.image.title="dirsort"
LABEL org.opencontainers.image.description="智能文件目录整理 CLI 工具"
LABEL org.opencontainers.image.source="https://github.com/0717lq/ai-company-wars-red"
LABEL org.opencontainers.image.version="0.4.0"

# 安装 dirsort + 全部可选依赖
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install /tmp/dirsort-*.whl[all] && rm -rf /tmp/*.whl

# 创建数据卷挂载点
VOLUME /data
WORKDIR /data

ENTRYPOINT ["dirsort"]
CMD ["--help"]
