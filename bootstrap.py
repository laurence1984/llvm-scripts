#!/usr/bin/python

from common import run_cmake

import subprocess
import os
import platform
import sys
import shutil

home = os.path.expanduser('~')
system = platform.system()

def build_stage(n):
    inst_dir = '/llvm/llvm-inst%s' % n

    optimize=True
    plugin = False
    static = system != 'Darwin'
    if n == 1:
        CC = 'clang'
        AR = 'llvm-ar'
        asserts = True
        lto = False
    else:
        prev_inst_dir = os.getcwd() + '/llvm-inst%s' % (n-1)
        os.environ['DYLD_LIBRARY_PATH'] = prev_inst_dir + '/lib/'
        CC =  prev_inst_dir + '/bin/clang'
        AR =  prev_inst_dir + '/bin/llvm-ar'
        asserts = False
        lto = True

    CXX = CC + '++'

    build_dir = home + '/llvm/bootstrap-stage%s' % n
    os.mkdir(build_dir)
    os.mkdir(home + inst_dir)

    os.chdir(build_dir)
    machine = platform.machine()
    if 'arm' in machine:
        targets = 'ARM'
    elif machine == 'x86_64':
        targets = 'X86'
    else:
        assert False

    run_cmake(CC=CC, CXX=CXX, AR=AR, inst_dir=inst_dir, optimize=optimize,
              asserts=asserts, lto=lto, static=static, plugin=plugin,
              targets=targets, thin=False)

    subprocess.check_call(['ninja'])
    subprocess.check_call(['ninja', 'install'])

    os.chdir('..')

assert os.path.exists('llvm/tools/clang')
assert os.path.exists('llvm/tools/lld')
assert os.path.exists('llvm/projects/compiler-rt')
if system == 'Darwin':
    assert os.path.exists('llvm/projects/libcxx')
else:
    assert not os.path.exists('llvm/projects/libcxx')
assert not os.path.exists('llvm/tools/clang/tools/extra')
build_stage(1)
build_stage(2)
build_stage(3)
