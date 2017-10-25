#!/usr/bin/env python3

import os
import sys

sys.path.append("../../tools/pylib")
import vendor_build
from vendor_build import BuildLib, BuildCLI
from os.path import join as path_join

xxxROOT = None
xxxBIN  = None

PUBHEADERS = ['lua.h', 'luaconf.h', 'lauxlib.h', 'lualib.h', 'lua.hpp']

def _win32_clean(builder):
    builder.shell(['rm', '*.o'], check_errorlevel=False)
    builder.shell(['rm', '*.obj'], check_errorlevel=False)
    builder.shell(['rm', 'lua.exe'], check_errorlevel=False)
    builder.shell(['rm', 'lua530.lib'], check_errorlevel=False)
    builder.shell(['rm', 'lua_d.exe'], check_errorlevel=False)
    builder.shell(['rm', 'lua530_d.lib'], check_errorlevel=False)


def build_windows(lib_name, builder):
    os.chdir('src')
    
    # no makefile for visual studio, so just build a static library by
    # running vc++ commands directly
    _win32_clean(builder)

    lib_filename = None
    if builder.build_debug():
        lib_filename = 'lua530_d.lib'
        builder.shell(['cl', '/MD', '/Od', '/c', '*.c'])
        builder.shell(['ren', 'lua.obj', 'lua.o'])
        builder.shell(['ren', 'luac.obj', 'luac.o'])
        builder.shell(['lib', '/OUT:'+lib_filename, '*.obj'])
        builder.shell(['link', '/OUT:lua_d.exe', 'lua.o', lib_filename])
    else:
        lib_filename = 'lua530.lib'
        builder.shell(['cl', '/MD', '/O2', '/c', '*.c'])
        builder.shell(['ren', 'lua.obj', 'lua.o'])
        builder.shell(['ren', 'luac.obj', 'luac.o'])
        builder.shell(['lib', '/OUT:'+lib_filename, '*.obj'])
        builder.shell(['link', '/OUT:lua.exe', 'lua.o', lib_filename])

    include_path = path_join(xxxROOT, 'vendors', 'include')
    builder.mkdir(include_path)

    # only copy the public header files
    for header_file in PUBHEADERS:
        builder.shell(['copy', header_file, include_path])

    builder.copy_lib_file(lib_filename, xxxROOT)

# platform arg is the Lua Makefile platform name
def build_linux_or_macos(lib_name, builder, platform):
    # todo: support debug.
    # patch the src/makefile to commet out MYCFLAGS
    
    builder.set_rootdir(path_join(xxxROOT, 'vendors', lib_name))
    builder.set_arch_environment(xxxROOT)
    
    builder.make_optional_clean()
    builder.make_command(platform)

    include_path = path_join(xxxROOT, 'vendors', 'include')
    builder.mkdir(include_path)
    
    for header_file in PUBHEADERS:
        builder.shell(['cp',
                       path_join('src', header_file),
                       include_path])
        
    builder.copy_lib_file(path_join('src', 'liblua.a'), xxxROOT)

if __name__ == '__main__':
    lib_name = 'lua53'
    cli = BuildCLI(sys.argv, lib_name)
    builder = BuildLib(cli)
    builder.verify_environment()

    xxxROOT = vendor_build.get_project_root_dir('{{ cookiecutter.project_prefix|upper }}')
    xxxBIN  = vendor_build.get_project_bin_dir('{{ cookiecutter.project_prefix|upper }}')
    
    try:
        if cli.get_target_platform() == 'Windows':
            build_windows(lib_name, builder)

        if cli.get_target_platform() == 'Darwin':
            build_linux_or_macos(lib_name, builder, 'macosx')

        if cli.get_target_platform() == 'Linux':
            build_linux_or_macos(lib_name, builder, 'linux')

    except vendor_build.BuildError as e:
        print("Failed building %s: %s" % (lib_name, e))
        sys.exit(1)

    print("Success.")
    sys.exit(0)
