FROM mcr.microsoft.com/devcontainers/base:jammy

# Specify the PIXI version to install
ARG PIXI_VERSION=v0.40.3

# Download and install PIXI; using a URL that downloads the proper binary (for linux-musl).
RUN curl -L -o /usr/local/bin/pixi -fsSL --compressed "https://github.com/prefix-dev/pixi/releases/download/${PIXI_VERSION}/pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi info

# Configure user and working directory for VS Code
USER vscode
WORKDIR /home/vscode

# Add PIXI bash completion
RUN echo 'eval "$(pixi completion -s bash)"' >> /home/vscode/.bashrc