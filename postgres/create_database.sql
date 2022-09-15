-- Database: authdb_dev

-- DROP DATABASE authdb_dev;

CREATE ROLE authdb_read;
CREATE USER auth_user WITH ENCRYPTED PASSWORD 'mypassword';
GRANT authdb_read TO auth_user;

CREATE DATABASE authdb_dev
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

GRANT ALL PRIVILEGES ON DATABASE authdb_dev TO auth_user;

\c authdb_dev auth_user

CREATE TABLE public.clients
(
    "Id" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    "ClientId" character varying(128) COLLATE pg_catalog."default" NOT NULL,
    "ClientSecret" character varying(256) COLLATE pg_catalog."default" NOT NULL,
    "IsAdmin" boolean NOT NULL,
    CONSTRAINT clients_pkey PRIMARY KEY ("Id")
);

\c authdb_dev auth_user

INSERT INTO public.clients ("ClientId", "ClientSecret", "IsAdmin") 
VALUES 
  ('sysadmin', '274644223f33149c4cb8fc2e30a7cc6e59622809', TRUE),
  ('ricardo', '8e7915f5a99b2f9cbf494d1fd3c7a8952114279d', TRUE);

SELECT * FROM public.clients;

\c authdb_dev postgres


ALTER TABLE public.clients
    OWNER to postgres;

GRANT SELECT ON TABLE public.clients TO authdb_read;

GRANT ALL ON TABLE public.clients TO postgres;
GRANT ALL ON TABLE public.clients TO auth_user; -- RICARDO
GRANT ALL PRIVILEGES ON TABLE public.clients TO auth_user;

CREATE TABLE public.blacklist
(
    token character varying(256) COLLATE pg_catalog."default" NOT NULL
)

TABLESPACE pg_default;

ALTER TABLE public.blacklist
    OWNER to postgres;

GRANT SELECT ON TABLE public.blacklist TO authdb_read;

GRANT ALL ON TABLE public.blacklist TO postgres;
GRANT ALL ON TABLE public.blacklist TO auth_user; -- RICARDO
GRANT ALL PRIVILEGES ON TABLE public.blacklist TO auth_user;