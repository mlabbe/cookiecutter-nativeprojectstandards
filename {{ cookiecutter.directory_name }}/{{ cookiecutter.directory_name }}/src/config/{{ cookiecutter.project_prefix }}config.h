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
#endif
{% endif %}

{%- if "final" in etype_list %}
//
// Release
//
#if defined(NDEBUG) && !FINAL_RELEASE
#endif

//
// Final
//
#if defined(NDEBUG) && FINAL_RELEASE
#endif
{% else %}
//
// Release
//
#if defined(NDEBUG)
#endif
{% endif %}

{% for etype in etype_list %}
//
// {{ etype|title }}
//
#if defined({{ etype|upper }})
#endif
{% endfor %}
