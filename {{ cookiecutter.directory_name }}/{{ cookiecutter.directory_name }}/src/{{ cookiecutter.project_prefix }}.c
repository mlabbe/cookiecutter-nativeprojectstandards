/*
 * {{ cookiecutter.project_name }} Copyright (C) {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}
 * 
 */
{% if cookiecutter.support_config == 'y' %}
#include "{{ cookiecutter.project_prefix }}config.h"
{%- endif -%}
{% if cookiecutter.support_public_include == 'y' %}
#include "{{ cookiecutter.project_prefix }}.h"
{%- endif -%}
{% if cookiecutter.uselib_sdl2 == 'y' %}
#include <stdlib.h> /* for atexit() */
#include <SDL.h>
{%- endif -%}

{% if cookiecutter.project_kind == 'ConsoleApp' or cookiecutter.project_kind == 'WindowedApp' %}
#include <stdio.h>


int main(int argc, char *argv[]) {
    puts("Welcome to {{ cookiecutter.project_name }}, a brand-new project by {{ cookiecutter.author_name }}.");

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
    return 0;
}
{% endif %}
