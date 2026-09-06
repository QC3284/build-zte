#!/bin/bash
# F50 (MU300) 5.4.302 内核构建(在 GitHub Actions runner 上执行)
# 代码 = 5.4.302 + 26 个 stable 补丁 + feimao 板;vermagic 伪装 5.4.254(保 vendor 模块 ABI)
set -e
export PATH=/opt/clang-r416183b/bin:$PATH
SRC=$GITHUB_WORKSPACE/bsp/kernel5.4/kernel5.4
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
# 内核尺寸必须 ≤ 原厂(0x2485a00),否则 LK 拒收 —— 关 KALLSYMS 省 ~200-400KB(ABI 无关)
sed -i 's|^CONFIG_KALLSYMS=y|# CONFIG_KALLSYMS is not set|' .config
sed -i 's|^CONFIG_KALLSYMS_ALL=y|# CONFIG_KALLSYMS_ALL is not set|' .config
cd $SRC
echo '=== tool versions ==='
make --version | head -1
which bison flex clang ld.lld
clang --version | head -1
echo '=== olddefconfig (full log) ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig
echo '=== Image ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- -j2 Image
echo '=== modules_prepare ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- modules_prepare
echo '=== zram.ko ==='
make O=$OUT ARCH=arm64 LLVM=1 LLVM_IAS=1 CROSS_COMPILE=aarch64-linux-gnu- M=drivers/block/zram modules
echo BUILD_DONE
ls -la $OUT/arch/arm64/boot/Image
