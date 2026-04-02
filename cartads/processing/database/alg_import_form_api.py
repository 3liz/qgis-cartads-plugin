
import hashlib
import time

from urllib.parse import urlparse

import requests

from qgis.core import (
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterString,
    QgsProject,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from ..tools import get_connection_name
from .base import BaseDatabaseAlgorithm, i18n, resources

# Shorcut
tr = i18n.tr


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_token(client_id: str, login: str, password: str, auth_url: str) -> str:
    # Initializing the sha256() method
    sha256 = hashlib.sha256()
    sha256.update(password.encode('UTF-8'))

    # Build payload
    auth_payload = {
        "clientId": client_id,
        "login": login,
        "password": sha256.hexdigest(),
    }

    # Perform request
    r = requests.post(auth_url, json=auth_payload)
    if r.status_code == requests.codes.ok \
            and r.headers.get('content-type','').startswith('application/json'):
        resp = r.json()
        return resp.get('Token')

    r.raise_for_status()
    return ''


def get_dossiers(token: str, api_url: str, api_payload: dict) -> list:
    # headers with autorization
    api_headers = {
        "Authorization": 'Bearer ' + token,
    }

    # Perform requests
    r = requests.get(api_url, params=api_payload, headers=api_headers)
    if r.status_code == requests.codes.ok \
        and r.headers.get('content-type', '').startswith('application/json'):
        resp = r.json()
        return resp

    r.raise_for_status()
    return []


def dossiers_into_insert(dossiers: list, schema: str, feedback: QgsProcessingFeedback) -> str:
    ''' Create the SQL query to insert the dossiers'''

    # convert dossiers into INSERT SQL Values

    def quote(s: str) -> str:
        return s.strip().replace("'", "''")

    dossier_values = [(
        "("
        f"{dossier.get('IdDossier')}, "
        f"'{dossier.get('NomDossier')}', "
        f"'{dossier.get('CoCommune')}', "
        f"{dossier.get('NCommune')}, "
        f"'{dossier.get('NVoirieTerrain', '')} {quote(dossier.get('AdresseTerrain', ''))}', "
        f"'{dossier.get('Parcelles')}', "
        f"'{dossier.get('CoTypeDossier')}', "
        f"'{dossier.get('Annee')}', "
        f"'{dossier.get('DateDepot')}', "
        f"'{dossier.get('DateLimiteInstruction', 'NULL')}', "
        f"'{dossier.get('DateModificationDossier')}', "
        f"'{dossier.get('DateAvisInstructeur', 'NULL')}', "
        f"'{dossier.get('DateDecisionSignataire', 'NULL')}', "
        f"'{dossier.get('DateNotificationDecisionSignataire', 'NULL')}', "
        f"'{quote(dossier.get('Stade', 'NULL'))}', "
        f"'{quote(dossier.get('AutoriteCompetente','NULL'))}', "
        f"'{quote(dossier.get('Instructeur', 'NULL'))}', "
        f"'{quote(dossier.get('AvisInstructeur', 'NULL'))}', "
        f"'{quote(dossier.get('Signataire', 'NULL'))}', "
        f"'{quote(dossier.get('DecisionSignataire', 'NULL'))}', "
        f"'{dossier.get('PrenomDemandeur', '')}  {quote(dossier.get('NomDemandeur', ''))}', "
        f"'{dossier.get('UrlDossier')}'"
        ")"
    ) for dossier in dossiers]

    # Join values
    values = ",\n".join(dossier_values)
    # Return the INSERT
    return (
        f"INSERT INTO \"{schema}\".new_cartads_dossier ("
        f"id_dossier, nom_dossier, commune, n_commune, adresse, "
        f"liste_parcelles, type_dossier, annee, date_depot, "
        f"date_limite_instruction, date_modification_dossier, "
        f"date_avis_instructeur, date_decision, date_notification_decision, "
        f"stade, autorite, instructeur, avis_instructeur, signataire, "
        f"decision, demandeur_principal, url_dossier) VALUES\n"
        f"{values}\n"
        f"ON CONFLICT DO NOTHING;"
    )


class ImportFromApi(BaseDatabaseAlgorithm):
    CONNECTION_NAME = "CONNECTION_NAME"
    SCHEMA = "SCHEMA"
    CLIENT_ID = "CLIENT_ID"
    LOGIN = "LOGIN"
    PASSWORD = "PASSWORD"
    AUTH_URL = "AUTH_URL"
    API_URL = "API_URL"
    DATE_MODIFICATION = "DATE_MODIFICATION"
    DATE_DEPOT_DEBUT = "DATE_DEPOT_DEBUT"
    DATE_DEPOT_FIN = "DATE_DEPOT_FIN"

    OUTPUT_STATUS = "OUTPUT_STATUS"
    OUTPUT_STRING = "OUTPUT_STRING"

    def name(self):
        return "import_from_api"

    def displayName(self):
        return tr("Import data from Cart@DS API")

    def shortHelpString(self):
        short_help = tr(
            "Import data from Cart@DS API."
            "\n"
            "\n"
            "If you have upgraded your QGIS plugin, you can run this script"
            " to upgrade your database to the new plugin version."
            "\n"
            "\n"
            "* PostgreSQL connection to the database: name of the database "
            "connection you would like to use for the upgrade."
            "* PostgreSQL schema in the database: The Cart@DS schema name."
            "* Cart@DS client ID: The Cart@DS client ID."
            "* Cart@DS login: The Cart@DS login."
            "* Cart@DS password: The Cart@DS password not already HASH."
            "* Cart@DS auth URL: The Cart@DS auth URL."
            "* Cart@DS API URL: The Cart@DS API URL."
        )
        return short_help

    def initAlgorithm(self, config):
        project = QgsProject.instance()
        connection_name = get_connection_name(project)
        connection_param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            tr("Connection to the PostgreSQL database"),
            "postgres",
            defaultValue=connection_name,
            optional=False,
        )
        connection_param.setHelp(tr("The database where the data will be imported."))
        self.addParameter(connection_param)

        schema_param = QgsProcessingParameterString(
            self.SCHEMA,
            tr("Schema name"),
            defaultValue=resources.schema_name(),
        )
        schema_param.setHelp(tr("The schema where the data will be imported."))
        self.addParameter(schema_param)

        self.addParameter(
            QgsProcessingParameterString(
                self.CLIENT_ID,
                tr("Cart@DS client ID"),
            ),
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.LOGIN,
                tr("Cart@DS login"),
            ),
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.PASSWORD,
                tr("Cart@DS password"),
            ),
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.AUTH_URL,
                tr("Cart@DS auth URL"),
            ),
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.API_URL,
                tr("Cart@DS API URL"),
            ),
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.DATE_MODIFICATION,
                tr("Date de modification"),
                QgsProcessingParameterDateTime.Date,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.DATE_DEPOT_DEBUT,
                tr("Date de dépot, borne inférieure"),
                QgsProcessingParameterDateTime.Date,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.DATE_DEPOT_FIN,
                tr("Date de dépot, borne supérieure"),
                QgsProcessingParameterDateTime.Date,
                optional=True,
            )
        )

        # OUTPUTS
        # Add output for status (integer) and message (string)
        self.addOutput(QgsProcessingOutputNumber(self.OUTPUT_STATUS, tr("Output status")))
        self.addOutput(QgsProcessingOutputString(self.OUTPUT_STRING, tr("Output message")))

    def checkParameterValues(self, parameters, context):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters,
            self.CONNECTION_NAME,
            context,
        )
        connection = metadata.findConnection(connection_name)
        schema = self.parameterAsString(parameters, self.SCHEMA, context)

        if schema not in connection.schemas():
            msg = tr(
                f"Schema {schema} does not exist in database!"
            )
            return False, msg

        auth_url = self.parameterAsString(parameters, self.AUTH_URL, context)

        if not is_valid_url(auth_url):
            msg = tr(
                f"The auth URL {auth_url} is not valid!"
            )
            return False, msg

        api_url = self.parameterAsString(parameters, self.API_URL, context)

        if not is_valid_url(api_url):
            msg = tr(
                f"The API URL {api_url} is not valid!"
            )
            return False, msg

        return super(ImportFromApi, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        connection_name = self.parameterAsConnectionName(parameters, self.CONNECTION_NAME, context)
        schema = self.parameterAsString(parameters, self.SCHEMA, context)

        client_id = self.parameterAsString(parameters, self.CLIENT_ID, context)
        login = self.parameterAsString(parameters, self.LOGIN, context)
        password = self.parameterAsString(parameters, self.PASSWORD, context)
        auth_url = self.parameterAsString(parameters, self.AUTH_URL, context)
        api_url = self.parameterAsString(parameters, self.API_URL, context)

        date_modification = self.parameterAsDateTime(parameters, self.DATE_MODIFICATION, context)
        date_depot_debut = self.parameterAsDateTime(parameters, self.DATE_DEPOT_DEBUT, context)
        date_depot_fin = self.parameterAsDateTime(parameters, self.DATE_DEPOT_FIN, context)

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(f"La connexion {connection_name} n'existe pas.")

        connection.executeSql(f'TRUNCATE TABLE "{schema}".new_cartads_dossier;')

        step = 0
        token = None
        while step != -1:
            if not token:
                feedback.pushInfo(tr("Getting the token to acces the API"))
                token = get_token(client_id, login, password, auth_url)
            if not token:
                raise QgsProcessingException("The token could not be retrieved from the API.")

            index = 1 * step
            limit = 5000
            offset = index * limit

            api_payload = {}
            if date_modification:
                api_payload['dateModification'] = date_modification.date().toPyDate().isoformat()
            if date_depot_debut:
                api_payload['dateDepotDebut'] = date_depot_debut.date().toPyDate().isoformat()
            if date_depot_fin:
                api_payload['dateDepotFin'] = date_depot_fin.date().toPyDate().isoformat()
            if limit:
                api_payload['limit'] = limit
            if offset:
                api_payload['offset'] = offset

            dossiers = get_dossiers(token, api_url, api_payload)
            if not dossiers:
                step = -1
                break

            nb_doss = len(dossiers)
            feedback.pushInfo(tr(f"Getting {nb_doss} dossiers from API for step {step}"))
            if not nb_doss:
                step = -1
                break

            sql_insert = dossiers_into_insert(dossiers, schema, feedback)
            if not sql_insert:
                step = -1
                break

            feedback.pushInfo(tr(f"Inserting {nb_doss} dossiers into database"))

            try:
                connection.executeSql(sql_insert)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))

            feedback.pushInfo(tr(f"Inserted {nb_doss} dossiers into database"))

            time.sleep(1)
            if nb_doss != limit:
                step = -1
            else:
                step += 1

        feedback.pushInfo(tr("Updating dossiers into database"))

        # liste des dossiers dont la liste des parcelles a changé
        sql = (
            "SELECT d.id_dossier "
            f"FROM \"{schema}\".cartads_dossier d "
            f"JOIN \"{schema}\".new_cartads_dossier n ON n.id_dossier = d.id_dossier "
            "WHERE d.liste_parcelles != n.liste_parcelles "
        )
        results = connection.executeSql(sql)
        dossiers_parcelles = []
        for result in results:
            dossiers_parcelles.append(result[0])

        nb_dossiers_parcelles = len(dossiers_parcelles)
        feedback.pushInfo(tr(f"{nb_dossiers_parcelles} dossiers dont la listes des parcelles a changé"))

        # liste des nouveaux dossiers
        sql = (
            "SELECT n.id_dossier "
            f"FROM \"{schema}\".new_cartads_dossier n "
            f"LEFT JOIN \"{schema}\".cartads_dossier d ON n.id_dossier = d.id_dossier "
            "WHERE d.id_dossier IS NULL "
        )
        results = connection.executeSql(sql)
        nouveaux_dossiers = []
        for result in results:
            nouveaux_dossiers.append(result[0])

        nb_nouveaux_dossiers = len(nouveaux_dossiers)
        feedback.pushInfo(tr(f"{nb_nouveaux_dossiers} nouveaux dossiers"))

        # suppression des parcelles et des géométries des dossiers dont la liste des parcelles a changé
        if dossiers_parcelles:
            feedback.pushInfo(
                tr(
                    "Suppression des parcelles et des géométries "
                    "des dossiers dont la liste des parcelles a changé"
                )
            )
            connection.executeSql(
                f"DELETE FROM \"{schema}\".cartads_dossier_parcelle WHERE "
                f"id_dossier IN ({','.join(map(str, dossiers_parcelles))})"
            )
            connection.executeSql(
                f"DELETE FROM \"{schema}\".cartads_dossier_geo WHERE "
                f"id_dossier IN ({','.join(map(str, dossiers_parcelles))})"
            )

        # ajout et mise à jour des dossiers
        feedback.pushInfo("Lancement de l'ajout et mise à jour des dossiers")
        connection.executeSql(
            f"INSERT INTO \"{schema}\".cartads_dossier ("
            "id_dossier, nom_dossier, commune, n_commune, adresse, "
            "liste_parcelles, type_dossier, annee, date_depot, "
            "date_limite_instruction, date_modification_dossier, "
            "date_avis_instructeur, date_decision, date_notification_decision, "
            "stade, autorite, instructeur, avis_instructeur, signataire, "
            "decision, demandeur_principal, url_dossier)\n"
            "SELECT id_dossier, nom_dossier, commune, n_commune, adresse, "
            "liste_parcelles, type_dossier, annee, date_depot, "
            "date_limite_instruction, date_modification_dossier, "
            "date_avis_instructeur, date_decision, date_notification_decision, "
            "stade, autorite, instructeur, avis_instructeur, signataire, "
            "decision, demandeur_principal, url_dossier\n"
            f"FROM \"{schema}\".new_cartads_dossier\n"
            "ORDER BY id_dossier ASC\n"
            "ON CONFLICT (nom_dossier) DO UPDATE\n"
            "SET commune = EXCLUDED.commune, "
            "n_commune = EXCLUDED.n_commune, "
            "adresse = EXCLUDED.adresse, "
            "liste_parcelles = EXCLUDED.liste_parcelles, "
            "type_dossier = EXCLUDED.type_dossier, "
            "annee = EXCLUDED.annee, "
            "date_depot = EXCLUDED.date_depot, "
            "date_limite_instruction = EXCLUDED.date_limite_instruction, "
            "date_modification_dossier = EXCLUDED.date_modification_dossier, "
            "date_avis_instructeur = EXCLUDED.date_avis_instructeur, "
            "date_decision = EXCLUDED.date_decision, "
            "date_notification_decision = EXCLUDED.date_notification_decision, "
            "stade = EXCLUDED.stade, "
            "autorite = EXCLUDED.autorite, "
            "instructeur = EXCLUDED.instructeur, "
            "avis_instructeur = EXCLUDED.avis_instructeur, "
            "signataire = EXCLUDED.signataire, "
            "decision = EXCLUDED.decision, "
            "demandeur_principal = EXCLUDED.demandeur_principal, "
            "url_dossier = EXCLUDED.url_dossier "
            "RETURNING id_dossier "
        )
        feedback.pushInfo("Ajout et mise à jour des dossiers terminés")

        # Mise à jour des parcelles et la géométrie des dossiers
        if dossiers_parcelles or nouveaux_dossiers:
            # Mise à jour des parcelles des dossiers
            feedback.pushInfo("Lancement de la mise à jour des parcelles des dossiers")
            connection.executeSql(
                f"INSERT INTO \"{schema}\".cartads_dossier_parcelle ("
                "id_dossier, nom_dossier, cartads_parcelle)\n"
                "SELECT d.id_dossier, d.nom_dossier, "
                "trim(unnest(string_to_array(d.liste_parcelles, ','))) cartads_parcelle "
                f"FROM \"{schema}\".cartads_dossier d "
                f"WHERE id_dossier IN "
                f"({','.join(map(str, dossiers_parcelles) + map(str, nouveaux_dossiers))})\n"
                "ON CONFLICT (id_dossier, cartads_parcelle) DO NOTHING\n"
                "RETURNING id_dossier, cartads_parcelle "
            )
            feedback.pushInfo("Mise à jour des parcelles des dossiers terminée")

            # Récupération du code geo_parcelle
            feedback.pushInfo("Lancement de la récupération du code geo_parcelle")
            connection.executeSql(
                f"UPDATE \"{schema}\".cartads_dossier_parcelle\n"
                "SET geo_parcelle = p.geo_parcelle\n"
                f"FROM \"{schema}\".cartads_parcelle p\n"
                "WHERE cartads_dossier_parcelle.cartads_parcelle = p.cartads_parcelle "
                "AND cartads_dossier_parcelle.geo_parcelle IS NULL "
            )
            feedback.pushInfo("Récupération du code geo_parcelle terminée")

            # Calcul des géométries des dossiers
            feedback.pushInfo("Lancment du calcul des géométries des dossiers")
            connection.executeSql(
                f"INSERT INTO \"{schema}\".cartads_dossier_geo ("
                "id_dossier, nom_dossier, geom, complete_geom)\n "
                "SELECT id_dossier, nom_dossier, geom, complete_geom\n"
                "FROM (\n"
                "   SELECT cdp.id_dossier, cdp.nom_dossier, ST_UNION(cph.geom) as geom,\n"
                "       COUNT(cdp.cartads_parcelle) AS defined_parcelle,\n"
                "       COUNT(cph.cartads_parcelle) AS found_parcelle,\n"
                "       COUNT(cdp.cartads_parcelle) = COUNT(cph.cartads_parcelle) AS complete_geom\n"
                f"  FROM \"{schema}\".cartads_dossier_parcelle cdp\n"
                f"  LEFT JOIN \"{schema}\".cartads_parcelle_historique cph "
                "ON cdp.cartads_parcelle = cph.cartads_parcelle\n"
                f"  WHERE cdp.id_dossier IN "
                f"({','.join(map(str, dossiers_parcelles) + map(str, nouveaux_dossiers))}) "
                "       AND ST_IsValid(cph.geom)\n"
                "   GROUP BY cdp.id_dossier, cdp.nom_dossier\n"
                ") AS calculate_cdg\n"
                "WHERE found_parcelle > 0\n"
                "ORDER BY id_dossier ASC\n"
                "ON CONFLICT (id_dossier) DO UPDATE\n"
                "SET geom = EXCLUDED.geom, complete_geom = EXCLUDED.complete_geom "
            )
            feedback.pushInfo("Calcul des géométries des dossiers terminée")

        feedback.pushInfo(tr("Updating dossiers into database done"))

        return {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: tr(
                "*** Intégration de dossiers depuis l'API terminée ***"
            ),
        }
