import os
import sys

sys.path.append("../../tools/pylib")
import vendor_build
from vendor_build import BuildLib, BuildCLI
from os.path import join as path_join

xxxROOT = None
xxxBIN  = None

def build_windows(lib_name, builder):
    COMPILER='vs2015'  # presumably this can be others
    arch = builder.get_arch()
    builder.set_rootdir(path_join(xxxROOT, 'vendors', lib_name))

    # generate build scripts
    bx_root = os.path.abspath(path_join('../', 'bx'))
    genie_exe = path_join(bx_root, 'tools', 'bin', 'windows', 'genie.exe')
    if not os.path.isfile(genie_exe):
        print("Could not find " + genie_exe)

    builder.shell([genie_exe, COMPILER])

    # build
    if builder.build_debug():
        config = 'Debug'
    else:
        config = 'Release'
    
    build_dir = path_join('.build', 'projects', COMPILER)
    os.chdir(build_dir)
    builder.devenv_build('bgfx.sln', config, 'bgfx')
    os.chdir('../../../')    
    
    # install lib
    if arch == vendor_build.arch_x64:
        arch_dir = 'win64_' + COMPILER
    elif arch == vendor_build.arch_x86:
        arch_dir = 'win32_' + COMPILER
        
    lib_path = path_join('.build', arch_dir, 'bin')
    lib_filename = 'bgfx' + config
    builder.copy_lib_file(path_join(lib_path, lib_filename+'.lib'), xxxROOT)
    builder.copy_lib_file(path_join(lib_path, lib_filename+'.pdb'), xxxROOT)

    # install headers
    builder.copy_header_files('include', xxxROOT)

    
def build_macos(libname, builder):
    pass

def build_linux(lib_name, builder):
    ACTION='gmake'
    arch = builder.get_arch()
    builder.set_rootdir(path_join(xxxROOT, 'vendors', lib_name))
    
    # generate build scripts
    bx_root = os.path.abspath(path_join('../', 'bx'))
    genie_exe = path_join(bx_root, 'tools', 'bin', 'linux', 'genie')
    if not os.path.isfile(genie_exe):
        print("Could not find " + genie_exe)
        sys.exit(1)

    os.system("chmod +x " + genie_exe)
    builder.shell([genie_exe, '--gcc=linux-gcc', ACTION])

    # build
    if builder.build_debug():
        config = 'debug'
    else:
        config = 'release'

    if arch == vendor_build.arch_x64:
        bits = '64'
    elif vendor_build.arch_x86:
        bits = '32'

    # install lib
    build_dir = path_join('.build', 'projects', 'gmake-linux')
    os.chdir(build_dir)
    jobs = vendor_build.globals['default_parallel_jobs']
    builder.make_command(['config=%s%s' % (config, bits), 'verbose=1', \
                          '--jobs=%d' % jobs])
    os.chdir('../../../')

    lib_path = path_join('.build', 'linux%s_gcc' % bits, 'bin') 
    lib_path = path_join(lib_path, 'libbgfx%s.a' % config.title())
    builder.copy_lib_file(lib_path, xxxROOT)

    # install headers
    builder.copy_header_files('include', xxxROOT)

if __name__ == '__main__':
    lib_name = 'bgfx'
    cli = BuildCLI(sys.argv, lib_name)
    builder = BuildLib(cli)
    builder.verify_environment()

    xxxROOT = vendor_build.get_project_root_dir('{{ cookiecutter.project_prefix|upper }}')
    xxxBIN  = vendor_build.get_project_bin_dir('{{ cookiecutter.project_prefix|upper }}')
    
    try:
        if cli.get_target_platform() == 'Windows':
            build_windows(lib_name, builder)

        if cli.get_target_platform() == 'Darwin':
            build_macos(lib_name, builder)            

        if cli.get_target_platform() == 'Linux':
            build_linux(lib_name, builder)

    except vendor_build.BuildError as e:
        print("Failed building %s: %s" % (lib_name, e))
        sys.exit(1)

    print("Success.")
    sys.exit(0)
