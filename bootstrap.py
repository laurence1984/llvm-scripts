#!/usr/bin/python

import subprocess
import os
import platform
import sys
import shutil

home = os.environ['HOME']

def build_stage(n):
    inst_dir = os.getcwd() + '/llvm-inst%s' % n

    if n == 1:
        cc = 'clang'
        extra_config_args = []
    else:
        prev_inst_dir = os.getcwd() + '/llvm-inst%s' % (n-1)
        os.environ['DYLD_LIBRARY_PATH'] = prev_inst_dir + '/lib/'
        cc =  prev_inst_dir + '/bin/clang'
        extra_config_args = ['--disable-assertions']

    cxx = cc + '++'
    cxx += ' -stdlib=libc++ -std=gnu++11'
    if n != 1:
        cc += ' -flto'
        cxx += ' -flto'

    os.environ['CC'] = cc
    os.environ['CXX'] = cxx

    build_dir = 'build-configure%s' % n
    subprocess.check_call(['mkdir', build_dir])
    subprocess.check_call(['mkdir', inst_dir])
    os.chdir(build_dir)

    configure_args = ['../llvm/configure',
                      '--prefix=' + inst_dir,
                      '--enable-optimized'] + \
                      extra_config_args

    if platform.system() != 'Darwin':
        binutils_inc_dir = home + '/binutils/binutils/include/'
        configure_args += ['--with-binutils-include=' + binutils_inc_dir]

    subprocess.check_call(configure_args)
    subprocess.check_call(['make', '-j8', 'CLANG_IS_PRODUCTION=1', 'VERBOSE=1'])
    if platform.system() != 'Darwin' and n != 1:
        os.remove('Release/bin/clang')
        subprocess.check_call(['make', '-j8', 'CLANG_IS_PRODUCTION=1',
                               'LDFLAGS=-static', 'VERBOSE=1'])

    subprocess.check_call(['make', 'install', 'CLANG_IS_PRODUCTION=1'])

    shutil.copy('../clang/tools/clang-format/clang-format.py',
                inst_dir + '/bin/')
    shutil.copy('../clang/tools/clang-format/clang-format.el',
                inst_dir + '/bin/')

    os.chdir('..')

assert os.path.exists('llvm/tools/clang')
assert os.path.exists('llvm/tools/lld')
assert os.path.exists('llvm/projects/compiler-rt')
assert os.path.exists('llvm/projects/libcxx')
assert not os.path.exists('llvm/tools/clang/tools/extra')
build_stage(1)
build_stage(2)
