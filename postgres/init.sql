SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;
CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

CREATE TABLE "movie" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar,
  "year" int,
  "director" varchar,
  "runtime_minutes" int,
  "genres" varchar
);

ALTER TABLE "movie" OWNER TO postgres;
INSERT INTO "movie" ("title", "year", "director", "runtime_minutes", "genres") 
VALUES
    ('Inception', 2010, 'Christopher Nolan', 148, 'Action, Adventure, Sci-fi'), 
    ('Tenet', 2020, 'Christopher Nolan', 150, 'Action, Sci-fi, Thriller'),
    ('Interstellar', 2014, 'Christopher Nolan', 169, 'Adventure, Drama, Sci-fi'), 
    ('Dunkirk', 2017, 'Christopher Nolan', 106, 'Action, Drama, History'), 
    ('Memento', 2000, 'Christopher Nolan', 113, 'Mistery, Thriller'),
    ('The Shawshank Redemption', 1994, 'Frank Darabont', 142, 'Drama'),
    ('Schindlers List', 1993, 'Stephen Spielberg', 195, 'Biography, Drama, History'),
    ('Pulp Fiction', 1994, 'Quentin Tarantino', 154, 'Crime, Drama'),
    ('Forrest Gump', 1994, 'Robert Zemeckis', 142, 'Drama, Romance'),
    ('Fight Club', 1999, 'David Fincher', 139, 'Drama');

SELECT * FROM "movie";

CREATE TABLE "venue" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "location" varchar
);

ALTER TABLE "venue" OWNER TO postgres;
INSERT INTO "venue" ("name", "location") 
VALUES
    ('Cinemark', 'Multiplaza Curridabat'), 
    ('Cinemark', 'Multiplaza Escazu'), 
    ('Cinemark', 'City Mall'), 
    ('Nova Cinemas', 'Plaza Real'),
    ('Nova Cinemas', 'Avenida Escazu'),
    ('Nova Cinemas', 'Ciudad del Este'),
    ('Cinepolis', 'Multicentro Desamparados'), 
    ('Cinepolis', 'Lincoln Plaza'), 
    ('Cinepolis', 'Terramall'), 
    ('Cinepolis', 'Terrazas Lindora');

SELECT * FROM "venue";

/* Venues where a movie is exhibited */
CREATE TABLE "movie_venue" (
  "id" SERIAL PRIMARY KEY,
  "id_movie" int,
  "id_venue" int
);

ALTER TABLE "movie_venue" ADD FOREIGN KEY ("id_movie") REFERENCES "movie" ("id");

ALTER TABLE "movie_venue" ADD FOREIGN KEY ("id_venue") REFERENCES "venue" ("id");

INSERT INTO "movie_venue" ("id_venue", "id_movie") 
SELECT v.id, m.id FROM "venue" AS v
CROSS JOIN "movie" AS m
WHERE MOD(v.id, m.id) != 0;

SELECT * FROM "movie_venue" AS mv
INNER JOIN "movie" AS m
ON m.id = mv.id_movie
INNER JOIN "venue" AS v
ON v.id = mv.id_venue;

/* Available times for a movie on a specific theater */
CREATE TABLE "movie_time" (
  "id" SERIAL PRIMARY KEY,
  "id_movie_venue" int,
  "movie_date" timestamp
);

/* Available seats for a function and seat type */
CREATE TABLE "movie_seat" (
  "id" SERIAL PRIMARY KEY,
  "id_movie_time" int,
  "total_seats" int,
  "available_seats" int,
  "id_seat_type" int,
  "price" decimal 
);

/* Types of catalogs */
CREATE TABLE "catalog" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar
);

/* Values for a specific catalog */
CREATE TABLE "catalog_value" (
  "id" SERIAL PRIMARY KEY,
  "id_catalog_name" int,
  "value" varchar
);

ALTER TABLE "movie_time" ADD FOREIGN KEY ("id_movie_venue") REFERENCES "movie_venue" ("id");

ALTER TABLE "catalog_value" ADD FOREIGN KEY ("id_catalog_name") REFERENCES "catalog" ("id");

ALTER TABLE "movie_seat" ADD FOREIGN KEY ("id_seat_type") REFERENCES "catalog_value" ("id");

ALTER TABLE "movie_seat" ADD FOREIGN KEY ("id_movie_time") REFERENCES "movie_time" ("id");

INSERT INTO "catalog" ("name") 
VALUES
    ('SEAT_TYPE');

INSERT INTO "catalog_value" ("id_catalog_name", "value") 
SELECT id, 'Regular' FROM "catalog" WHERE "name" = 'SEAT_TYPE'
UNION
SELECT id, 'VIP' FROM "catalog" WHERE "name" = 'SEAT_TYPE';

SELECT c.name, cv.value FROM "catalog_value" AS cv
INNER JOIN "catalog" AS c
ON c.id = cv.id_catalog_name;

INSERT INTO "movie_time" ("id_movie_venue", "movie_date") 
SELECT mv.id, NOW() + m.runtime_minutes * interval '1 minutes' FROM "movie_venue" AS mv 
INNER JOIN "movie" as m
ON m.id = mv.id_movie
UNION
SELECT mv.id, NOW() + 2.5 * m.runtime_minutes * interval '1 minutes' FROM "movie_venue" AS mv 
INNER JOIN "movie" as m
ON m.id = mv.id_movie
UNION
SELECT mv.id, NOW() + 3.5 * m.runtime_minutes * interval '1 minutes' FROM "movie_venue" AS mv 
INNER JOIN "movie" as m
ON m.id = mv.id_movie;

SELECT * FROM "movie_time" ORDER BY id_movie_venue;

INSERT INTO "movie_seat" ("id_movie_time", "total_seats", "available_seats", "id_seat_type", "price")
SELECT mt.id, 50, 50, 
      (SELECT cv.id FROM "catalog" as c 
       INNER JOIN "catalog_value" as cv 
         ON c.id = cv.id_catalog_name 
         AND c.name = 'SEAT_TYPE' 
         AND cv.value = 'Regular'),
      3750
FROM "movie_time" AS mt
UNION
SELECT mt.id, 15, 15, 
      (SELECT cv.id FROM "catalog" as c 
       INNER JOIN "catalog_value" as cv 
         ON c.id = cv.id_catalog_name 
         AND c.name = 'SEAT_TYPE' 
         AND cv.value = 'VIP'),
      7000
FROM "movie_time" AS mt;

SELECT CONCAT(v.name, ' ', v.location) as venue, m.title, mt.movie_date, ms.total_seats, ms.available_seats, cv.value as ticket_type, ms.price 
FROM "movie_seat" as ms
INNER JOIN "movie_time" as mt
  ON mt.id = ms.id_movie_time
INNER JOIN "movie_venue" as mv
  ON mv.id = mt.id_movie_venue
INNER JOIN "movie" as m 
  ON m.id = mv.id_movie
INNER JOIN "venue" as v
  ON v.id = mv.id_venue
INNER JOIN "catalog_value" as cv
  ON cv.id = ms.id_seat_type;

CREATE TABLE "booking" (
  "id" SERIAL PRIMARY KEY,
  "id_movie_seat" int,
  "id_user" int,
  "reserved_seats" int,
  "time" timestamp
);

ALTER TABLE "booking" ADD FOREIGN KEY ("id_movie_seat") REFERENCES "movie_seat" ("id");

CREATE TABLE "payment" (
  "id" SERIAL PRIMARY KEY,
  "id_booking" int,
  "approved" boolean,
  "last_digits" int,
  "time" timestamp
);

ALTER TABLE "payment" ADD FOREIGN KEY ("id_booking") REFERENCES "booking" ("id");

CREATE TABLE "notification" (
  "id" SERIAL PRIMARY KEY,
  "sender" varchar,
  "recipient" varchar,
  "subject" varchar,
  "body" varchar,
  "time" timestamp
);