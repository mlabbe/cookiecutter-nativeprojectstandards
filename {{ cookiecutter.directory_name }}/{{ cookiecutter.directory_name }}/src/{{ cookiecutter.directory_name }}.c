/*
 * {{ cookiecutter.project_name }} Copyright (C) {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}
 * 
 */
{% if cookiecutter.support_config == 'y' %}
#include "{{ cookiecutter.project_prefix }}config.h"
{%- endif -%}
{% if cookiecutter.support_public_include == 'y' %}
#include "{{ cookiecutter.directory_name }}.h" /* public header */
{%- endif -%}
{% if cookiecutter.uselib_sdl2 == 'y' %}
#include <stdlib.h> /* for atexit() */
#include <SDL.h>
{%- endif -%}
{% if cookiecutter.uselib_bgfx == 'y' %}
#include <bgfx/c99/bgfx.h>
{%- endif -%}
{% if cookiecutter.uselib_glew == 'y' %}
#include <GL/glew.h>
{%- endif -%}
{% if cookiecutter.uselib_lua53 == 'y' %}
#include <lua.h>
#include <lualib.h>
#include <lauxlib.h>
{%- endif -%}

{% if cookiecutter.project_kind == 'ConsoleApp' or cookiecutter.project_kind == 'WindowedApp' %}
#include <stdio.h>


int main(int argc, char *argv[]) {
    puts("Welcome to {{ cookiecutter.project_name }}, a brand-new project by {{ cookiecutter.author_name }}.");

{% if cookiecutter.uselib_lua53 == 'y' %}
    lua_State *L = luaL_newstate();
{%- endif %}

{% if cookiecutter.uselib_sdl2 == 'y' %}
    if (SDL_Init(SDL_INIT_VIDEO|SDL_INIT_TIMER) != 0) {
        fprintf(stderr,
                "\nUnable to initialize SDL:  %s\n",
                SDL_GetError()
               );
        return 1;
    }
    atexit(SDL_Quit);    
{%- endif %}

{% if cookiecutter.uselib_glew == 'y' %}
  GLenum err = glewInit();
  if (GLEW_OK != err)
  {
      fprintf(stderr, "Error: %s\n", glewGetErrorString(err));
  }
  fprintf(stdout, "Status: Using GLEW %s\n", glewGetString(GLEW_VERSION));  
{% endif %} 

{% if cookiecutter.uselib_bgfx == 'y' %}
	bgfx_init(BGFX_RENDERER_TYPE_COUNT
			, BGFX_PCI_ID_NONE
			, 0
			, NULL
			, NULL);
{%- endif %}   

{% if cookiecutter.uselib_lua53 == 'y' %}
    lua_close(L);
{%- endif %}
 
    return 0;
}
{% endif %}
