{% macro slug(col_name) -%}
    regexp_replace(lower(btrim({{ col_name }})), '\W', '-', 1, 0, 'i')
{%- endmacro %}

{% macro dim_key(canonical_name, raw_value) -%}
    md5(lower(coalesce({{ canonical_name }}, {{ raw_value }})))
{%- endmacro %}