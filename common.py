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
              static=False, shared=False, plugin=True, targets='all',
              build32=False, ubsan=False, thin=True, lld=True, examples=False):
  assert optimize == 0 or optimize == 1 or optimize == 2 or optimize == 3
  CC = which(CC)
  CXX = which(CXX)
  inst_dir = HOME + inst_dir

  CFLAGS=[]

  if 'clang' in CC:
    CFLAGS += ['-fcolor-diagnostics', '-fno-unique-section-names']

  if stats:
    CFLAGS += ['-DLLVM_ENABLE_STATS']

  CMAKE_ARGS = []

  if not optimize:
    buildtype = 'Debug'
  elif debug:
    buildtype = 'RelWithDebInfo'
  else:
    buildtype = 'Release'

  if debug:
    debug_opt = '-g'
  else:
    debug_opt = ''

  if asserts:
    assert_opt = ''
  else:
    assert_opt = '-DNDEBUG'

  opts = '-O%s %s %s' % (optimize, debug_opt, assert_opt)

  CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS_RELEASE=%s' % opts]
  CMAKE_ARGS += ['-DCMAKE_C_FLAGS_RELEASE=%s' % opts]

  CMAKE_ARGS += ['-DCMAKE_C_FLAGS_RELWITHDEBINFO=%s' % opts]
  CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=%s' % opts]

  CMAKE_ARGS += ['-DCMAKE_C_FLAGS_DEBUG=%s' % opts]
  CMAKE_ARGS += ['-DCMAKE_CXX_FLAGS_DEBUG=%s' % opts]

  if system == 'Darwin' or not thin:
    AR_OPTS = 'cr'
  else:
    AR_OPTS = 'crT'
  AR_COMMAND = 'rm -f <TARGET>; %s %s <TARGET> <OBJECTS>' % (AR, AR_OPTS)

  if examples:
    CMAKE_ARGS += ['-DCLANG_BUILD_EXAMPLES=ON', '-DLLVM_BUILD_EXAMPLES=ON']

  CMAKE_ARGS += ['-G', 'Ninja',
                 '-DCMAKE_INSTALL_PREFIX=%s' % inst_dir,
                 '-DCMAKE_BUILD_TYPE=%s' % buildtype,
                 '-DCMAKE_C_CREATE_STATIC_LIBRARY=%s' % AR_COMMAND,
                 '-DCMAKE_CXX_CREATE_STATIC_LIBRARY=%s' % AR_COMMAND,
                 '-DCOMPILER_RT_BUILD_SHARED_ASAN=ON',
                 '-DENABLE_X86_RELAX_RELOCATIONS=ON',
                 '-DLLVM_TARGETS_TO_BUILD=%s' % targets]
  if build32:
    CMAKE_ARGS += ['-DLLVM_BUILD_32_BITS=ON']

  if system == 'Darwin':
    CMAKE_ARGS += ['-DLIBCXX_LIBCPPABI_VERSION=2']
  if system == 'Linux':
    CMAKE_ARGS += ['-DLLVM_ENABLE_SPHINX=ON']
  if system != 'Darwin':
    CMAKE_ARGS += ['-DLIBCXX_CXX_ABI=libstdc++',
                   '-DLIBCXX_LIBSUPCXX_INCLUDE_PATHS=/usr/include/c++/4.8.3;/usr/include/c++/4.8.3/x86_64-redhat-linux']

  if system == 'Windows':
    CMAKE_ARGS += ['-DLLVM_LIT_TOOLS_DIR=' + HOME + '/gnuwin32/GetGnuWin32/gnuwin32/bin']

  linker_flags=[]
  if not optimize:
    linker_flags += ['-Wl,-O0', '-Wl,--build-id=none']

  if lto:
    linker_flags += ['-flto']
    CMAKE_ARGS += ['-DLLVM_PARALLEL_LINK_JOBS=%s' % get_num_lto_link_processes()]

  if lld:
    linker_flags += ['-fuse-ld=lld']

  if ubsan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Undefined']
  elif asan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Address']
  elif msan:
    CMAKE_ARGS += ['-DLLVM_USE_SANITIZER=Memory']

  if linker_flags:
    # Unfortunatelly the CMAKE_*_LINKER_FLAGS don't cover all cases.

    CFLAGS += linker_flags
    CFLAGS += ['-Qunused-arguments']

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
