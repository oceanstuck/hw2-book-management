CREATE DATABASE library;
CREATE TABLE books (
	itemID int NOT NULL AUTO INCREMENT,
	title varchar(255) NOT NULL,
	author varchar(255) NOT NULL,
	publisher varchar(255) NOT NULL,
	year int NOT NULL,
	isbn varchar(18),
	qty int NOT NULL,
	CHECK (qty>=0),
	PRIMARY KEY itemID
);