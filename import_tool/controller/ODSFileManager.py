from lxml import etree as xml_tree_parser
import logging
import os.path
import sys
import urllib.request
import zipfile


class ODSFileManager(object):

    __ods_xml_data = None
    __ods_schema = None
   
    def __init__(self, xml_file_path, schema_file_path, xml_url=None, schema_url=None):
        log = logging.getLogger(__name__)
        try:
            self.xml_file_path = xml_file_path
            log.debug('xml_file_path is %s' % self.xml_file_path)

            self.schema_file_path = schema_file_path
            log.debug('schema_file_path is %s' % self.schema_file_path)

            # If the xml_url has been passed in to the constructor, we will retrieve the zip file from the remote url
            if xml_url:
                self.__local_mode = False
                self.schema_url = schema_url
                log.debug('schema_url is %s' % self.schema_url)
                self.xml_url = xml_url
                log.debug('xml_url is %s' % self.xml_url)

            # Otherwise we will set local_mode which will skip the download and just look for the zip file locally
            else:
                self.__local_mode = True

        except Exception as e:
            log.error(e)

    def __return_attribute(self, attribute_name):
        pass

    def __retrieve_latest_schema_file(self):
        """Retrieve the latest published schema file from a publicly-accessible published location

        Parameters
        ----------
        None
        
        Returns
        -------
        String: Filename if found
        """

        file_name = self.schema_file_path
        tmp_file_name = str.format("%s.tmp" % file_name)

        # If we are not running in local mode, we attempt to download the latest schema zip file first.
        if not self.__local_mode:
            url = self.schema_url

            with urllib.request.urlopen(url) as response:
                # Download the file and save it to a temporary file name
                with open(tmp_file_name) as out_file:
                    log = logging.getLogger(__name__)
                    log.info("Downloading schema")
                    out_file.write(response.read())

                    # Check that the temporary file has downloaded properly
                    if os.path.isfile(tmp_file_name):
                        # If the data file already exists, remove it
                        if os.path.isfile(file_name):
                            os.remove(file_name)
                        # Rename the temporary download file to the xml file name
                        os.rename(tmp_file_name, file_name)
                        log.info("Schema download complete")
                        print(file_name)
                        return file_name
                    else:
                        raise ValueError('Unable to locate the schema file')

        # If we are running in local mode, we simply check that the zip file is already present locally
        # and return the file name
        else:
            if os.path.isfile(file_name):
                return file_name

    def __retrieve_latest_datafile(self):
        """The purpose of this function is to retrieve the latest
        published file from a public published location

        Parameters
        ----------
        None
        
        Returns
        -------
        String: Filename if found
        """

        file_name = self.xml_file_path
        tmp_file_name = str.format("%s.tmp" % file_name)

        # If we are not running in local mode, we attempt to download the latest zip file first
        if not self.__local_mode:
            url = self.xml_url

            with urllib.request.urlopen(url) as response:
                # Download the file and save it to a temporary file name
                with open(tmp_file_name) as out_file:
                    log = logging.getLogger(__name__)
                    log.info("Downloading data")
                    out_file.write(response.read())

                    # Check that the temporary file has downloaded properly
                    if os.path.isfile(tmp_file_name):
                        # If the data file already exists, remove it
                        if os.path.isfile(file_name):
                            os.remove(file_name)
                        # Rename the temporary download file to the xml file name
                        os.rename(tmp_file_name, file_name)
                        log.info("Download complete")
                        return file_name
                    else:
                        raise ValueError('Unable to locate the data file')

        # If we are running in local mode, We check that the data zip file is present locally
        # and return the file name
        else:
            if os.path.isfile(file_name):
                return file_name

    def __retrieve_latest_schema(self, schema_filename):
        """Get the latest XSD for the ODS XML data and return it as an
        XMLSchema object

        Parameters
        ----------
        None

        Returns
        -------
        xml_schema: the ODS XSD as an XMLSchema object
        """
        try:
            print(schema_filename)
            with zipfile.ZipFile(schema_filename) as local_zipfile:
                # get to the name of the actual zip file
                zip_info = local_zipfile.namelist()
                print(zip_info)

                # extract the schema file from the zip
                with local_zipfile.open('HSCOrgRefData.xsd') as f:
                    doc = xml_tree_parser.parse(f)
                    return xml_tree_parser.XMLSchema(doc)

        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

    def __import_latest_datafile(self, data_filename):
        """Determine if we have a zip file or xml file, check that it is valid,
        and then populate an etree object that we can parse

        Parameters
        ----------
        String: filename of the zip file containing the xml
        
        Returns
        -------
        None
        """
        log = logging.getLogger(__name__)
        log.debug(f'Data filename is {data_filename}')
        try:
            with zipfile.ZipFile(data_filename) as local_zipfile:
                # get to the name of the actual zip file
                zip_info = local_zipfile.namelist()

                # extract the first file in the zip, assumption there will be
                # only one
                with local_zipfile.open(zip_info[0]) as local_datafile:
                    log.debug("Loading data")
                    self.__ods_xml_data = xml_tree_parser.parse(local_datafile)

        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise

    def __validate_xml_against_schema(self):
        try:
            log = logging.getLogger(__name__)
            log.debug("Validating data against schema")

            doc = self.__ods_xml_data
            schema = self.__ods_schema
            valid = schema.validate(doc)

            if not valid:
                raise Exception("XML file is not valid against the schema")

            else:
                log = logging.getLogger(__name__)
                log.debug("Data is valid against schema")
                return valid

        except Exception as e:
            raise
            sys.exit(1)

    def get_latest_xml(self):
        """Check if we have ODS xml data. If we don't we should retrieve the latest version available and
        explode it from zip format into a xmltree object

        Parameters
        ----------
        None
        
        Returns
        -------
        xml_tree_parser: containing the entire xml dataset
        """

        if self.__ods_schema is None:
            schema_filename = self.__retrieve_latest_schema_file()
            self.__ods_schema = self.__retrieve_latest_schema(schema_filename)

        if self.__ods_xml_data is None:
            data_filename = self.__retrieve_latest_datafile()
            self.__import_latest_datafile(data_filename)
            self.__validate_xml_against_schema()
        log = logging.getLogger(__name__)
        log.info("Data loaded")
        return self.__ods_xml_data
