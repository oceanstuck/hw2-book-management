CREATE DATABASE library;
CREATE TABLE books (
	bookID int NOT NULL AUTO_INCREMENT,
	title varchar(255) NOT NULL,
	author varchar(255) NOT NULL,
	publisher varchar(255) NOT NULL,
    edition int DEFAULT 1,
	year int,
	isbn varchar(13),
	qty int DEFAULT 0,
	CHECK (qty>=0 AND edition>0),
	PRIMARY KEY (bookID)
);
CREATE UNIQUE INDEX bookEd ON books (title, edition);

INSERT INTO books VALUES (1, "Apostles of Mercy", "Lindsay Ellis", "St. Martin\'s Press", 1, 2024, "9781250274564", 1);
SELECT * FROM books;