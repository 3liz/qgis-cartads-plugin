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

--
-- Data for Name: glossary_zones; Type: TABLE DATA; Schema: cartads; Owner: -
--

INSERT INTO cartads.glossary_zones (glossary_zones_id, zones_type, zones_type_code) VALUES (1, 'Zonage', 'Z');
INSERT INTO cartads.glossary_zones (glossary_zones_id, zones_type, zones_type_code) VALUES (2, 'Contrainte annexe', 'C');
INSERT INTO cartads.glossary_zones (glossary_zones_id, zones_type, zones_type_code) VALUES (3, 'Servitude d''utilité publique', 'C');
INSERT INTO cartads.glossary_zones (glossary_zones_id, zones_type, zones_type_code) VALUES (4, 'Prescription d''urbanisme', 'P');
INSERT INTO cartads.glossary_zones (glossary_zones_id, zones_type, zones_type_code) VALUES (5, 'Document annexe', 'D');


--
-- Name: glossary_zones_glossary_zones_id_seq; Type: SEQUENCE SET; Schema: cartads; Owner: -
--

SELECT pg_catalog.setval('cartads.glossary_zones_glossary_zones_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--



