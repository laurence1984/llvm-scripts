#!/usr/bin/python

from common import run_cmake

import subprocess
import os
import platform
import sys
import shutil

home = os.environ['HOME']

def build_stage(n):
    inst_dir = '/llvm/llvm-inst%s' % n

    optimize=True
    production = True
    static = True
    if n == 1:
        CC = 'clang'
        asserts = True
        lto = False
    else:
        prev_inst_dir = os.getcwd() + '/llvm-inst%s' % (n-1)
        os.environ['DYLD_LIBRARY_PATH'] = prev_inst_dir + '/lib/'
        CC =  prev_inst_dir + '/bin/clang'
        asserts = False
        lto = True

    CXX = CC + '++'

    build_dir = home + '/llvm/bootstrap-stage%s' % n
    subprocess.check_call(['mkdir', build_dir])
    subprocess.check_call(['mkdir', home + inst_dir])
    os.chdir(build_dir)

    run_cmake(CC=CC, CXX=CXX, inst_dir=inst_dir, optimize=optimize,
              asserts=asserts, lto=lto, static=static, production=production)

    subprocess.check_call(['ninja', '-v'])
    subprocess.check_call(['ninja', '-v', 'install'])

    shutil.copy('../clang/tools/clang-format/clang-format.py',
                home + inst_dir + '/bin/')
    shutil.copy('../clang/tools/clang-format/clang-format.el',
                home + inst_dir + '/bin/')

    os.chdir('..')

assert os.path.exists('llvm/tools/clang')
assert os.path.exists('llvm/tools/lld')
assert os.path.exists('llvm/projects/compiler-rt')
assert os.path.exists('llvm/projects/libcxx')
assert not os.path.exists('llvm/tools/clang/tools/extra')
build_stage(1)
build_stage(2)
