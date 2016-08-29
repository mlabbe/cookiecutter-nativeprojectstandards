import os
import sys

# temp: until I ship it
sys.path.append("../../../../vendor_build/vendor_build")

import vendor_build
from vendor_build import BuildLib, BuildCLI
from os.path import join as path_join

{{ cookiecutter.project_prefix|upper }}ROOT = None
{{ cookiecutter.project_prefix|upper }}BIN  = None

def build_windows(lib_name, builder):
    arch = builder.get_arch()
    builder.set_rootdir(path_join({{ cookiecutter.project_prefix|upper }}ROOT, 'vendors', lib_name))

    sln_name = os.path.normpath("VisualC/SDL_VS2008.sln")
    builder.devenv_upgrade(sln_name)

    if builder.build_debug():
        config = 'Debug'
    else:
        config = 'Release'

    builder.devenv_build(sln_name, config, 'SDL2')
    builder.devenv_build(sln_name, config, 'SDL2main')

    if arch == vendor_build.arch_x64:
        arch_dir = 'x64'
    elif arch == vendor_build.arch_x86:
        arch_dir = 'win32'

    # install dll
    if {{ cookiecutter.project_prefix|upper }}BIN != None:
        dll_path = path_join('VisualC', arch_dir, config, 'SDL2.dll')
        builder.install_file_in_bin_dir(os.path.normpath(dll_path), {{ cookiecutter.project_prefix|upper }}BIN)

    # install header files and libary
    builder.copy_header_files('include', {{ cookiecutter.project_prefix|upper }}ROOT)

    lib_dir = path_join('VisualC', arch_dir, config)
    libsdl2_path     = path_join(lib_dir, 'SDL2.lib')
    libsdl2main_path = path_join(lib_dir, 'SDL2main.lib')
    builder.copy_lib_file(libsdl2_path, {{ cookiecutter.project_prefix|upper }}ROOT)
    builder.copy_lib_file(libsdl2main_path, {{ cookiecutter.project_prefix|upper }}ROOT)
        

if __name__ == '__main__':
    lib_name = 'SDL2'
    cli = BuildCLI(sys.argv, lib_name)
    builder = BuildLib(cli)
    builder.verify_environment()

    {{ cookiecutter.project_prefix|upper }}ROOT = vendor_build.get_project_root_dir('{{ cookiecutter.project_prefix|upper }}')
    {{ cookiecutter.project_prefix|upper }}BIN  = vendor_build.get_project_bin_dir('{{ cookiecutter.project_prefix|upper }}')
    print("project root dir: %s" % {{ cookiecutter.project_prefix|upper }}ROOT)
    
    try:
        if cli.get_target_platform() == 'Windows':
            build_windows(lib_name, builder)

    except vendor_build.BuildError as e:
        print("Failed building %s: %s" % (lib_name, e))
        sys.exit(1)

    print("Success.")
    sys.exit(0)
