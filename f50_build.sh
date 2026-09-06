#!/bin/bash
# F50 (MU300) 5.4.302 内核构建(在 GitHub Actions runner 上执行)
# 代码 = 5.4.302 + 26 个 stable 补丁 + feimao 板;vermagic 伪装 5.4.254(保 vendor 模块 ABI)
set -e
export PATH=/opt/clang/clang-r416183b/bin:$PATH
export ZTE_BOARD_NAME=anthurium
SRC=$GITHUB_WORKSPACE/w205ds_276
OUT=$GITHUB_WORKSPACE/out
mkdir -p $OUT
cp config $OUT/.config
cd $OUT
sed -i 's|^CONFIG_LOCALVERSION=.*|CONFIG_LOCALVERSION="-android12-9-g9c6342244991"|' .config
sed -i 's|^CONFIG_LOCALVERSION_AUTO=y|# CONFIG_LOCALVERSION_AUTO is not set|' .config
sed -i 's|^CONFIG_MODULE_SIG_FORCE=y|# CONFIG_MODULE_SIG_FORCE is not set|' .config
sed -i 's|^CONFIG_MODULE_SIG_ALL=y|# CONFIG_MODULE_SIG_ALL is not set|' .config
sed -i 's|^CONFIG_DEBUG_INFO=y|# CONFIG_DEBUG_INFO is not set|' .config
sed -i 's|^CONFIG_UAPI_HEADER_TEST=y|# CONFIG_UAPI_HEADER_TEST is not set|' .config
cd $SRC
echo '=== olddefconfig ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig 2>&1 | tail -2
echo '=== Image ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- -j2 Image 2>&1 | tail -5
echo '=== modules_prepare ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- modules_prepare 2>&1 | tail -3
echo '=== zram.ko ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- M=drivers/block/zram modules 2>&1 | tail -3
echo BUILD_DONE
ls -la $OUT/arch/arm64/boot/Image
