import os
import sys
import subprocess

sys.path.append('../tools/pylib')
import vendor_build
    
vendors = [
{% if cookiecutter.uselib_sdl2 == 'y' -%}
    'SDL2',
{%- endif %}
{% if cookiecutter.uselib_bgfx == 'y' -%}
    'bgfx',
{%- endif %}
{% if cookiecutter.uselib_glew == 'y' -%}
    'glew',
{%- endif %}
{% if cookiecutter.uselib_lua53 == 'y' -%}
    'lua53',
{%- endif %}
]

def compile_vendor( vendor, cli ):
    os.chdir( vendor )

    cmd = [ sys.executable,     'vendorcompile.py', 
            '--platform', cli.get_target_platform(), 
            '--action',   'build', 
            '--arch',     'x64' if cli.options.arch is None else cli.options.arch ]

    if cli.options.clean:
        cmd.append( '--clean-first' )

    if cli.options.ccache:
        cmd.append( '--use-ccache' )

    if cli.options.force_clang:
        cmd.append( '--force-clang' )

    if cli.options.debug:
        cmd.append( '--debug=1')

    print(' '.join( cmd ))

    try:
        subprocess.check_call( ' '.join(cmd), shell=True )
    except subprocess.CalledProcessError as e:
        raise vendor_build.BuildError( 'compile_vendor( %s ) returned %i ' % 
                                    (vendor, e.returncode ) )
    os.chdir('..')


if __name__ == '__main__':
    cli = vendor_build.BuildCLI( sys.argv, 'all vendor libs' )

    try:
        for vendor in vendors:
            compile_vendor(vendor, cli)
    except vendor_build.BuildError as e:
        print("%s failed building: %s: %s" % (sys.argv[0], vendor, e))
        sys.exit(1)
