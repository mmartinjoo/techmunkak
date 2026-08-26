{% macro slug(col_name) -%}
    regexp_replace(lower(btrim({{ col_name }})), '\W', '-', 1, 0, 'i')
{%- endmacro %}