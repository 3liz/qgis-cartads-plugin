"""Tests for Processing algorithms."""

import unittest

from pathlib import Path

import psycopg

from qgis import processing

from cartads.plugin_tools.feedback import LoggerProcessingFeedBack
from cartads.plugin_tools.resources import (
    available_migrations,
    schema_version,
)
from cartads.processing.database import CreateDatabaseStructure, UpgradeDatabaseStructure
from cartads.processing.provider import Provider

# This list must not be changed
# as it correspond to the list of tables
# created for the first version
TABLES_FOR_FIRST_VERSION = [
    "glossary_test_category",
    "metadata",
    "test",
]

# Expected list of tables for current version
# Must be changed any time the SQL structure is changed
TABLES_FOR_CURRENT_VERSION = [
    "glossary_zones",
    "metadata",
    "cartads_dossier",
    "cartads_dossier_geo",
    "cartads_dossier_parcelle",
    "cartads_dossier_parcelle_historique",
    "cartads_parcelle",
    "cartads_parcelle_historique",
    "communes",
    "geo_zones",
    "new_cartads_dossier",
    "zones",
]


def test_available_migrations():
    versions = available_migrations()
    assert versions[-1][0] == schema_version()  # The last upgrade available


def test_processing_create(processing_provider: Provider):
    params = {
        "CONNECTION_NAME": "test",
        "OVERRIDE": True,
    }

    feedback = LoggerProcessingFeedBack()

    # Run create database structure alg
    alg = f"{processing_provider.id()}:create_database_structure"
    processing_output = processing.run(alg, params, feedback=feedback)

    assert processing_output["OUTPUT_STATUS"] == 1
    assert processing_output["OUTPUT_VERSION"] == schema_version()


def test_upgrade_from(
    db_schema: str,
    db_install_version: int,
    db_connection: psycopg.Connection,
    processing_provider: Provider,
    data: Path,
):
    """Test the algorithms for creating and updating the database structure."""

    current_version = schema_version()

    assert db_install_version is not None, "This test require at least one available upgrade"
    assert current_version >= db_install_version, (
        "Current schema version cannot be lower than install version"
    )

    # Get the installation dir of the previous version
    test_version = db_install_version
    if current_version == db_install_version:
        test_version = db_install_version - 1
    install_dir = data.joinpath(f"install-version-{test_version}", "sql")
    assert install_dir.exists()

    feedback = LoggerProcessingFeedBack()

    # Create the database from the latest update
    CreateDatabaseStructure.create_database(
        "test",
        db_schema,
        version=test_version,
        override=True,
        install_dir=install_dir,
        feedback=feedback,
    )

    case = unittest.TestCase()

    cursor = db_connection.cursor()

    # Check the list of tables and views from the database
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]

    # Expected tables in the specific version written above at the beginning of the test.
    # DO NOT CHANGE HERE, change below at the end of the test.
    case.assertCountEqual(TABLES_FOR_FIRST_VERSION, result)

    assert result == TABLES_FOR_FIRST_VERSION

    # Check if the version has been written in the metadata table
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()
    assert record is not None
    assert int(record[0]) == test_version
    assert int(record[0]) != current_version

    # Run the update database structure alg
    # Since the structure has been created with db_install_version above
    # The expected list of tables
    feedback.pushDebugInfo("Update the database")
    UpgradeDatabaseStructure.upgrade_database(
        "test",
        db_schema,
        run_migrations=True,
        feedback=feedback,
    )
    # Check if the version has been written in the metadata table
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()
    assert record is not None
    assert int(record[0]) == current_version
    assert int(record[0]) != test_version
    # Check the list of tables
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]
    case.assertCountEqual(TABLES_FOR_CURRENT_VERSION, result)

    # Close connection
    db_connection.close()


def test_upgrade_all(
    db_schema: str,
    db_connection: psycopg.Connection,
    processing_provider: Provider,
    data: Path,
):
    """Test the algorithms for creating and updating the database structure."""

    current_version = schema_version()

    assert current_version >= 1, (
        "Current schema version cannot be lower than install version"
    )

    # Get the installation dir of the previous version
    test_version = 1
    install_dir = data.joinpath(f"install-version-{test_version}", "sql")
    assert install_dir.exists()

    feedback = LoggerProcessingFeedBack()

    # Create the database from the latest update
    CreateDatabaseStructure.create_database(
        "test",
        db_schema,
        version=test_version,
        override=True,
        install_dir=install_dir,
        feedback=feedback,
    )

    case = unittest.TestCase()

    cursor = db_connection.cursor()

    # Check the list of tables and views from the database
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]

    # Expected tables in the specific version written above at the beginning of the test.
    # DO NOT CHANGE HERE, change below at the end of the test.
    case.assertCountEqual(TABLES_FOR_FIRST_VERSION, result)

    assert result == TABLES_FOR_FIRST_VERSION

    # Check if the version has been written in the metadata table
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()
    assert record is not None
    assert int(record[0]) == test_version
    assert int(record[0]) != current_version

    # Run the update database structure alg
    # Since the structure has been created with db_install_version above
    # The expected list of tables
    feedback.pushDebugInfo("Update the database")
    UpgradeDatabaseStructure.upgrade_database(
        "test",
        db_schema,
        run_migrations=True,
        feedback=feedback,
    )
    # Check if the version has been written in the metadata table
    sql = f"""
        SELECT me_version
        FROM {db_schema}.metadata
        WHERE me_status = 1
        ORDER BY me_version_date DESC
        LIMIT 1;
    """
    cursor.execute(sql)
    record = cursor.fetchone()
    assert record is not None
    assert int(record[0]) == current_version
    assert int(record[0]) != test_version
    # Check the list of tables
    cursor.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{db_schema}'
        ORDER BY table_name
        """
    )
    records = cursor.fetchall()
    result = [r[0] for r in records]
    case.assertCountEqual(TABLES_FOR_CURRENT_VERSION, result)

    # Close connection
    db_connection.close()
