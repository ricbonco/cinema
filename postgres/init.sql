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

CREATE TABLE movies (
    movie_id SERIAL PRIMARY KEY, 
    movie_name VARCHAR NOT NULL
);

ALTER TABLE movies OWNER TO postgres;
INSERT INTO movies(movie_name) 
VALUES
    ('Inception'), 
    ('Tenet'),
    ('Interstellar'), 
    ('Dunkirk'), 
    ('Memento');
