-- Database: authdb_dev

-- DROP DATABASE authdb_dev;

CREATE ROLE authdb_read;
CREATE USER auth_user WITH ENCRYPTED PASSWORD 'Eh8Q1*IGOpGK!Qd*9SB5T8DnmIxjo&@1B4nxIbT15ePLSNHViy';
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
    "IsEmployee" boolean NOT NULL,
    CONSTRAINT clients_pkey PRIMARY KEY ("Id")
);

\c authdb_dev auth_user

INSERT INTO public.clients ("ClientId", "ClientSecret", "IsAdmin", "IsEmployee") 
VALUES 
  -- Admin Role
  ('sysadmin', 'fcb9728b3698d0fc32436cbd33e1c11fe0ba0daf', TRUE, TRUE),
  -- Admin Role
  ('cinemaadmin', '08eff19c752e1cbaf913091252b97529a4aae3ee', TRUE, TRUE),
  -- Employee Role
  ('cinemaemployee', 'f96ee118bad4e713726e86f06a9d68e67308814d', FALSE, TRUE),
  -- Customer Role
  ('cinemacustomer', 'eaebaa3a0fa62f87c4216040d6e1d7e054f63a90', FALSE, FALSE);

SELECT * FROM public.clients;

\c authdb_dev postgres

ALTER TABLE public.clients
    OWNER to postgres;

GRANT SELECT ON TABLE public.clients TO authdb_read;

GRANT ALL ON TABLE public.clients TO postgres;
GRANT ALL ON TABLE public.clients TO auth_user; 
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
GRANT ALL ON TABLE public.blacklist TO auth_user; 
GRANT ALL PRIVILEGES ON TABLE public.blacklist TO auth_user;