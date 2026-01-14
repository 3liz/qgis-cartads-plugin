--
-- PostgreSQL database dump
--






SET statement_timeout = 0;
SET lock_timeout = 0;


SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- cartads_dossier_geo cartads_dossier_geo_id_dossier_key
ALTER TABLE ONLY cartads.cartads_dossier_geo
    ADD CONSTRAINT cartads_dossier_geo_id_dossier_key UNIQUE (id_dossier);


-- cartads_dossier_geo cartads_dossier_geo_nom_dossier_key
ALTER TABLE ONLY cartads.cartads_dossier_geo
    ADD CONSTRAINT cartads_dossier_geo_nom_dossier_key UNIQUE (nom_dossier);


-- cartads_dossier_geo cartads_dossier_geo_pkey
ALTER TABLE ONLY cartads.cartads_dossier_geo
    ADD CONSTRAINT cartads_dossier_geo_pkey PRIMARY KEY (cartads_dossier_geo_id);


-- cartads_dossier cartads_dossier_id_dossier_key
ALTER TABLE ONLY cartads.cartads_dossier
    ADD CONSTRAINT cartads_dossier_id_dossier_key UNIQUE (id_dossier);


-- cartads_dossier cartads_dossier_nom_dossier_key
ALTER TABLE ONLY cartads.cartads_dossier
    ADD CONSTRAINT cartads_dossier_nom_dossier_key UNIQUE (nom_dossier);


-- cartads_dossier_parcelle_historique cartads_dossier_parcelle_historique_pkey
ALTER TABLE ONLY cartads.cartads_dossier_parcelle_historique
    ADD CONSTRAINT cartads_dossier_parcelle_historique_pkey PRIMARY KEY (cartads_dossier_parcelle_historique_id);


-- cartads_dossier_parcelle cartads_dossier_parcelle_pkey
ALTER TABLE ONLY cartads.cartads_dossier_parcelle
    ADD CONSTRAINT cartads_dossier_parcelle_pkey PRIMARY KEY (cartads_dossier_parcelle_id);


-- cartads_dossier cartads_dossier_pkey
ALTER TABLE ONLY cartads.cartads_dossier
    ADD CONSTRAINT cartads_dossier_pkey PRIMARY KEY (cartads_dossier_id);


-- cartads_parcelle cartads_parcelle_cartads_parcelle_key
ALTER TABLE ONLY cartads.cartads_parcelle
    ADD CONSTRAINT cartads_parcelle_cartads_parcelle_key UNIQUE (cartads_parcelle);


-- cartads_parcelle cartads_parcelle_geo_parcelle_key
ALTER TABLE ONLY cartads.cartads_parcelle
    ADD CONSTRAINT cartads_parcelle_geo_parcelle_key UNIQUE (geo_parcelle);


-- cartads_parcelle_historique cartads_parcelle_historique_cartads_parcelle_key
ALTER TABLE ONLY cartads.cartads_parcelle_historique
    ADD CONSTRAINT cartads_parcelle_historique_cartads_parcelle_key UNIQUE (cartads_parcelle);


-- cartads_parcelle_historique cartads_parcelle_historique_geo_parcelle_key
ALTER TABLE ONLY cartads.cartads_parcelle_historique
    ADD CONSTRAINT cartads_parcelle_historique_geo_parcelle_key UNIQUE (geo_parcelle);


-- cartads_parcelle_historique cartads_parcelle_historique_pkey
ALTER TABLE ONLY cartads.cartads_parcelle_historique
    ADD CONSTRAINT cartads_parcelle_historique_pkey PRIMARY KEY (cartads_parcelle_id);


-- cartads_parcelle cartads_parcelle_pkey
ALTER TABLE ONLY cartads.cartads_parcelle
    ADD CONSTRAINT cartads_parcelle_pkey PRIMARY KEY (cartads_parcelle_id);


-- communes communes_pkey
ALTER TABLE ONLY cartads.communes
    ADD CONSTRAINT communes_pkey PRIMARY KEY (communes_id);


-- geo_zones geo_zones_pkey
ALTER TABLE ONLY cartads.geo_zones
    ADD CONSTRAINT geo_zones_pkey PRIMARY KEY (geo_zones_id);


-- glossary_zones glossary_zones_pkey
ALTER TABLE ONLY cartads.glossary_zones
    ADD CONSTRAINT glossary_zones_pkey PRIMARY KEY (glossary_zones_id);


-- cartads_dossier_parcelle id_dossier_cartads_parcelle_key
ALTER TABLE ONLY cartads.cartads_dossier_parcelle
    ADD CONSTRAINT id_dossier_cartads_parcelle_key UNIQUE (id_dossier, cartads_parcelle);


-- new_cartads_dossier new_cartads_dossier_id_dossier_key
ALTER TABLE ONLY cartads.new_cartads_dossier
    ADD CONSTRAINT new_cartads_dossier_id_dossier_key UNIQUE (id_dossier);


-- new_cartads_dossier new_cartads_dossier_nom_dossier_key
ALTER TABLE ONLY cartads.new_cartads_dossier
    ADD CONSTRAINT new_cartads_dossier_nom_dossier_key UNIQUE (nom_dossier);


-- zones zones_pkey
ALTER TABLE ONLY cartads.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (zones_id);


--
-- PostgreSQL database dump complete
--
