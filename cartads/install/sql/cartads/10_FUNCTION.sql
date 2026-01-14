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

-- polygons_intersection(text, text, text, text, text, text, text, text, text, integer)
CREATE FUNCTION cartads.polygons_intersection(_schema_a text, _table_a text, _pk_field_a text, _geom_field_a text, _schema_b text, _table_b text, _pk_field_b text, _geom_field_b text, _condition text DEFAULT NULL::text, _limit integer DEFAULT NULL::integer) RETURNS TABLE(pk_a integer, pk_b integer, geom geometry)
    LANGUAGE plpgsql
    AS $_$
BEGIN
  RETURN QUERY EXECUTE
  format(
  $$
    SELECT (%3$s)::int AS pk_a, (%7$s)::int AS pk_b,
    ST_Multi(st_collectionextract(ST_Intersection(a."%4$s", b."%8$s"), 3)) AS geom
    FROM "%1$s"."%2$s" a
    JOIN "%5$s"."%6$s" b ON ST_INTERSECTS(a."%4$s", b."%8$s")
    %9$s
    GROUP BY pk_a, pk_b
    ORDER BY pk_a, pk_b
    %10$s
  $$,
  _schema_a,
  _table_a,
  _pk_field_a,
  _geom_field_a,
  _schema_b,
  _table_b,
  _pk_field_b,
  _geom_field_b,
  ('WHERE ' || _condition),
  ('LIMIT ' || _limit)
  );
END
$_$;


--
-- PostgreSQL database dump complete
--



