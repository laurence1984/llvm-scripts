#!/usr/bin/python

from common import run_cmake
import os
HOME = os.path.expanduser('~')

#CC=HOME + '/llvm/build/bin/clang'
#CXX=HOME + '/llvm/build/bin/clang++'

#CC='gcc'
#CXX='g++'

CC='clang'
CXX='clang++'

inst_dir='/llvm/test-install'
optimize=0
asserts=True
debug=False
lto=False
stats=False
asan=False
ubsan=False
msan=False
static=False
shared=False
plugin=True

run_cmake(CC=CC, CXX=CXX, inst_dir=inst_dir,
          optimize=optimize, asserts=asserts, debug=debug, lto=lto,
          stats=stats, asan=asan, msan=msan, ubsan=ubsan, static=static,
          shared=shared,  plugin=plugin)
