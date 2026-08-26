{% test not_empty(model, column_name) %}

select *
from {{ model }}
where trim({{ column_name }}) = ''

{% endtest %}