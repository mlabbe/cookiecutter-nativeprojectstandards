/*
 * {{ cookiecutter.project_name }} Copyright (C) {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}
 * 
 */
{% if cookiecutter.support_config %}
#include <{{ cookiecutter.project_prefix }}config.h>
{%- endif -%}
{% if cookiecutter.support_public_include %}
#include <{{ cookiecutter.project_prefix }}.h>
{%- endif -%}
{% if cookiecutter.project_kind == 'ConsoleApp' or cookiecutter.project_kind == 'WindowedApp' %}
#include <stdio.h>

int main(void) {
    puts("Welcome to {{ cookiecutter.project_name }}, a brand-new project by {{ cookiecutter.author_name }}.");
    return 0;
}
{% endif %}
