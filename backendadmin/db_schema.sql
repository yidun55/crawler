# coding: utf-8
create database if not exists crawler charset 'utf8';
use crawler

drop table if exists daily_quantity;
create table daily_quantity(
       domain_name varchar(30), 
       request integer(10), 
       response integer(10), 
       overdue integer(10), 
       incomplete integer(10), 
       httperror integer(10), 
       append integer(10), 
       updated integer(10), 
       duplicate integer(10), 
       exceptions integer(10), 
       date_str varchar(10) 
);

drop table if exists processer_stats;
create table processer_stats(
       domain_name varchar(30), 
       item_in integer(10), 
       item_out_append integer(10), 
       item_out_update integer(10), 
       item_ignore integer(10), 
       item_ignore_duplicate integer(10), 
       date_str varchar(10), 
       description varchar(200)
);

drop table if exists mongo_stats;
create table mongo_stats(
       domain varchar(30) not null, 
       cur_total integer, 
       old_total integer, 
       date_str varchar(8) not null
);

drop table if exists domains;
create table domains(
       domain varchar(30) not null primary key, 
       domain_name varchar(80) not null, 
       url varchar(100), 
       status integer not null default 1
);
