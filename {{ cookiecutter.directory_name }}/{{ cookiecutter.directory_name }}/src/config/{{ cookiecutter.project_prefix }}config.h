/*
 * {{ cookiecutter.project_name }} Copyright (C) {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}
 * 
 */

#pragma once

{% set etype_list = cookiecutter.execution_types.split(',') %}

{%- if "debug" in etype_list %}
//
// Debug
//
#if defined(DEBUG)
#    define CONFIG_DEFINES_SET 1
#endif
{% endif %}

{%- if "final" in etype_list %}
//
// Release
//
#if defined(NDEBUG) && !FINAL_RELEASE
#    define CONFIG_DEFINES_SET 1
#endif

//
// Final
//
#if defined(NDEBUG) && FINAL_RELEASE
#    define CONFIG_DEFINES_SET 1
#endif
{% else %}
//
// Release
//
#if defined(NDEBUG)
#    define CONFIG_DEFINES_SET 1
#endif
{% endif %}

{% for etype in etype_list %}
//
// {{ etype|title }}
//
#if defined({{ etype|upper }})
#    define CONFIG_DEFINES_SET 1
#endif
{% endfor %}


#if CONFIG_DEFINES_SET != 1
#    error Build type (DEBUG, NDEBUG, FINAL_RELEASE, ...) must be defined at compile time.
#endif
