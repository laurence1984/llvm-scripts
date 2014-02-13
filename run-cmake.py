#!/usr/bin/python

optimize=False
asserts=True
debug=False
lto=False
stats=False
asan=False
msan=False
build32=False
static=False
shared=False

import subprocess
import platform
import os

HOME = os.environ['HOME']

CC='clang'
CXX='clang++'

#CC=HOME + '/llvm/build/bin/clang'
#CXX=HOME + '/llvm/build/bin/clang++'

#CC='/usr/bin/gcc'
#CXX='/usr/bin/g++'

CFLAGS=[]
if not 'gcc' in CC:
  CFLAGS += ['-Wdocumentation', '-fcolor-diagnostics']

  if asan:
      CFLAGS += ['-fsanitize=address']

  if msan:
      CFLAGS += ['-stdlib=libc++', '-fsanitize=memory', '-nostdinc++', '-I%s/inst/libc++-msan/include/' % HOME,
                 '-L%s/inst/libc++-msan/lib' % HOME, '-lc++', '-lc++abi']

if stats:
  CFLAGS += ['-DLLVM_ENABLE_STATS']

CMAKE_ARGS  = ['-DCLANG_BUILD_EXAMPLES=ON', '-DLLVM_BUILD_EXAMPLES=ON', '-G Ninja']
CMAKE_ARGS += ['-DLLVM_BINUTILS_INCDIR=%s/binutils/binutils/include' % HOME]
CMAKE_ARGS += ['-DCMAKE_PREFIX_PATH=%s/llvm/cloog-inst' % HOME]
CMAKE_ARGS += ['-DCMAKE_INSTALL_PREFIX=%s/llvm/test-install' % HOME]
CMAKE_ARGS += ['-DCMAKE_BUILD_TYPE=None']

linker_flags=[]
if static:
  linker_flags += ['-static']
if lto:
  linker_flags += ['-flto']
if linker_flags:
  CMAKE_ARGS +=  ['-DCMAKE_EXE_LINKER_FLAGS="' + ' '.join(linker_flags) + '"']

if static:
  CMAKE_ARGS += [' -DLIBCLANG_BUILD_STATIC=ON', '-DLLVM_ENABLE_PIC=OFF']

if shared:
  CMAKE_ARGS += ['-DBUILD_SHARED_LIBS=ON']

if build32:
    CMAKE_ARGS += ['-DLLVM_BUILD_32_BITS=ON']

if asserts:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=ON']
else:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=OFF']

if msan:
    opt = ['-O1', '-g', '-fno-omit-frame-pointer']
elif lto:
    opt = ['-O3', '-flto']
elif optimize:
    opt = ['-O3']
else:
    opt = ['-O0']
    CMAKE_ARGS += ['-DLLVM_NO_DEAD_STRIP=ON']

if debug:
  opt += ['-g']
  if platform.system() != 'Darwin':
    opt += ['-fdebug-types-section', '-gsplit-dwarf']
    assert not ('ccache' in CC)

if platform.system() != 'Darwin':
  CMAKE_ARGS += ['-DCMAKE_AR=%s/inst/binutils/bin/ar' % HOME]

CFLAGS += opt
CXXFLAGS=CFLAGS + ['-std=c++11']

CMAKE_ARGS += ['-DCMAKE_RANLIB=/usr/bin/true']
CMAKE_ARGS += ['-DCMAKE_C_FLAGS="%s"' % ' '.join(CFLAGS)]
CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS="%s"' % ' '.join(CXXFLAGS)]

cmd = 'CC="%s" CXX="%s" cmake ../llvm %s' % (CC, CXX, ' '.join(CMAKE_ARGS))

subprocess.check_call(cmd, shell=True)
