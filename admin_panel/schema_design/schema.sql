--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2 (Debian 13.2-1.pgdg100+1)
-- Dumped by pg_dump version 13.3 (Ubuntu 13.3-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: admin_panel; Type: SCHEMA; Schema: -; Owner: -
--

DROP SCHEMA IF EXISTS admin_panel CASCADE;
CREATE SCHEMA admin_panel;


--
-- Name: profession; Type: TYPE; Schema: admin_panel; Owner: -
--

CREATE TYPE admin_panel.profession AS ENUM (
    'actor',
    'director',
    'writer'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: movies_filmwork; Type: TABLE; Schema: admin_panel; Owner: -
--

CREATE TABLE admin_panel.movies_filmwork (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title character varying(255) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    imdb_rating double precision
);


--
-- Name: movies_filmwork_genres; Type: TABLE; Schema: admin_panel; Owner: -
--

CREATE TABLE admin_panel.movies_filmwork_genres (
    id bigint NOT NULL,
    genre_id uuid NOT NULL,
    filmwork_id uuid NOT NULL
);


--
-- Name: movies_filmwork_genres_id_seq; Type: SEQUENCE; Schema: admin_panel; Owner: -
--

CREATE SEQUENCE admin_panel.movies_filmwork_genres_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movies_filmwork_genres_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_panel; Owner: -
--

ALTER SEQUENCE admin_panel.movies_filmwork_genres_id_seq OWNED BY admin_panel.movies_filmwork_genres.id;


--
-- Name: movies_genre; Type: TABLE; Schema: admin_panel; Owner: -
--

CREATE TABLE admin_panel.movies_genre (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(20) NOT NULL
);


--
-- Name: movies_person; Type: TABLE; Schema: admin_panel; Owner: -
--

CREATE TABLE admin_panel.movies_person (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    first_name character varying(30) DEFAULT ''::character varying NOT NULL,
    last_name character varying(30) DEFAULT ''::character varying NOT NULL
);


--
-- Name: movies_personfilmwork; Type: TABLE; Schema: admin_panel; Owner: -
--

CREATE TABLE admin_panel.movies_personfilmwork (
    id bigint NOT NULL,
    person_id uuid NOT NULL,
    filmwork_id uuid NOT NULL,
    profession admin_panel.profession NOT NULL
);


--
-- Name: movies_personfilmwork_id_seq; Type: SEQUENCE; Schema: admin_panel; Owner: -
--

CREATE SEQUENCE admin_panel.movies_personfilmwork_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movies_personfilmwork_id_seq; Type: SEQUENCE OWNED BY; Schema: admin_panel; Owner: -
--

ALTER SEQUENCE admin_panel.movies_personfilmwork_id_seq OWNED BY admin_panel.movies_personfilmwork.id;


--
-- Name: movies_filmwork_genres id; Type: DEFAULT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_filmwork_genres ALTER COLUMN id SET DEFAULT nextval('admin_panel.movies_filmwork_genres_id_seq'::regclass);


--
-- Name: movies_personfilmwork id; Type: DEFAULT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_personfilmwork ALTER COLUMN id SET DEFAULT nextval('admin_panel.movies_personfilmwork_id_seq'::regclass);


--
-- Name: movies_genre genres_pkey; Type: CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_genre
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- Name: movies_filmwork_genres movies_filmwork_genres_pkey; Type: CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_filmwork_genres
    ADD CONSTRAINT movies_filmwork_genres_pkey PRIMARY KEY (id);


--
-- Name: movies_personfilmwork movies_personfilmwork_pkey; Type: CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_personfilmwork
    ADD CONSTRAINT movies_personfilmwork_pkey PRIMARY KEY (id);


--
-- Name: movies_filmwork movies_pkey; Type: CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_filmwork
    ADD CONSTRAINT movies_pkey PRIMARY KEY (id);


--
-- Name: movies_person person_pkey; Type: CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);


--
-- Name: movies_filmwork_id_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE INDEX movies_filmwork_id_idx ON admin_panel.movies_filmwork_genres USING btree (filmwork_id);


--
-- Name: movies_genre_filmwork_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE UNIQUE INDEX movies_genre_filmwork_idx ON admin_panel.movies_filmwork_genres USING btree (genre_id, filmwork_id);


--
-- Name: movies_genre_id_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE INDEX movies_genre_id_idx ON admin_panel.movies_filmwork_genres USING btree (genre_id);


--
-- Name: movies_person_filmwork_profession_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE UNIQUE INDEX movies_person_filmwork_profession_idx ON admin_panel.movies_personfilmwork USING btree (person_id, filmwork_id, profession);


--
-- Name: movies_personfilmwork_filmwork_id_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE INDEX movies_personfilmwork_filmwork_id_idx ON admin_panel.movies_personfilmwork USING btree (filmwork_id);


--
-- Name: movies_personfilmwork_person_id_idx; Type: INDEX; Schema: admin_panel; Owner: -
--

CREATE INDEX movies_personfilmwork_person_id_idx ON admin_panel.movies_personfilmwork USING btree (person_id);


--
-- Name: movies_filmwork_genres genre_fkey; Type: FK CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_filmwork_genres
    ADD CONSTRAINT genre_fkey FOREIGN KEY (genre_id) REFERENCES admin_panel.movies_genre(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: movies_filmwork_genres movie_fkey; Type: FK CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_filmwork_genres
    ADD CONSTRAINT movie_fkey FOREIGN KEY (filmwork_id) REFERENCES admin_panel.movies_filmwork(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: movies_personfilmwork movie_fkey; Type: FK CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_personfilmwork
    ADD CONSTRAINT movie_fkey FOREIGN KEY (filmwork_id) REFERENCES admin_panel.movies_filmwork(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: movies_personfilmwork person_fkey; Type: FK CONSTRAINT; Schema: admin_panel; Owner: -
--

ALTER TABLE ONLY admin_panel.movies_personfilmwork
    ADD CONSTRAINT person_fkey FOREIGN KEY (person_id) REFERENCES admin_panel.movies_person(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

