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

/*CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY, 
    movie_name VARCHAR NOT NULL
);*/

CREATE TABLE "movies" (
  "id" SERIAL PRIMARY KEY,
  "title" varchar,
  "year" int,
  "director" varchar,
  "runtime_minutes" int,
  "genres" varchar
);

ALTER TABLE "movies" OWNER TO postgres;
INSERT INTO "movies" ("title", "year", "director", "runtime_minutes", "genres") 
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

SELECT * FROM "movies";

CREATE TABLE "venues" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "location" varchar
);

ALTER TABLE "venues" OWNER TO postgres;
INSERT INTO "venues" ("name", "location") 
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

SELECT * FROM "venues";

/* Venues where a movie is exhibited */
CREATE TABLE "movies_venues" (
  "id" SERIAL PRIMARY KEY,
  "movie_id" int,
  "venue_id" int
);

ALTER TABLE "movies_venues" ADD FOREIGN KEY ("movie_id") REFERENCES "movies" ("id");

ALTER TABLE "movies_venues" ADD FOREIGN KEY ("venue_id") REFERENCES "venues" ("id");

INSERT INTO "movies_venues" ("venue_id", "movie_id") 
SELECT v.id, m.id FROM "venues" AS v
CROSS JOIN "movies" AS m
WHERE MOD(v.id, m.id) != 0;

SELECT * FROM "movies_venues" AS mv
INNER JOIN "movies" AS m
ON m.id = mv.movie_id
INNER JOIN "venues" AS v
ON v.id = mv.venue_id;

/* Available times for a movie on a specific theater */
CREATE TABLE "movies_times" (
  "id" SERIAL PRIMARY KEY,
  "id_movies_venues" int,
  "movie_date" timestamp
);

/* Available seats for a function and seat type */
CREATE TABLE "movies_seats" (
  "id" SERIAL PRIMARY KEY,
  "id_movies_times" int,
  "total_seats" int,
  "available_seats" int,
  "id_seat_type" int,
  "price" decimal 
);

/* Types of catalogs */
CREATE TABLE "catalogs" (
  "id" SERIAL PRIMARY KEY,
  "catalog_name" varchar
);

/* Values for a specific catalog */
CREATE TABLE "catalogs_values" (
  "id" SERIAL PRIMARY KEY,
  "id_catalog_name" int,
  "catalog_value" varchar
);

ALTER TABLE "movies_times" ADD FOREIGN KEY ("id_movies_venues") REFERENCES "movies_venues" ("id");

ALTER TABLE "catalogs_values" ADD FOREIGN KEY ("id_catalog_name") REFERENCES "catalogs" ("id");

ALTER TABLE "movies_seats" ADD FOREIGN KEY ("id_seat_type") REFERENCES "catalogs_values" ("id");

ALTER TABLE "movies_seats" ADD FOREIGN KEY ("id_movies_times") REFERENCES "movies_times" ("id");

INSERT INTO "catalogs" ("catalog_name") 
VALUES
    ('SEAT_TYPE');

INSERT INTO "catalogs_values" ("id_catalog_name", "catalog_value") 
SELECT id, 'Regular' FROM "catalogs" WHERE catalog_name = 'SEAT_TYPE'
UNION
SELECT id, 'VIP' FROM "catalogs" WHERE catalog_name = 'SEAT_TYPE';

SELECT c.catalog_name, cv.catalog_value FROM "catalogs_values" AS cv
INNER JOIN "catalogs" AS c
ON c.id = cv.id_catalog_name;

INSERT INTO "movies_times" ("id_movies_venues", "movie_date") 
SELECT mv.id, NOW() + m.runtime_minutes * interval '1 minutes' FROM "movies_venues" AS mv 
INNER JOIN "movies" as m
ON m.id = mv.movie_id
UNION
SELECT mv.id, NOW() + 2 * m.runtime_minutes * interval '1 minutes' FROM "movies_venues" AS mv 
INNER JOIN "movies" as m
ON m.id = mv.movie_id
UNION
SELECT mv.id, NOW() + 3 * m.runtime_minutes * interval '1 minutes' FROM "movies_venues" AS mv 
INNER JOIN "movies" as m
ON m.id = mv.movie_id;

SELECT * FROM "movies_times" ORDER BY id_movies_venues;

INSERT INTO "movies_seats" ("id_movies_times", "total_seats", "available_seats", "id_seat_type", "price")
SELECT mt.id, 50, 50, 
      (SELECT cv.id FROM "catalogs" as c 
       INNER JOIN "catalogs_values" as cv 
         ON c.id = cv.id_catalog_name 
         AND c.catalog_name = 'SEAT_TYPE' 
         AND cv.catalog_value = 'Regular'),
      3750
FROM "movies_times" AS mt
UNION
SELECT mt.id, 15, 15, 
      (SELECT cv.id FROM "catalogs" as c 
       INNER JOIN "catalogs_values" as cv 
         ON c.id = cv.id_catalog_name 
         AND c.catalog_name = 'SEAT_TYPE' 
         AND cv.catalog_value = 'VIP'),
      3750
FROM "movies_times" AS mt;

SELECT CONCAT(v.name, ' ', v.location) as venue, m.title, mt.movie_date, ms.total_seats, ms.available_seats, cv.catalog_value, ms.price FROM "movies_seats" as ms
INNER JOIN "movies_times" as mt
  ON mt.id = ms.id_movies_times
INNER JOIN "movies_venues" as mv
  ON mv.id = mt.id_movies_venues
INNER JOIN "movies" as m 
  ON m.id = mv.movie_id
INNER JOIN "venues" as v
  ON v.id = mv.venue_id
INNER JOIN "catalogs_values" as cv
  ON cv.id = ms.id_seat_type

