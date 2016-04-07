import subprocess
import platform
import os
import shutil

HOME = os.path.expanduser('~')
system = platform.system()

def which(x):
  try:
    ret = shutil.which(x)
  except AttributeError:
    return subprocess.check_output(['which', x]).strip()
  assert ret
  return ret

def get_system_memory():
  if system == 'Darwin':
    num_bytes = int(subprocess.check_output(['sysctl', 'hw.memsize']).split(':')[1].strip())
  else:
    num_bytes = (os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))
  return num_bytes/1024.0/1024.0/1024.0

def get_num_lto_link_processes():
    return int(get_system_memory()/3)

def run_cmake(CC='clang', CXX='clang++', AR='llvm-ar',
              inst_dir='/llvm/test-install', optimize=False, asserts=True,
              debug=False, lto=False, stats=False, asan=False, msan=False,
              static=False, shared=False, plugin=True, profile=False,
              targets='all', build32=False, ubsan=False, thin=True,
              lld=False):
  CC = which(CC)
  CXX = which(CXX)
  inst_dir = HOME + inst_dir

  CFLAGS=[]

  if 'clang' in CC:
    CFLAGS += ['-fcolor-diagnostics', '-fno-unique-section-names']

  if stats:
    CFLAGS += ['-DLLVM_ENABLE_STATS']

  CMAKE_ARGS = []

  if optimize:
    if debug:
      buildtype = 'RelWithDebInfo'
    else:
      buildtype = 'Release'
  else:
    if debug:
      buildtype = 'Debug'
    else:
      buildtype = 'Release'
      CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS_RELEASE=-O0 -DNDEBUG']
      CMAKE_ARGS += ['-DCMAKE_C_FLAGS_RELEASE=-O0 -DNDEBUG']

  if system == 'Darwin' or not thin:
    AR_OPTS = 'cr'
  else:
    AR_OPTS = 'crT'
  AR_COMMAND = 'rm -f <TARGET>; %s %s <TARGET> <OBJECTS>' % (AR, AR_OPTS)

  CMAKE_ARGS += ['-DCLANG_BUILD_EXAMPLES=ON', '-DLLVM_BUILD_EXAMPLES=ON',
                 '-G', 'Ninja',
                 '-DCMAKE_INSTALL_PREFIX=%s' % inst_dir,
                 '-DCMAKE_BUILD_TYPE=%s' % buildtype,
                 '-DCMAKE_CXX_CREATE_STATIC_LIBRARY=%s' % AR_COMMAND,
                 '-DCOMPILER_RT_BUILD_SHARED_ASAN=ON',
                 '-DLLVM_TARGETS_TO_BUILD=%s' % targets]
  if build32:
    CMAKE_ARGS += ['-DLLVM_BUILD_32_BITS=ON']

  if system == 'Darwin':
    CMAKE_ARGS += ['-DLIBCXX_LIBCPPABI_VERSION=2']
  if system == 'Linux':
    CMAKE_ARGS += ['-DLLVM_ENABLE_SPHINX=ON']
  if system != 'Darwin':
    CMAKE_ARGS += ['-DLIBCXX_CXX_ABI=libstdc++',
                   '-DLIBCXX_LIBSUPCXX_INCLUDE_PATHS=/usr/include/c++/4.8.3;/usr/include/c++/4.8.3/x86_64-redhat-linux',
                   '-DLLVM_BINUTILS_INCDIR=%s/binutils/binutils/include' % HOME]

  if system == 'Windows':
    CMAKE_ARGS += ['-DLLVM_LIT_TOOLS_DIR=' + HOME + '/gnuwin32/GetGnuWin32/gnuwin32/bin']
    if not debug:
      CMAKE_ARGS += ['-DCMAKE_STATIC_LINKER_FLAGS=/llvmlibthin',
                     '-DCMAKE_LINKER=%s' % which('lld-link')]

  linker_flags=[]
  if lto:
    linker_flags += ['-flto']
    CMAKE_ARGS += ['-DLLVM_PARALLEL_LINK_JOBS=%s' % get_num_lto_link_processes()]
  if optimize and system == 'Linux' and not profile:
    linker_flags += ['-Wl,--strip-all']

  if lld:
    linker_flags += ['-fuse-ld=lld']

  if ubsan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Undefined']
  elif asan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Address']
  elif msan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Memory']

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
