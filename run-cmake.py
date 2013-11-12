#!/usr/bin/python

optimize=True
asserts=True
stats=False
asan=False
msan=False
build32=False
static=False
shared=False

import subprocess
import os

CC='ccache clang'
CXX='ccache clang++'

#CC='clang'
#CXX='clang++'

CC='/home/espindola/llvm/build/bin/clang'
CXX='/home/espindola/llvm/build/bin/clang++'

#CC='/usr/bin/gcc'
#CXX='/usr/bin/g++'

CFLAGS='-ffunction-sections -fdata-sections'

if not 'gcc' in CC:
  CFLAGS += ' -Wdocumentation -fcolor-diagnostics'

  if asan:
      CFLAGS += ' -fsanitize=address'

  if msan:
      CFLAGS += ' -stdlib=libc++ -fsanitize=memory -nostdinc++ -I/home/espindola/inst/libc++-msan/include/ -L/home/espindola/inst/libc++-msan/lib -lc++ -lc++abi'
else:
  pass

if stats:
  CFLAGS += ' -DLLVM_ENABLE_STATS'

CXXFLAGS=CFLAGS + ' -std=c++11'

CMAKE_ARGS  = "-DCLANG_BUILD_EXAMPLES=ON -DLLVM_BUILD_EXAMPLES=ON -G Ninja"
#CMAKE_ARGS += " -DLLVM_LIT_EXTRA_ARGS=--use-processes"
#CMAKE_ARGS += " -DCLANG_TEST_EXTRA_ARGS=--use-processes"
CMAKE_ARGS += " -DLLVM_BINUTILS_INCDIR=/home/espindola/binutils/binutils/include"
CMAKE_ARGS += " -DCMAKE_PREFIX_PATH=/home/espindola/llvm/cloog-inst"
CMAKE_ARGS += " -DCMAKE_EXE_LINKER_FLAGS=-Wl,-gc-sections"

CMAKE_ARGS += " -DCMAKE_INSTALL_PREFIX=/home/espindola/llvm/test-install"

if static:
  CMAKE_ARGS += " -DCMAKE_EXE_LINKER_FLAGS=-static"
  CMAKE_ARGS += " -DLIBCLANG_BUILD_STATIC=ON"

if shared:
  CMAKE_ARGS += " -DBUILD_SHARED_LIBS=ON"

if build32:
    CMAKE_ARGS += " -DLLVM_BUILD_32_BITS=ON"

if asserts:
    CMAKE_ARGS += " -DLLVM_ENABLE_ASSERTIONS=ON"
else:
    CMAKE_ARGS += " -DLLVM_ENABLE_ASSERTIONS=OFF"

CMAKE_ARGS += " -DCMAKE_BUILD_TYPE=None"

if optimize:
    opt = "-O3"
else:
    opt = "-O0 -g"
    opt += " -fdebug-types-section -gsplit-dwarf"
    assert not ('ccache' in CC)

if msan:
  opt = '-O1 -g -fno-omit-frame-pointer'

CMAKE_ARGS += ' -DCMAKE_C_FLAGS="%s %s"' % (CFLAGS, opt)
CMAKE_ARGS += ' -DCMAKE_CXX_FLAGS="%s %s"' % (CXXFLAGS, opt)

cmd = 'CC="%s" CXX="%s" CFLAGS="%s" CXXFLAGS="%s" cmake ../llvm %s' % \
    (CC, CXX, CFLAGS, CXXFLAGS, CMAKE_ARGS)

subprocess.check_call(cmd, shell=True)
