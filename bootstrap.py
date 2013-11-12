#!/usr/bin/python

import subprocess
import os
import sys
import shutil

home = os.environ['HOME']

def build_stage(n):
    inst_dir = home + '/inst/clang'

    if n == 1:
        cc = inst_dir + '/bin/clang'
        cxx = cc + '++'
        extra_config_args = []
    else:
        cc = os.getcwd() + '/build-configure%s' % (n - 1) + '/Release+Asserts/bin/clang -flto'
        cxx = os.getcwd() + '/build-configure%s' % (n - 1) + '/Release+Asserts/bin/clang++ -flto'
        extra_config_args = ['--disable-assertions']
    os.environ['CC'] = cc
    os.environ['CXX'] = cxx

    build_dir = 'build-configure%s' % n
    subprocess.check_call(['mkdir', build_dir])
    os.chdir(build_dir)
    binutils_inc_dir = home + '/binutils/binutils/include/'
    configure_args = ['../llvm/configure',
                      '--prefix=' + inst_dir,
                      '--with-binutils-include=' + binutils_inc_dir,
                      '--enable-optimized'] + \
                      extra_config_args
    subprocess.check_call(configure_args)
    subprocess.check_call(['make', '-j8', 'CLANG_IS_PRODUCTION=1', 'VERBOSE=1'])

    if n != 1:
      os.remove('Release/bin/clang')
      subprocess.check_call(['make', '-j8', 'CLANG_IS_PRODUCTION=1','LDFLAGS=-static', 'VERBOSE=1'])

    os.chdir('..')

assert os.path.exists('llvm/tools/clang')
assert os.path.exists('llvm/tools/lld')
assert os.path.exists('llvm/projects/compiler-rt')
assert not os.path.exists('llvm/tools/clang/tools/extra')
build_stage(1)
build_stage(2)

shutil.move(home + '/inst/clang', home + '/inst/clang-old')
os.chdir('build-configure2')
subprocess.check_call(['make', 'install'])
os.chdir('..')
shutil.copy('clang/tools/clang-format/clang-format.py',
            home + '/inst/clang/bin/')
shutil.copy('clang/tools/clang-format/clang-format.el',
            home + '/inst/clang/bin/')
