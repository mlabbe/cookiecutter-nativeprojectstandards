-- {{ cookiecutter.project_name }} premake5 script
--
-- This can be ran directly, but commonly, it is only run
-- by package maintainers.
-- See http://www.frogtoss.com/labs/premake-for-package-maintainers.html
--
-- IMPORTANT NOTE: premake5 alpha 9 does not handle this script
-- properly.  Build premake5 from Github master, or, presumably,
-- use alpha 10 in the future.

{% set x86_count = cookiecutter.windows_x86.split(',')|length + cookiecutter.linux_x86.split(',')|length -%}
{% set x64_count = cookiecutter.windows_x64.split(',')|length + cookiecutter.linux_x64.split(',')|length -%}
{% set etype_list = cookiecutter.execution_types.split(',') -%}
{% set macos_list = cookiecutter.macos.split(',') -%}
{% set windows_x86_list = cookiecutter.windows_x86.split(',') -%}
{% set windows_x64_list = cookiecutter.windows_x64.split(',') -%}
{% if cookiecutter.main_language == 'c89' or cookiecutter.main_language == 'c99' -%}
  {% set lang_ext = 'c' -%}
{% elif cookiecutter.main_language == 'c++' -%}
  {% set lang_ext = 'cpp' -%}
{% endif -%}
{% if cookiecutter.project_kind == "StaticLib" or cookiecutter.project_kind == "SharedLib" %}
 {% set out_dir = "lib" %}
{% else %}
 {% set out_dir = "bin" %}
{% endif -%}
  
workspace "{{ cookiecutter.project_name|title }}"
  -- these dir specifications assume the generated files have been moved
  -- into a subdirectory.  ex: <root>/build/makefile
  local root_dir = path.join(path.getdirectory(_SCRIPT),"../../")
  local build_dir = path.join(path.getdirectory(_SCRIPT))
  configurations { {% for etype in etype_list -%}
   "{{ etype|title }}"{% if not loop.last %}, {% endif %}
  {%- endfor %} }

  {% if x64_count > 0 %}
  platforms { "x64" }
  {% endif %}
  {% if x86_count > 0 %}
  filter "not system:macosx"
    platforms { "x86" }  
  {% endif %}
  
  objdir(path.join(build_dir, "obj/"))

  -- architecture filters
  {% if x86_count > 0 %}
  filter "configurations:x86"
    architecture "x86"
  {%- endif %}
  {% if x64_count > 0 %}
  filter "configurations:x64"
    architecture "x86_64"
  {%- endif %}

  -- execution type filters
  --
  -- DEBUG | RELEASE | FINAL_RELEASE are the three canonical build types, but support
  -- other popular macros as well. Consider:
  -- 
  --  * DEBUG builds have cross-comp unit debug behaviors (low perf)
  --  * RELEASE builds are built with optimization but can have debug/logging hooks built in.
  --  * FINAL_RELEASE builds *are also release builds*, but are very hard to debug
  --
  --  No explicit support for profile builds yet. Proper profiling should happen in FINAL_RELEASE.
  {%- if "debug" in etype_list %}
  filter "configurations:Debug"
    defines {"DEBUG", "_DEBUG", "FINAL_RELEASE=0"}
    symbols "On"
    targetsuffix "_d"
  {% endif %}
  {%- if "release" in etype_list %}
  filter "configurations:Release"
    defines {"NDEBUG", "RELEASE", "FINAL_RELEASE=0"}
    optimize "On"
  {% endif %}
  {%- if "final" in etype_list %}
  filter "configurations:Final"   
    defines {"NDEBUG", "RELEASE", "FINAL_RELEASE=1"}
    optimize "On"
  {% endif %}
   
  project "{{ cookiecutter.directory_name }}"
    kind "{{ cookiecutter.project_kind }}"

    files {root_dir.."src/**.h",
           root_dir.."src/**.{{ lang_ext }}",
{% if cookiecutter.support_config == 'y' %}           root_dir.."src/config/{{ cookiecutter.project_prefix }}config.h",{% endif %}
 {% if cookiecutter.support_public_include == 'y' %}           root_dir.."include/*.h",{% endif %}
           root_dir.."src/3rdparty/*.{{ lang_ext }}",
           root_dir.."src/3rdparty/*.h",
    }

    includedirs {
{% if cookiecutter.support_config == 'y' %}       root_dir.."src/config/",{% endif %}
 {% if cookiecutter.support_public_include == 'y' %}       root_dir.."include/",{% endif %}
  root_dir.."/src/3rdparty",
    }

{% if cookiecutter.support_vendors == 'y' %}
    sysincludedirs {
       root_dir.."vendors/include",        
    }
{% endif %}


    filter "system:linux or system:macosx"
{%- if cookiecutter.main_language == 'c89' %}
      buildoptions {"--std=gnu90"}
{% elif cookiecutter.main_language == 'c99' %}
      buildoptions {"--std=gnu99"}
{% elif cookiecutter.main_language == 'c++' %}
      buildoptions {"--std=c++11"}
{% endif %}
    -- features: off by default, turn them on and regenerate
    -- if you need them
    filter{}
    warnings "Extra"
    rtti("off")
    exceptionhandling("off")
    filter "action:vs*"
      defines {"_CRT_SECURE_NO_WARNINGS"}
      fatalwarnings {"4715"} -- not all control paths return a value
      
{% if cookiecutter.support_vendors == 'y' %}
    filter("architecture:x86", "system:not macosx") 
      libdirs(root_dir.."vendors/lib/x86")

    filter("architecture:x86_64", "system:not macosx")      
      libdirs(root_dir.."vendors/lib/x64")

    filter "system:macosx"
      libdirs(root_dir.."vendors/lib")
      
{% if cookiecutter.uselib_sdl2 == 'y' %}
    -- libSDL2 linking
    filter{}
      links {'SDL2'}
    filter "system:linux"
      links {"GL", "dl", "pthread", "sndio"}
    filter "system:windows"
      links {"SDL2main"}
    filter "system:macosx"
      links {"AudioToolbox.framework",
             "AudioUnit.framework",
             "CoreAudio.framework",
             "IOKit.framework",
             "Carbon.framework",
             "Cocoa.framework",
             "CoreVideo.framework",
             "ForceFeedback.framework",
             "OpenGL.framework",
             "iconv"}
{% endif %}

{% if cookiecutter.uselib_bgfx == 'y' %}
    -- bgfx linking
    filter {}
      links {'bgfxRelease', 'bxRelease', 'bimgRelease'}
    filter "system:linux"
      links {'GL', 'X11'}
    filter("architecture:x86", "system:windows") 
      links {'psapi'}
    filter "system:macosx"
      links {'Cocoa.framework',
             'QuartzCore.framework',
             'OpenGL.framework'}
      linkoptions { "-weak_framework Metal" } -- bug: this is separating on whitespace
{% endif %}

{% if cookiecutter.uselib_glew == 'y' %}
    -- glew linking.
    -- append 'd' and regenerate premake to link debug glew
    filter {"not system:windows"}
      links {'GLEW'}
    filter {"system:linux"}
      links {'GL'}
    filter "system:windows"
      links {'opengl32'}
      defines {'GLEW_STATIC'}
      links {'glew32s'}
{% endif %}      

{% if cookiecutter.uselib_lua53 == 'y' %}
    -- lua linking
    -- append '_d' and regenerate premake to link debug lua
     filter {}
       links {'lua'}     
{% endif %}

{%- endif %}

-- cwd for debug execution is relative to installed DLL
-- directory.
{%- if cookiecutter.has_dist_dir == 'y' %}

   filter "toolset:msc"
      -- note that release and final exes overwrite each other with this scheme. 
      targetdir(root_dir..'../{{ cookiecutter.directory_name }}_dist/bin/win32_$(PlatformTarget)')
      debugdir(root_dir..'../{{ cookiecutter.directory_name }}_dist/bin/win32_$(PlatformTarget)')

{% else %}

    filter "toolset:msc"
      debugdir(root_dir.."../bin/$(Configuration)/win32_$(PlatformTarget)")
      targetdir(root_dir.."../bin/$(Configuration)/win32_$(PlatformTarget)")

{% endif %}

newaction
{
   trigger = "dist",
   description = "Create distributable premake dirs (maintainer only)",
   execute = function()


      -- special denotes the action *and* os_str make up the dir name
      -- needed when an action alone is ambiguous (ex: gmake runs on multiple OSes)
      local premake_do_action = function(action,os_str,special)
         local premake_dir
         if special then
            premake_dir = "./"..action.."_"..os_str
         else
            premake_dir = "./"..action
         end
         local premake_path = premake_dir.."/premake5.lua"

         os.mkdir(premake_dir)
         os.execute("cp premake5.lua "..premake_dir)
         os.execute("premake5 --os="..os_str.." --file="..premake_path.." "..action)
         os.execute("rm "..premake_path)
      end

{% for proj in windows_x86_list if not proj == 'mingw' and not proj in windows_x64_list %}
      premake_do_action("{{ proj }}", "windows", false)  
{% endfor -%} 
{% for proj in windows_x64_list if not proj == 'mingw' %}
      premake_do_action("{{ proj }}", "windows", false)  
{%- endfor -%} 
{% if 'xcode4' in macos_list %}
      premake_do_action("xcode4", "macosx", false)
{%- endif -%}
{% if cookiecutter.linux_x64|length > 0 or cookiecutter.linux_x86|length > 0 %}      
      premake_do_action("gmake", "linux", true)
{%- endif -%}
{% if 'clang' in macos_list %}      
      premake_do_action("gmake", "macosx", true)
{%- endif -%}
{% if 'mingw' in windows_x64_list or 'mingw' in windows_x86_list %}
      premake_do_action("gmake", "windows", true)
{%- endif %} 
   end
}

-- currently there is no premake5 clean action, so this will have to suffice
-- this deletes the premake5 --action=dist generated subdirectories
newaction
{
    trigger     = "clean",
    description = "Clean all build files and output",
    execute = function ()

        files_to_delete = 
        {
            "Makefile",
            "*.make",
            "*.txt",
            "*.7z",
            "*.zip",
            "*.tar.gz",
            "*.db",
            "*.opendb",
            "*.vcproj",
            "*.vcxproj",
            "*.vcxproj.user",
            "*.vcxproj.filters",
            "*.sln",
            "*~*"
        }

        directories_to_delete = 
        {
            "obj",
            "ipch",
            "bin",
            ".vs",
            "Debug",
            "Release",
            "release",
            "lib",
            "test",
            "makefiles",
            "gmake",
            "vs2010",
            "xcode4",
            "gmake_linux",
            "gmake_macosx",
            "gmake_windows"
        }

        for i,v in ipairs( directories_to_delete ) do
          os.rmdir( v )
        end

        if os.is "macosx" then
           os.execute("rm -rf *.xcodeproj")
           os.execute("rm -rf *.xcworkspace")
        end

        if not os.is "windows" then
            os.execute "find . -name .DS_Store -delete"
            for i,v in ipairs( files_to_delete ) do
              os.execute( "rm -f " .. v )
            end
        else
            for i,v in ipairs( files_to_delete ) do
              os.execute( "del /F /Q  " .. v )
            end
        end

    end
}
