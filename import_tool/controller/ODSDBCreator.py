import datetime
import logging
import sys
from tqdm import tqdm

from sqlalchemy.orm import sessionmaker
# import models
from import_tool.models.Address import Address
from import_tool.models.base import Base
from import_tool.models.CodeSystem import CodeSystem
from import_tool.models.Organisation import Organisation
from import_tool.models.Relationship import Relationship
from import_tool.models.Role import Role
from import_tool.models.Successor import Successor
from import_tool.models.Version import Version
from import_tool.models.Setting import Setting

schema_version = '015'


def convert_string_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d')


class ODSDBCreator(object):

    __ods_xml_data = None
    __code_system_dict = {}

    def __init__(self, engine):
        # Create the SQLAlchemy session
        logger = logging.getLogger(__name__)
        logger.debug("Creating SQLAlchemy session")
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # Creates the tables of all objects derived from our Base object
        metadata = Base.metadata
        metadata.create_all(engine)

    def __create_settings(self):
    
        logger = logging.getLogger(__name__)
        logger.debug("Setting schema version")
        setting = Setting()
        setting.key = 'schema_version'
        setting.value = schema_version
        self.session.add(setting)

    def __create_codesystems(self):
        """Loops through all the code systems in an organisation and adds them
        to the database

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        
        logger = logging.getLogger(__name__)
        logger.debug("Adding codesystem information")

        # these are all code systems, we have a DRY concept here as so much of
        # this code is common, it doesn't make sense to do it 3 times, lets
        # loop
        code_system_types = [
            './CodeSystems/CodeSystem[@name="OrganisationRelationship"]',
            './CodeSystems/CodeSystem[@name="OrganisationRecordClass"]',
            './CodeSystems/CodeSystem[@name="OrganisationRole"]']

        for code_system_type in code_system_types:
            # we are going to need to append a lot of data into this array
            codesystems = {}

            relationships = self.__ods_xml_data.find(code_system_type)
            relationship_types = {}

            # enumerate the iter as it doesn't provide an index which we need
            for idx, relationship in enumerate(relationships.findall('concept')):

                codesystems[idx] = CodeSystem()

                relationship_id = relationship.attrib.get('id')
                display_name = relationship.attrib.get('displayName')
                relationship_types[relationship_id] = display_name

                code_system_type_name = code_system_type
                code_system_type_name = code_system_type_name.replace(
                    './CodeSystems/CodeSystem[@name="', '').replace('"]', '')

                codesystems[idx].id = relationship_id
                codesystems[idx].name = code_system_type_name
                codesystems[idx].displayname = display_name

                # pop these in a global  dictionary, we will use these later in __create_organisations
                self.__code_system_dict[relationship_id] = display_name

                # append this instance of code system to the session
                self.session.add(codesystems[idx])

        primary_role_scope = './Manifest/PrimaryRoleScope'

        primary_role_scopes = self.__ods_xml_data.find(primary_role_scope)

        for idx, primary_role in enumerate(primary_role_scopes.findall('PrimaryRole')):

            codesystems = {}

            codesystems[idx] = CodeSystem()

            primary_role_id = primary_role.attrib.get('id')
            primary_role_display_name = primary_role.attrib.get('displayName')
            code_system_type_name = 'PrimaryRoleScope'

            codesystems[idx].id = primary_role_id
            codesystems[idx].name = code_system_type_name
            codesystems[idx].displayname = primary_role_display_name

            self.session.add(codesystems[idx])

    def __create_organisations(self):
        """Creates the organisations and adds them to the session

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        logger = logging.getLogger(__name__)
        logger.debug("Adding organisation information")

        organisations = {}

        if self.__test_mode:
            test_import_limit = 10
            test_import_count = 0

        for idx, organisation in tqdm(enumerate(self.__ods_xml_data.findall(
                '.Organisations/Organisation'))):

            organisations[idx] = Organisation()

            organisations[idx].odscode = organisation.find('OrgId').attrib.get('extension')

            organisations[idx].name = organisation.find('Name').text

            organisations[idx].status = organisation.find('Status').attrib.get('value')

            organisations[idx].record_class = self.__code_system_dict[organisation.attrib.get('orgRecordClass')]

            organisations[idx].last_changed = organisation.find('LastChangeDate').attrib.get('value')

            organisations[idx].ref_only = bool(organisation.attrib.get('refOnly'))

            for date in organisation.findall('Date'):
                if date.find('Type').attrib.get('value') == 'Legal':

                    try:
                        organisations[idx].legal_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass

                    try:
                        organisations[idx].legal_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

                elif date.find('Type').attrib.get('value') == 'Operational':
                    try:
                        organisations[idx].operational_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass

                    try:
                        organisations[idx].operational_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

            self.session.add(organisations[idx])

            self.__create_addresses(organisations[idx], organisation)

            self.__create_roles(organisations[idx], organisation)

            self.__create_relationships(organisations[idx], organisation)

            self.__create_successors(organisations[idx], organisation)

            if self.__test_mode:
                test_import_count += 1
                if test_import_count > test_import_limit:
                    break

        organisations = None

    def __create_roles(self, organisation, organisation_xml):
        """Creates the roles, this should only be called from
         __create_organisations()

        Parameters
        ----------
        organisation = xml element of the full organisation

        Returns
        -------
        None
        """
        roles_xml = organisation_xml.find('Roles')
        roles = {}

        for idx, role in enumerate(roles_xml):

            roles[idx] = Role()

            roles[idx].organisation_ref = organisation.ref
            roles[idx].org_odscode = organisation.odscode
            roles[idx].code = role.attrib.get('id')
            roles[idx].primary_role = bool(role.attrib.get('primaryRole'))
            roles[idx].status = role.find('Status').attrib.get('value')
            roles[idx].unique_id = role.attrib.get('uniqueRoleId')

            # Add Operational and Legal start/end dates if present
            for date in role.findall('Date'):
                if date.find('Type').attrib.get('value') == 'Legal':
                    try:
                        roles[idx].legal_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass
                    try:
                        roles[idx].legal_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

                elif date.find('Type').attrib.get('value') == 'Operational':
                    try:
                        roles[idx].operational_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass
                    try:
                        roles[idx].operational_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

            self.session.add(roles[idx])

        roles = None

    def __create_relationships(self, organisation, organisation_xml):
        """Creates the relationships, this should only be called from
         __create_organisations()

        Parameters
        ----------
        organisation = xml element of the full organisation

        Returns
        -------
        None
        """
        relationships_xml = organisation_xml.find('Rels')
        relationships = {}

        if relationships_xml is not None:

            for idx, relationship in enumerate(relationships_xml):

                relationships[idx] = Relationship()

                relationships[idx].organisation_ref = organisation.ref
                relationships[idx].org_odscode = organisation.odscode
                relationships[idx].code = relationship.attrib.get('id')
                relationships[idx].target_odscode = relationship.find(
                    'Target/OrgId').attrib.get('extension')
                relationships[idx].status = relationship.find(
                    'Status').attrib.get('value')
                relationships[idx].unique_id = relationship.attrib.get(
                    'uniqueRelId')

                for date in relationship.findall('Date'):
                    if date.find('Type').attrib.get('value') == 'Legal':
                        try:
                            relationships[idx].legal_start_date = \
                                convert_string_to_date(date.find('Start').attrib.get('value'))
                        except:
                            pass
                        try:
                            relationships[idx].legal_end_date = \
                                convert_string_to_date(date.find('End').attrib.get('value'))
                        except:
                            pass

                    elif date.find('Type').attrib.get('value') == 'Operational':
                        try:
                            relationships[idx].operational_start_date = \
                                convert_string_to_date(date.find('Start').attrib.get('value'))
                        except:
                            pass
                        try:
                            relationships[idx].operational_end_date = \
                                convert_string_to_date(date.find('End').attrib.get('value'))
                        except:
                            pass

                # self.__code_system_dict[]

                self.session.add(relationships[idx])

        relationships = None

    def __create_addresses(self, organisation, organisation_xml):

        for idx, location in enumerate(organisation_xml.findall(
                'GeoLoc/Location')):

            address = Address()

            try:
                address.org_odscode = organisation.odscode
            except AttributeError:
                pass

            try:
                address.address_line1 = location.find('AddrLn1').text
            except AttributeError:
                pass

            try:
                address.address_line2 = location.find('AddrLn2').text
            except AttributeError:
                pass

            try:
                address.address_line3 = location.find('AddrLn3').text
            except AttributeError:
                pass

            try:
                address.town = location.find('Town').text
            except AttributeError:
                pass

            try:
                address.county = location.find('County').text
            except AttributeError:
                pass

            try:
                address.post_code = location.find('PostCode').text
            except AttributeError:
                pass

            try:
                organisation.post_code = location.find('PostCode').text
            except AttributeError:
                pass

            try:
                address.country = location.find('Country').text
            except AttributeError:
                pass

            try:
                address.uprn = location.find('UPRN').text
            except AttributeError:
                pass

            self.session.add(address)

    def __create_successors(self, organisation, organisation_xml):

        for idx, succ in enumerate(organisation_xml.findall(
                'Succs/Succ')):

            successor = Successor()

            try:
                successor.unique_id = succ.attrib.get('uniqueSuccId')
            except AttributeError:
                pass

            try:
                successor.org_odscode = organisation.odscode
            except AttributeError:
                pass

            try:
                successor.legal_start_date = \
                    convert_string_to_date(succ.find('Date/Start').attrib.get('value'))
            except AttributeError:
                pass

            try:
                successor.type = \
                    succ.find('Type').text
            except AttributeError:
                pass

            try:
                successor.target_odscode = \
                    succ.find('Target/OrgId').attrib.get('extension')
            except AttributeError:
                pass

            try:
                successor.target_primary_role_code = \
                    succ.find('Target/PrimaryRoleId').attrib.get('id')
            except AttributeError:
                pass

            try:
                successor.target_unique_role_id = \
                    succ.find('Target/PrimaryRoleId').attrib.get('uniqueRoleId')
            except AttributeError:
                pass

            self.session.add(successor)

    def __create_version(self):
        """adds all the version information to the versions table

        Parameters
        ----------
        None
        Returns
        -------
        None
        """

        logger = logging.getLogger(__name__)
        logger.debug("Adding version information")
        version = Version()

        version.file_version = self.__ods_xml_data.find(
            './Manifest/Version').attrib.get('value')
        version.publication_date = self.__ods_xml_data.find(
            './Manifest/PublicationDate').attrib.get('value')
        version.publication_type = self.__ods_xml_data.find(
            './Manifest/PublicationType').attrib.get('value')
        version.publication_seqno = self.__ods_xml_data.find(
            './Manifest/PublicationSeqNum').attrib.get('value')
        version.publication_source = self.__ods_xml_data.find(
            './Manifest/PublicationSource').attrib.get('value')
        version.file_creation_date = self.__ods_xml_data.find(
            './Manifest/FileCreationDateTime').attrib.get('value')
        version.import_timestamp = datetime.datetime.now()
        version.record_count = self.__ods_xml_data.find(
            './Manifest/RecordCount').attrib.get('value')
        version.content_description = self.__ods_xml_data.find(
            './Manifest/ContentDescription').attrib.get('value')

        self.session.add(version)

    def create_database(self, ods_xml_data, test_mode):
        """creates a sqlite database in the current path with all the data

        Parameters
        ----------
        ods_xml_data: xml_tree_parser object required that is valid
        TODO: check validity here
        Returns
        -------
        None
        """
        logger = logging.getLogger(__name__)
        logger.info('Starting import')

        self.__test_mode = test_mode
        self.__ods_xml_data = ods_xml_data
        if self.__ods_xml_data is not None:
            try:
                self.__create_version()
                self.__create_codesystems()
                self.__create_organisations()
                self.__create_settings()

                logger = logging.getLogger(__name__)
                logger.debug("Committing session")
                self.session.commit()

            except Exception as e:
                # If anything fails, let's not commit anything
                logger = logging.getLogger(__name__)
                logger.error("Unexpected error:", sys.exc_info()[0])
                logger.debug("Rolling back...")
                self.session.rollback()
                logger.debug("Rollback complete")
                raise

            finally:
                self.session.close()