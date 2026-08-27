create table if not exists bronze.currency_conversions(
    id serial primary key,
    from_currency_code varchar(3) not null,
    to_currency_code varchar(3) not null,
    value numeric(5, 2) not null
);

create unique index from_to_unique on bronze.currency_conversions (from_currency_code, to_currency_code);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('EUR', 'EUR', 1.00);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('PLN', 'EUR', 4.33);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('GBP', 'EUR', 0.86);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('HUF', 'EUR', 364.00);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('CZK', 'EUR', 15.08);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('BGN', 'EUR', 1.94);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('DKK', 'EUR', 7.47);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('RON', 'EUR', 5.26);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('SEK', 'EUR', 11.08);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('CHF', 'EUR', 0.94);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('NOK', 'EUR', 10.88);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('ISK', 'EUR', 140.40);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('ALL', 'EUR', 92.18);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('BYN', 'EUR', 3.51);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('BAM', 'EUR', 1.96);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('MDL', 'EUR', 19.94);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('MKD', 'EUR', 61.52);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('RSD', 'EUR', 117.30);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('UAH', 'EUR', 51.86);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('TRY', 'EUR', 56.17);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('GEL', 'EUR', 3.03);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('AMD', 'EUR', 423.40);

insert into bronze.currency_conversions(from_currency_code, to_currency_code, value)
values ('AZN', 'EUR', 1.98);