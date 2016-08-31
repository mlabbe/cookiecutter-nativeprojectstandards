# {{ cookiecutter.project_name }} #

{% if cookiecutter.project_kind == "StaticLib" or cookiecutter.project_kind == "SharedLib" %}
# Example Usage

```C
#include <{{ cookiecutter.project_prefix }}.h>
```
{% endif %}

## Changelog ##

release | what's new                          | date
--------|-------------------------------------|---------
0.0.1   | initial                             | 

## Building ##

{% if cookiecutter.support_build == 'y' %}
{{ cookiecutter.project_name }} uses [Premake5](https://premake.github.io/download.html) generated Makefiles and IDE project files.  The generated project files are checked in under `build/` so you don't have to download and use Premake in most cases.
{% endif %}

# Copyright and Credit #

Copyright &copy; {{ cookiecutter.copyright_years }} {{ cookiecutter.copyright_holder }}. {% if cookiecutter.open_source_license == "Not open source" %}File [LICENSE](LICENSE) covers all files in this repo unless expressly noted.{% endif %}

{{ cookiecutter.project_name }} by {{ cookiecutter.author_name }}
<{{ cookiecutter.author_email }}> 
{% if cookiecutter.author_twitter|length > 0 %}[@{{ cookiecutter.author_twitter }}](https://www.twitter.com/{{ cookiecutter.author_twitter }}) {% endif %}

## Support ##

Directed support for this work is available from the original author under a paid agreement.

[Contact author]({{ cookiecutter.author_contact_url }})
