/*
 * {{ cookiecutter.project_name }} Copyright (C) {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}
 * 
 */

#pragma once

{% set etype_list = cookiecutter.execution_types.split(',') %}
{% for etype in etype_list %}
//
// {{ etype|title }}
//
#if defined({{ etype|upper }})
#endif
{% endfor %}
