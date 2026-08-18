\restrict dbmate

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anime_relations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.anime_relations (
    anime_id character varying(255) NOT NULL,
    related_anime_id character varying(255) NOT NULL,
    type_related_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_not_self_relation CHECK (((anime_id)::text <> (related_anime_id)::text))
);


--
-- Name: animes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.animes (
    id character varying(255) NOT NULL,
    franchise_id character varying(255),
    season integer DEFAULT 1,
    title character varying(255),
    description text,
    type text,
    poster text,
    is_finished boolean,
    week_day text,
    last_scraped_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_keys (
    id integer NOT NULL,
    user_id uuid NOT NULL,
    key character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    expired_at timestamp with time zone,
    last_used_at timestamp with time zone
);


--
-- Name: api_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_keys_id_seq OWNED BY public.api_keys.id;


--
-- Name: api_scopes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.api_scopes (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: api_scopes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.api_scopes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: api_scopes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.api_scopes_id_seq OWNED BY public.api_scopes.id;


--
-- Name: avatars; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.avatars (
    id integer NOT NULL,
    label character varying(255) NOT NULL,
    url character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: avatars_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.avatars_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: avatars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.avatars_id_seq OWNED BY public.avatars.id;


--
-- Name: episodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.episodes (
    id integer NOT NULL,
    anime_id character varying(255) NOT NULL,
    ep_number integer NOT NULL,
    url text NOT NULL,
    preview text,
    job_id character varying,
    status text,
    size integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: episodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.episodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: episodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.episodes_id_seq OWNED BY public.episodes.id;


--
-- Name: franchises; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.franchises (
    id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: genres; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.genres (
    anime_id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: related_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.related_types (
    id integer NOT NULL,
    name character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: related_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.related_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: related_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.related_types_id_seq OWNED BY public.related_types.id;


--
-- Name: role_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_types (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: role_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.role_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: role_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.role_types_id_seq OWNED BY public.role_types.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Name: user_download_episode; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_download_episode (
    user_id uuid NOT NULL,
    episode_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_save_anime; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_save_anime (
    user_id uuid NOT NULL,
    anime_id character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying(64) NOT NULL,
    password character varying(60) NOT NULL,
    avatar_id integer,
    role_id integer NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: api_keys id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys ALTER COLUMN id SET DEFAULT nextval('public.api_keys_id_seq'::regclass);


--
-- Name: api_scopes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_scopes ALTER COLUMN id SET DEFAULT nextval('public.api_scopes_id_seq'::regclass);


--
-- Name: avatars id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.avatars ALTER COLUMN id SET DEFAULT nextval('public.avatars_id_seq'::regclass);


--
-- Name: episodes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.episodes ALTER COLUMN id SET DEFAULT nextval('public.episodes_id_seq'::regclass);


--
-- Name: related_types id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.related_types ALTER COLUMN id SET DEFAULT nextval('public.related_types_id_seq'::regclass);


--
-- Name: role_types id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_types ALTER COLUMN id SET DEFAULT nextval('public.role_types_id_seq'::regclass);


--
-- Name: anime_relations anime_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_relations
    ADD CONSTRAINT anime_relations_pkey PRIMARY KEY (anime_id, related_anime_id, type_related_id);


--
-- Name: animes animes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animes
    ADD CONSTRAINT animes_pkey PRIMARY KEY (id);


--
-- Name: api_keys api_keys_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_key_key UNIQUE (key);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: api_scopes api_scopes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_scopes
    ADD CONSTRAINT api_scopes_pkey PRIMARY KEY (id);


--
-- Name: avatars avatars_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.avatars
    ADD CONSTRAINT avatars_pkey PRIMARY KEY (id);


--
-- Name: episodes episodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_pkey PRIMARY KEY (id);


--
-- Name: franchises franchises_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.franchises
    ADD CONSTRAINT franchises_pkey PRIMARY KEY (id);


--
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (anime_id, name);


--
-- Name: related_types related_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.related_types
    ADD CONSTRAINT related_types_pkey PRIMARY KEY (id);


--
-- Name: role_types role_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_types
    ADD CONSTRAINT role_types_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: episodes uq_episode_anime_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT uq_episode_anime_number UNIQUE (anime_id, ep_number);


--
-- Name: user_download_episode user_download_episode_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_download_episode
    ADD CONSTRAINT user_download_episode_pkey PRIMARY KEY (user_id, episode_id);


--
-- Name: user_save_anime user_save_anime_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_save_anime
    ADD CONSTRAINT user_save_anime_pkey PRIMARY KEY (user_id, anime_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_animes_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_animes_created_at ON public.animes USING btree (created_at);


--
-- Name: idx_animes_franchise_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_animes_franchise_id ON public.animes USING btree (franchise_id);


--
-- Name: idx_animes_last_scraped; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_animes_last_scraped ON public.animes USING btree (last_scraped_at);


--
-- Name: idx_api_keys_expired; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_api_keys_expired ON public.api_keys USING btree (expired_at);


--
-- Name: idx_episodes_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_episodes_created_at ON public.episodes USING btree (created_at);


--
-- Name: idx_user_download_episode_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_download_episode_created ON public.user_download_episode USING btree (created_at);


--
-- Name: idx_user_download_episode_episode_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_download_episode_episode_id ON public.user_download_episode USING btree (episode_id);


--
-- Name: idx_user_save_anime_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_save_anime_created ON public.user_save_anime USING btree (created_at);


--
-- Name: idx_users_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_created_at ON public.users USING btree (created_at);


--
-- Name: anime_relations anime_relations_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_relations
    ADD CONSTRAINT anime_relations_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.animes(id) ON DELETE CASCADE;


--
-- Name: anime_relations anime_relations_related_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_relations
    ADD CONSTRAINT anime_relations_related_anime_id_fkey FOREIGN KEY (related_anime_id) REFERENCES public.animes(id) ON DELETE CASCADE;


--
-- Name: anime_relations anime_relations_type_related_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.anime_relations
    ADD CONSTRAINT anime_relations_type_related_id_fkey FOREIGN KEY (type_related_id) REFERENCES public.related_types(id) ON DELETE CASCADE;


--
-- Name: animes animes_franchise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.animes
    ADD CONSTRAINT animes_franchise_id_fkey FOREIGN KEY (franchise_id) REFERENCES public.franchises(id) ON DELETE SET NULL;


--
-- Name: api_keys api_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: episodes episodes_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.episodes
    ADD CONSTRAINT episodes_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.animes(id) ON DELETE CASCADE;


--
-- Name: genres genres_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.animes(id) ON DELETE CASCADE;


--
-- Name: user_download_episode user_download_episode_episode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_download_episode
    ADD CONSTRAINT user_download_episode_episode_id_fkey FOREIGN KEY (episode_id) REFERENCES public.episodes(id) ON DELETE CASCADE;


--
-- Name: user_download_episode user_download_episode_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_download_episode
    ADD CONSTRAINT user_download_episode_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_save_anime user_save_anime_anime_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_save_anime
    ADD CONSTRAINT user_save_anime_anime_id_fkey FOREIGN KEY (anime_id) REFERENCES public.animes(id) ON DELETE CASCADE;


--
-- Name: user_save_anime user_save_anime_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_save_anime
    ADD CONSTRAINT user_save_anime_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_avatar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_avatar_id_fkey FOREIGN KEY (avatar_id) REFERENCES public.avatars(id) ON DELETE SET NULL;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role_types(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict dbmate


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('0001');
