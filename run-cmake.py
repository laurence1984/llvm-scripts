#!/usr/bin/python

from common import run_cmake

#CC=HOME + '/inst/clang/bin/clang'
#CXX=HOME + '/inst/clang/bin/clang++'

#CC=HOME + '/llvm/build/bin/clang'
#CXX=HOME + '/llvm/build/bin/clang++'

#CC='/usr/bin/gcc'
#CXX='/usr/bin/g++'


CC='clang'
CXX='clang++'
AR='ar'
RANLIB='true'
inst_dir='/llvm/test-install'
optimize=True
asserts=True
debug=False
lto=False
stats=False
asan=False
build32=False
static=False
shared=False
production=False

run_cmake(CC=CC, CXX=CXX, AR=AR, RANLIB=RANLIB, inst_dir=inst_dir,
          optimize=optimize, asserts=asserts, debug=debug, lto=lto,
          stats=stats, asan=asan, build32=build32, static=static, shared=shared,
          production=production)
