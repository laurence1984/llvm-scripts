import subprocess
import platform
import os

HOME = os.environ['HOME']

def which(x):
  return subprocess.check_output(['which', x]).strip()

def run_cmake(CC='clang', CXX='clang++', AR='ar',
              inst_dir='/llvm/test-install', optimize=False, asserts=True,
              debug=False, lto=False, stats=False, asan=False,
              static=False, shared=False, plugin=True, profile=False):
  CC = which(CC)
  CXX = which(CXX)
  AR = which(AR)
  RANLIB = which('true')
  inst_dir = HOME + inst_dir

  CFLAGS=[]

  if not 'gcc' in CC:
    CFLAGS += ['-fcolor-diagnostics']

  if stats:
    CFLAGS += ['-DLLVM_ENABLE_STATS']

  if optimize:
    if debug:
      buildtype = 'RelWithDebInfo'
    else:
      buildtype = 'Release'
  else:
    if debug:
      buildtype = 'Debug'
    else:
      buildtype = 'None'

  CMAKE_ARGS  = ['-DCLANG_BUILD_EXAMPLES=ON', '-DLLVM_BUILD_EXAMPLES=ON',
                 '-G', 'Ninja',
                 '-DCMAKE_PREFIX_PATH=%s/llvm/cloog-inst' % HOME,
                 '-DCMAKE_INSTALL_PREFIX=%s' % inst_dir,
                 '-DCMAKE_BUILD_TYPE=%s' % buildtype,
                 '-DCMAKE_RANLIB=%s' % RANLIB,
                 '-DCMAKE_AR=%s' % AR,
                 '-DLLVM_ENABLE_SPHINX=ON',
                 '-DCOMPILER_RT_BUILD_SHARED_ASAN=ON']

  if platform.system() == 'Darwin':
    CMAKE_ARGS += ['-DLIBCXX_LIBCPPABI_VERSION=2']
  else:
    CMAKE_ARGS += ['-DLIBCXX_CXX_ABI=libstdc++',
                   '-DLIBCXX_LIBSUPCXX_INCLUDE_PATHS=/usr/include/c++/4.8.3;/usr/include/c++/4.8.3/x86_64-redhat-linux',
                   '-DLLVM_BINUTILS_INCDIR=%s/binutils/binutils/include' % HOME]


  linker_flags=[]
  if lto:
    linker_flags += ['-flto']
  if optimize and platform.system() != 'Darwin':
    if not profile:
      linker_flags += ['-Wl,--strip-all']

  if asan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Address']
    linker_flags += ['-shared-libasan']

  if linker_flags:
    CMAKE_ARGS +=  ['-DCMAKE_EXE_LINKER_FLAGS=' + ' '.join(linker_flags)]

  if static:
    CMAKE_ARGS += ['-DLIBCLANG_BUILD_STATIC=ON']
    CMAKE_ARGS += ['-DLLVM_BUILD_STATIC=ON']

  if shared:
    CMAKE_ARGS += ['-DBUILD_SHARED_LIBS=ON']

  if asserts:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=ON']
  else:
    CMAKE_ARGS += ['-DLLVM_ENABLE_ASSERTIONS=OFF']

  if plugin:
    CMAKE_ARGS += ['-DCLANG_PLUGIN_SUPPORT=ON']
  else:
    CMAKE_ARGS += ['-DCLANG_PLUGIN_SUPPORT=OFF']

  if lto:
    CFLAGS += ['-flto']

  CXXFLAGS=CFLAGS

  CMAKE_ARGS += ['-DCMAKE_C_FLAGS=%s' % ' '.join(CFLAGS)]
  CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS=%s' % ' '.join(CXXFLAGS)]

  os.environ['CC'] = CC
  os.environ['CXX'] = CXX
  cmd = ['cmake', '../llvm'] + CMAKE_ARGS
  subprocess.check_call(cmd)
