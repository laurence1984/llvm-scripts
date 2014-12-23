#!/usr/bin/python

from common import run_cmake
import os
HOME = os.environ['HOME']

#CC=HOME + '/llvm/build/bin/clang'
#CXX=HOME + '/llvm/build/bin/clang++'

#CC='gcc'
#CXX='g++'

CC='clang'
CXX='clang++'

AR='ar'
inst_dir='/llvm/test-install'
optimize=True
asserts=True
debug=False
lto=False
stats=False
asan=False
buildtype=''
static=False
shared=False
plugin=True
profile=False

run_cmake(CC=CC, CXX=CXX, AR=AR, inst_dir=inst_dir,
          optimize=optimize, asserts=asserts, debug=debug, lto=lto,
          stats=stats, asan=asan, buildtype=buildtype, static=static,
          shared=shared,  plugin=plugin, profile=profile)
