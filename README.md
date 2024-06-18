# GLMFuzz 编译指南

## 项目

github: https://github.com/msxfXF/GLMFuzz
docker hub: https://hub.docker.com/layers/msxf/glmfuzz

## 设置环境变量

```bash
export LLVM_VERSION=16
```

## 更新软件源

将Ubuntu的软件源更改为清华大学的镜像源，以加快下载速度：

```bash
sed -i 's@archive.ubuntu.com@mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list
sed -i 's@security.ubuntu.com@mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list
```

## 更新系统并安装基本工具

更新系统并安装一些基本工具：

```bash
apt-get update
apt-get full-upgrade -y
apt-get install -y --no-install-recommends wget ca-certificates apt-utils
rm -rf /var/lib/apt/lists/*
```

## 安装 NVIDIA 驱动

首先，确保您的系统上安装了最新的 NVIDIA 驱动。您可以通过以下命令来安装，版本号请自行查阅：

```bash
sudo apt-get update
sudo apt-get install -y nvidia-driver-470
```

安装完成后，重启系统以使驱动生效：

```bash
sudo reboot
```

## 安装 CUDA

接下来，安装 CUDA 工具包。请根据您的操作系统和 CUDA 版本下载相应的安装包。以下是安装 CUDA 11.3 的示例：

```bash
wget https://developer.download.nvidia.com/compute/cuda/11.3.0/local_installers/cuda_11.3.0_465.19.01_linux.run
sudo sh cuda_11.3.0_465.19.01_linux.run
```

在安装过程中，选择安装 CUDA 工具包和驱动（如果尚未安装驱动）。

安装完成后，添加 CUDA 路径到环境变量：

```bash
echo 'export PATH=/usr/local/cuda-11.3/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.3/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

## 安装 cuDNN

下载并安装 cuDNN 库。以下是安装 cuDNN 8.2 的示例：

```bash
wget https://developer.download.nvidia.com/compute/redist/cudnn/v8.2.0/cudnn-11.3-linux-x64-v8.2.0.53.tgz
tar -xzvf cudnn-11.3-linux-x64-v8.2.0.53.tgz
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

## 安装依赖项

在编译 PyTorch 之前，您需要安装一些依赖项：

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake git libopenblas-dev libblas-dev libeigen3-dev python3-dev python3-pip
pip3 install numpy pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses
```

## 编译和安装 PyTorch

克隆 PyTorch 仓库并编译安装：

```bash
git clone --recursive https://github.com/pytorch/pytorch
cd pytorch
git submodule sync
git submodule update --init --recursive
python3 setup.py install
```

## 验证安装

安装完成后，您可以通过以下命令验证 PyTorch 和 CUDA 的安装是否成功：

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

如果输出显示 PyTorch 版本号和 CUDA 设备名称，则说明安装成功。

## 添加LLVM软件源

添加LLVM软件源并下载其GPG密钥：

```bash
echo "deb [signed-by=/etc/apt/keyrings/llvm-snapshot.gpg.key] http://apt.llvm.org/jammy/ llvm-toolchain-jammy-${LLVM_VERSION} main" > /etc/apt/sources.list.d/llvm.list
wget -qO /etc/apt/keyrings/llvm-snapshot.gpg.key https://apt.llvm.org/llvm-snapshot.gpg.key
```

## 安装所需软件包

安装项目所需的各种软件包：

```bash
apt-get update
apt-get -y install --no-install-recommends \
    make cmake automake meson ninja-build bison flex \
    git xz-utils bzip2 wget jupp nano bash-completion less vim joe ssh psmisc \
    python3 python3-dev python3-pip python-is-python3 \
    libtool libtool-bin libglib2.0-dev \
    apt-transport-https gnupg dialog \
    gnuplot-nox libpixman-1-dev bc \
    gcc-${GCC_VERSION} g++-${GCC_VERSION} gcc-${GCC_VERSION}-plugin-dev gdb lcov \
    clang-${LLVM_VERSION} clang-tools-${LLVM_VERSION} libc++1-${LLVM_VERSION} \
    libc++-${LLVM_VERSION}-dev libc++abi1-${LLVM_VERSION} libc++abi-${LLVM_VERSION}-dev \
    libclang1-${LLVM_VERSION} libclang-${LLVM_VERSION}-dev \
    libclang-common-${LLVM_VERSION}-dev libclang-rt-${LLVM_VERSION}-dev libclang-cpp${LLVM_VERSION} \
    libclang-cpp${LLVM_VERSION}-dev liblld-${LLVM_VERSION} \
    liblld-${LLVM_VERSION}-dev liblldb-${LLVM_VERSION} liblldb-${LLVM_VERSION}-dev \
    libllvm${LLVM_VERSION} libomp-${LLVM_VERSION}-dev libomp5-${LLVM_VERSION} \
    lld-${LLVM_VERSION} lldb-${LLVM_VERSION} llvm-${LLVM_VERSION} \
    llvm-${LLVM_VERSION}-dev llvm-${LLVM_VERSION}-runtime llvm-${LLVM_VERSION}-tools \
    $([ "$(dpkg --print-architecture)" = "amd64" ] && echo gcc-${GCC_VERSION}-multilib gcc-multilib) \
    $([ "$(dpkg --print-architecture)" = "arm64" ] && echo libcapstone-dev)
rm -rf /var/lib/apt/lists/*
```

## 更新编译器替代项

设置GCC和Clang的默认版本：

```bash
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 0
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 0
update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${LLVM_VERSION} 0
update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-${LLVM_VERSION} 0
```

## 安装Rust工具链

使用Rustup安装Rust工具链：

```bash
wget -qO- https://sh.rustup.rs | CARGO_HOME=/etc/cargo sh -s -- -y -q --no-modify-path
```

## 设置环境变量

将Cargo的bin目录添加到PATH环境变量中：

```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/etc/cargo/bin
```

## 清理APT缓存

清理APT缓存以释放空间：

```bash
apt clean -y
```

## 设置LLVM配置

设置LLVM配置的环境变量：

```bash
export LLVM_CONFIG=llvm-config-16
```

## 克隆并安装afl-cov

克隆afl-cov仓库并进行安装：

```bash
git clone --depth=1 https://github.com/vanhauser-thc/afl-cov
(cd afl-cov && make install)
rm -rf afl-cov
```

## 编译和安装项目

编译和安装GLMFuzz：

```bash
git clone https://github.com/msxfXF/GLMFuzz.git
cd GLMFuzz
make distrib
sudo make install

CC=gcc-11 CXX=g++-11 TEST_BUILD= /bin/sh -c sed -i.bak 's/^	-/	/g' GNUmakefile
make clean
make distrib
([ "${TEST_BUILD}" ] || (make install))
mv GNUmakefile.bak GNUmakefile
```

## 配置开发环境

配置开发环境的一些常用设置：

```bash
CC=gcc-11 CXX=g++-11 TEST_BUILD= /bin/sh -c echo "set encoding=utf-8" > /root/.vimrc
echo ". /etc/bash_completion" >> ~/.bashrc
echo 'alias joe="joe --wordwrap --joe_state -nobackup"' >> ~/.bashrc
echo "export PS1='"'[AFL++ \h] \w \$ '"'" >> ~/.bashrc
```
