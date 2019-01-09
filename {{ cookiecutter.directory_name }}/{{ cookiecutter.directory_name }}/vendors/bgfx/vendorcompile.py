import os
import sys

sys.path.append("../../tools/pylib")
import vendor_build
from vendor_build import BuildLib, BuildCLI
from os.path import join as path_join

xxxROOT = None
xxxBIN  = None


def run_genie(with_args, compiler):
    # generate build scripts
    bx_root = os.path.abspath(path_join('../', 'bx'))
    genie_exe = path_join(bx_root, 'tools', 'bin', 'windows', 'genie.exe')
    if not os.path.isfile(genie_exe):
        print("Could not find " + genie_exe)

    builder.shell([genie_exe] + with_args + [compiler])
    

def build_windows(lib_name, builder):
    COMPILER='vs2017'  # presumably this can be others
    arch = builder.get_arch()
    builder.set_rootdir(path_join(xxxROOT, 'vendors', lib_name))

    run_genie(['--with-tools'], COMPILER)

    builder.shell([genie_exe, COMPILER])

    # build
    if builder.build_debug():
        config = 'Debug'
    else:
        config = 'Release'
    
    build_dir = path_join('.build', 'projects', COMPILER)
    os.chdir(build_dir)
    # build all projects in generated sln
    builder.devenv_build('bgfx.sln', config, project=None)

	
    os.chdir('../../../')    
    
    # install lib
    if arch == vendor_build.arch_x64:
        arch_dir = 'win64_' + COMPILER
    elif arch == vendor_build.arch_x86:
        arch_dir = 'win32_' + COMPILER
        
    lib_path = path_join('.build', arch_dir, 'bin')
    for lib_name in ('bgfx', 'bx', 'bimg'):
        lib_filename = lib_name + config
        builder.copy_lib_file(path_join(lib_path, lib_filename+'.lib'), xxxROOT)
        builder.copy_lib_file(path_join(lib_path, lib_filename+'.pdb'), xxxROOT)

    # install headers
    builder.copy_header_files('include', xxxROOT)
    builder.copy_header_files('../bx/include', xxxROOT)
    builder.copy_header_files('../bimg/include', xxxROOT)

    # install binaries
    bin_dir = path_join('.build', arch_dir, 'bin')
    for bin_file in ('shaderc', 'texturec', 'texturev', 'geometryc'):
        bin_file = bin_file + config
        for ext in ('pdb', 'exe'):
            actual_bin_file = bin_file + '.' + ext
            builder.copy_bin_file(path_join(bin_dir, actual_bin_file), xxxROOT)            
 	# re-run genie with examples in case this is a developer machine build
    # and the developer wants to run examples.  Don't build them, though.
    run_genie(['--with-tools', '--with-examples'], COMPILER)

    
def build_macos(libname, builder):
    ACTION='gmake'
    arch = builder.get_arch()
    builder.set_rootdir(path_join(xxxROOT, 'vendors', lib_name))

    # generate build scripts    
    bx_root = os.path.abspath(path_join('../', 'bx'))
    genie_exe = path_join(bx_root, 'tools', 'bin', 'darwin', 'genie')
    if not os.path.isfile(genie_exe):
        print("Could not find " + genie_exe)
        sys.exit(1)

    os.system("chmod +x " + genie_exe)
    builder.shell([genie_exe, '--gcc=osx', ACTION])

    # build
    if builder.build_debug():
        config = 'debug'
    else:
        config = 'release'

    if arch == vendor_build.arch_x64:
        bits = '64'
    elif arch == vendor_build.arch_x86:
        bits = '32'
    
    # fixme: this is where fat binary support would go if there was fat binary support
    
    # install lib
    build_dir = path_join('.build', 'projects', 'gmake-osx')
    os.chdir(build_dir)
    jobs = vendor_build.globals['default_parallel_jobs']
    builder.make_command(['config=%s%s' % (config, bits), 'verbose=1', \
                          '--jobs=%d' % jobs])

    os.chdir("../../../")

    lib_path = path_join('.build', 'osx%s_clang' % bits, 'bin')
    lib_path = path_join(lib_path, 'libbgfx%s.a' % config.title())
    builder.copy_lib_file(lib_path, xxxROOT)

    # install headers
    builder.copy_header_files('include', xxxROOT)

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
