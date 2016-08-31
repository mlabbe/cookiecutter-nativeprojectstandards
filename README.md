# Project status #

WIP - don't use it yet

# Native Project Standards Generator #

This Cookiecutter generates a C/C++ project based on the [Native Project Standards](http://www.frogtoss.com/labs/pages/native-project-standards.html).  This includes standardized directories to support most projects.  It also uses Premake to pre-generate build scripts which can be distributed.  Because the generated Premake files can be distributed, they don't have to be run by your end users.  See [Premake For Package Maintainers](http://www.frogtoss.com/labs/premake-for-package-maintainers.html) for details on this low-interference strategy to cross platform project development.

It supports projects that contain static libraries, dynamic libraries and exes.  Post-generation, your project will build on Linux, Mac and Windows in 32-bit and 64-bit.  Because it uses Premake, it is possible to extend the project to other operating systems.

## Installation ##

Prior to installation, make sure [Premake5](https://premake.github.io/download.html) is in your path, as well as [Python](https://www.python.org).  These instructions work for any desktop operating system.

    # download and install the cookiecutter project templating system
    pip install cookiecutter

    # run cookiecutter
    cookiecutter https://github.com/mlabbe/cookiecutter-nativeprojectstandards

Cookiecutter will now ask you questions about your project including where to put it.

## Usage ##

The philosophy behind the Native Project Standards is that it supports standardized locations for everything in a build tree.  If you don't need something, you delete it.  If you need it, you put it where it says it should go.

## TODO ##

- improve generated readme.md, especially when it comes to building
- document
 - all of the build commands
 - supported configurations
 - how vendors works
- Add `/tools` to native project standards, comment on public header files for executable projects (they can be used for mods)

# Credits #

Native Project Standards by Michael Labbe
Copyright (C) 2016 Frogtoss Games, Inc.
[@frogtoss](https://www.twitter.com/frogtoss)
