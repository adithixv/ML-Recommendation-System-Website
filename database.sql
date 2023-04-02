create database users;

use users;
create table accounts(
name varchar(30) PRIMARY KEY NOT NULL,
password varchar(30) NOT NULL
);

select * from accounts;