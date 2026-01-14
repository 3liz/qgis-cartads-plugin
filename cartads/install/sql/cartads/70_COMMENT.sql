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

-- SCHEMA cartads
COMMENT ON SCHEMA cartads IS 'Schéma Administration des Droits du Sol pour la mise en place du connecteur cart@ds';


-- cartads_dossier
COMMENT ON TABLE cartads.cartads_dossier IS 'Liste des parcelles historiques issue du cadastre.';


-- cartads_dossier_geo
COMMENT ON TABLE cartads.cartads_dossier_geo IS 'Liste des dossiers Cart@DS avec une géométrie reconstruite à partir des parcelles';


-- cartads_dossier_parcelle
COMMENT ON TABLE cartads.cartads_dossier_parcelle IS 'Liste des parcelles par dossiers Cart@DS.';


-- cartads_dossier_parcelle_historique
COMMENT ON TABLE cartads.cartads_dossier_parcelle_historique IS 'Liste des parcelles historiques associées aux dossiers Cart@DS avec leur parcelle actuelle.';


-- cartads_parcelle
COMMENT ON TABLE cartads.cartads_parcelle IS 'Liste des parcelles avec leur url vers l''API Cart@DS issue du cadastre.';


-- communes
COMMENT ON TABLE cartads.communes IS 'Table des communes issue du cadastre.';


-- geo_zones
COMMENT ON TABLE cartads.geo_zones IS 'Zones urba avec les géométries.';


-- glossary_zones
COMMENT ON TABLE cartads.glossary_zones IS 'Glossaires des Zones urba Cart@DS.';


-- metadata
COMMENT ON TABLE cartads.metadata IS 'Metadata of the structure : version and date. Useful for database structure and glossary data migrations between versions';


-- zones
COMMENT ON TABLE cartads.zones IS 'Liste des différentes zones d''urbanismes.
Le champ "zones_type" =  ''Zonage'', ''Contrainte annexe'', ''Servitude d''''utilité publique'', ''Prescription d''''urbanisme'', ''Document annexe''.
Le champ "zones_type_code " = ''Z'', ''C'', ''S'', ''P'', ''D''.
 ';


--
-- PostgreSQL database dump complete
--



