#!/usr/bin/env python3

import os
import re
import sys
import platform
import subprocess

from os.path import join as path_join

ARG_TABLE = {'--skip-premake': 'rely on already-existing result of genie/premake dist command',
             '--quiet': 'remove log lines, exclusively emit errors and subprocess output',
             '--skip-vendors': "don't compile vendors",
             '--skip': "skip both vendors and premake",
             '--help': 'this text'}

def which(exe_name):
    is_windows = platform.system() == 'Windows'
    if is_windows:
        exe_name += '.exe'

    if not 'PATH' in os.environ:
        return None

    for path in os.environ['PATH'].split(os.pathsep):        
        exe_path = path_join(path, exe_name)
        if is_windows:
            exe_path = exe_path.lower()
        
        if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):            
            return exe_path
        
    return None


def find_arg_0param(expected_arg):
    for arg in sys.argv:
        if arg == expected_arg:
            return True

    return False

def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def message(msg):
    if not find_arg_0param('--quiet'):
        print(msg)

def get_project_root():
    return os.path.split(os.path.realpath(__file__))[0]

def shell(cmd):
    if not find_arg_0param('--quiet'):
        print(' '.join(cmd))
    cp = subprocess.run(cmd)

    if cp.returncode != 0:
        fatal("%s failed" % ' '.join(cmd))

def compile_vendors(project_root):
    vendor_dir = path_join(project_root, 'vendors')

    if (find_arg_0param('--skip-vendors')): return
    if (find_arg_0param('--skip')): return
    if not os.path.isdir(vendor_dir): return

    os.chdir(vendor_dir)

    python_bin = 'python3'
    if platform.system() == 'Windows':
        python_bin = 'python.exe'


    shell([python_bin, 'compile_all_vendors.py'])

    os.chdir(project_root)

def is_vcvars_setup():
    return platform.system() == 'Windows' and 'VisualStudioVersion' in os.environ


def is_genie(premake_filename):
    return premake_filename == 'genie.lua'


def strip_args():
    args = []

    for arg in sys.argv:
        if arg in ARG_TABLE:
            continue
        args.append(arg)

    args.pop(0)
    return args

def get_darwin_arch():
    return subprocess.getoutput('uname -p')


def print_help():
    if not find_arg_0param('--help'):
        return

    print("usage: %s [optional arguments]" % sys.argv[0])
    for arg in sorted(ARG_TABLE):
        print("\t%s: %s" % (arg, ARG_TABLE[arg]))

    print("""
    The purpose of this script is to build the codebase in common
    and default ways without interacting with the user.  It is useful
    for quick in-editor rebuilds, where it examines the host system
    and environment to build as requested.

    =GENie builds=
    To use Visual Studio on Windows, run vcvars.  Otherwise, Clang
    may be attempted.

    While clang builds are used on Windows, vendors may not be
    clang-compatible.  Build vendors manually with msvc, then run
    this script with --skip-vendors from then on out.

    =Premake builds=
    Makefiles on all platforms except Windows, where Visual Studio
    is required.

    =Visual Studio Version Selector=
    If vcvars is installed, a corresponding vs#### directory is 
    attempted.  If one doesn't exist, the newest vs version is used.
    To avoid this behaviour, simply run Premake or GENie to generate
    a matching VS version.

    =Passing Arguments to Ninja, Make=
    All program arguments that do not match what is listed above are
    passed verbatim to make or ninja.

    For example:
    ./make.py -t clean                          # If building with ninja, 
                                                # this cleans

    ./make.py config=release_x64 --skip-vendors # Makefile now building release, 
                                                # skipping vendor building which
                                                # is a make.py argument
    """)

    sys.exit(0)


# build/ or build_experimental
def get_premake_subdir(project_root_dir):
    build_normal = path_join(project_root_dir, 'build')
    build_experimental = path_join(project_root_dir, 'build_experimental')

    if os.path.isdir(build_experimental):
        return build_experimental
    
    if os.path.isdir(build_normal):
        return build_normal
    
    fatal("Could not find build subdir under %s" % project_root_dir)


# premake5.lua or genie.lua
def get_premake_filename(premake_subdir):
    options = ('genie.lua', 'premake5.lua')

    for option in options:
        
        option_path = path_join(premake_subdir, option)
        
        if os.path.exists(option_path):
            return option
    
    fatal("Could not find premake or genie under %s" % premake_subdir)


# runs premake or GENie
def run_premake(build_subdir, premake_filename):
    if find_arg_0param('--skip-premake'):
        return

    if find_arg_0param('--skip'):
        return

    if premake_filename == 'premake5.lua':
        premake_exe = 'premake5'
    else:
        premake_exe = 'genie'

    shell([premake_exe, 'dist'])

    os.chdir(premake_subdir)


# scan for vs* subdirs, returning the highest one
def get_highest_vs_version():
    vs_dir_matcher = re.compile('^vs(\d+)')

    highest_version = 0

    # assumes already in build subdir
    for path in os.listdir('.'):
        if not os.path.isdir(path):
            continue

        result = vs_dir_matcher.match(path)
        if result == None:
            continue

        version_number = int(result.group(1))
        if version_number > highest_version:
            highest_version = version_number
        
    if version_number == 0:
        fatal("no visual studio versions found")

    return "vs%d" % version_number

# find a match for the vcvars installed and the vs build dir
# failing that, just return the highest vc version
def get_vs_version():
    VS_VERSION_LOOKUP = {
        '8.0': 'vs2005',
        '9.0': 'vs2008',
        '10.0': 'vs2010',
        '11.0': 'vs2012',
        '12.0': 'vs2013',
        '14.0': 'vs2015',
        '15.0': 'vs2017',
        '16.0': 'vs2019',
        '17.0': 'vs2022'  # check this when it comes out
    }

    if not 'VisualStudioVersion' in os.environ:
        fatal("no vcvars found")

    version_number = os.environ['VisualStudioVersion']

    # if there is a perfect match, just return that
    if version_number in VS_VERSION_LOOKUP:

        version_name = VS_VERSION_LOOKUP[version_number]

        if os.path.isdir(version_name):
            message("building with %s" % version_name)
            return version_name

    # otherwise, just return the highest version
    version_name = get_highest_vs_version()
    message("vcvars tools are from version %s, but building from directory %s" % \
        (VS_VERSION_LOOKUP[version_number], version_name))
    return version_name




# seek out the build subdirectory
def find_build_subdir(premake_filename, premake_subdir):

    system = platform.system().lower()

    build_subdir = ''
    if not is_genie(premake_filename):
        # premake5 case

        if system == 'linux' or 'bsd' in system:
            build_subdir = 'gmake_linux'

        elif system == 'darwin':
            build_subdir = 'gmake_macosx'

        elif system == 'windows':
            if is_vcvars_setup():
                build_subdir = get_vs_version()
            else:
                fatal('re-run after setting visual studio environment variables')

    else:
        # GENie case

        if system == 'linux' or 'bsd' in system:
            build_subdir = 'ninja_linux'

        elif system == 'darwin':
            arch = get_darwin_arch()
            if arch == 'arm':
                build_subdir = 'ninja_macos-arm64'
            else:
                build_subdir = 'ninja_macos-x86_64'        

        elif system == 'windows':
            if is_vcvars_setup():
                build_subdir = get_vs_version()
            else:
                build_subdir = 'ninja_windows'

        
    if len(build_subdir) == 0:
        fatal("No fitting build subdir found for os and build environment. Run premake manually.")

    return build_subdir

def vsbuild():
    
    # find the name of the sln in this folder
    sln_file = ''
    for file in os.listdir('.'):
        if os.path.isfile(file) and os.path.splitext(file.lower())[1] == '.sln':
            sln_file = file
            break
    
    if len(sln_file) == 0:
        fatal("could not find .sln file to build")

    cmd = ['msbuild.exe', sln_file]


    args = strip_args()

    # we break from not adding additional args to
    # msbuild/make/ninja/etc here to default to 64-bit platform on msbuild.
    if 'VSCMD_ARG_TGT_ARCH' in os.environ and os.environ['VSCMD_ARG_TGT_ARCH'] == 'x64':
        if not '/p:Platform=x64' in args and not '/p:Platform=x86' in args:
            print("Forcing x64 arch in sln build")

            args.append('/p:Platform=x64')


    cmd.extend(args)

    shell(cmd)


def make():
    cmd = ['make']

    args = strip_args()
    cmd.extend(args)

    shell(cmd)
    

def ninja():
    subdirs = ['debug', 'release', 
            'debug64', 'release64',
            'debug32', 'release32']

    build_subdirs = []

    for subdir in subdirs:
        if find_arg_0param(subdir):
            build_subdirs.append(subdir)

    if len(build_subdirs) == 0:
        message('no build subdirs specified -- building debug64')
        build_subdirs.append('debug64')

    for build_subdir in build_subdirs:
        os.chdir(build_subdir)
        cmd = ['ninja']
    
        # hack: take full command line args, then further strip
        # the build subdirs
        args_full = strip_args()
        args = []
        for arg in args_full:
            if not arg in subdirs:
                args.append(arg)

        cmd.extend(args)
        
        shell(cmd)
        os.chdir('..')


def check_dependencies(premake_filename):
    deps = []
    
    if is_genie(premake_filename):
        deps.append('genie')
        deps.append('ninja')
    else:
        deps.append('premake5')
        
    errors = []
    for dep in deps:
        if which(dep) == None:
            errors.append(dep)

    if len(errors) == 0:
        return

    print("dependent programs not found in PATH:", file=sys.stderr)
    for error in errors:
        print(" - %s" % error)
    
    fatal("place dependent programs in PATH to continue")

    
#
# main
#

print_help()

project_root_dir = get_project_root()

premake_subdir = get_premake_subdir(project_root_dir)
premake_filename = get_premake_filename(premake_subdir)

check_dependencies(premake_filename)

compile_vendors(project_root_dir)

os.chdir(premake_subdir)
run_premake(premake_subdir, premake_filename)

build_subdir = find_build_subdir(premake_filename, premake_subdir)
message("build subdir: " + build_subdir)

os.chdir(build_subdir)

if not is_genie(premake_filename):
    # premake case
    if platform.system() == 'Windows':
        vsbuild()

    else:
        make()

else:
    # GENie case
    if is_vcvars_setup():
        vsbuild()
    else:
        ninja()

sys.exit(0)
