import argparse
import logging
import time
import sys

from import_tool.controller.ODSFileManager import ODSFileManager

from import_tool.controller.ODSDBCreator import ODSDBCreator
from sqlalchemy import create_engine

# Set up logging
log_format = "%(asctime)s|OpenODS-Import|%(levelname)s|%(message)s"
formatter = logging.Formatter(log_format)
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

# Set up the command line arguments
parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbose", action="store_true",
                    help="run the import in verbose mode")
parser.add_argument("-d", "--dbms", choices=["sqlite", "postgres"],
                    help="the DBMS to use (defaults to SQLite)")
parser.add_argument("-l", "--local", action="store_true",
                    help="skip the XML data file download and use a local copy")
parser.add_argument("-x", "--xml", type=str,
                    help="specify the path to the local XML data file")
parser.add_argument("-s", "--schema", type=str,
                    help="specify the path to the local XSD schema file")
parser.add_argument("-u", "--data_url", type=str,
                    help="specify the url to the official XML data file")
parser.add_argument("-w", "--schema_url", type=str,
                    help="specify the url to the official XML schema file")
parser.add_argument("-c", "--connection", type=str,
                    help="specify the connection string for the database engine")
parser.add_argument("-t", "--testdb", action="store_true",
                    help="create a db with only 10 records for use in testing")

args = parser.parse_args()

# Set the logging level based on --verbose parameter
if args.verbose:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)

# Set local mode based on command line parameters
if args.local:
    local_mode = args.local
else:
    log.info("Download mode is not currently available due to the publicly-accessible source data being removed. Please"
             "download the source data manually, and then re-run with the local switch e.g. 'python import.py -l'")
    sys.exit(1)

# Set the XML file path if specified, otherwise use default
if args.xml:
    xml_file_path = args.xml
    log.debug("XML parameter provided: %s" % xml_file_path)
else:
    xml_file_path = 'data/fullfile.zip'

# Set the schema file path if specified, otherwise use default
if args.schema:
    schema_file_path = args.schema
    log.debug("Schema parameter provided: %s" % schema_file_path)
else:
    schema_file_path = 'data/ancilliary.zip'

# Set the data file url if specified, otherwise use default
if args.data_url:
    xml_url_path = args.data_url
    log.debug("URL parameter provided: %s" % xml_url_path)
else:
    xml_url_path = 'http://systems.hscic.gov.uk/data/ods/interfacechanges/fullfile.zip'

# Set the schema file url if specified, otherwise use default
if args.schema_url:
    schema_url_path = args.schema_url
    log.debug("URL parameter provided: %s" % schema_url_path)
else:
    schema_url_path = 'https://digital.nhs.uk/media/971/ancilliary/zip/ancilliary'

# Set the connection string using command line parameter
if args.connection:
    connection_string = args.connection
    log.debug("Connection parameter provided: %s" % connection_string)
else:
    connection_string = None

if args.testdb:
    test_mode = True
    log.debug("Running in test mode")
else:
    test_mode = False

log.debug("Running in verbose mode")

if local_mode:
    log.debug("Running in local mode")

    # Instantiate an instance of the ODSFileManager to get us the validated XML data to work with
    File_manager = ODSFileManager(xml_file_path=xml_file_path,
                                  schema_file_path=schema_file_path)
else:
    log.debug("Running in download mode")
    # Instantiate an instance of the ODSFileManager to get us the validated XML data to work with
    File_manager = ODSFileManager(xml_file_path=xml_file_path,
                                  schema_file_path=schema_file_path,
                                  xml_url=xml_url_path,
                                  schema_url=schema_url_path)
    

def get_engine():

    # Create the SQLAlchemy engine based on command line parameter (default to sqlite)
    log.debug("Creating SQLAlchemy engine")

    if args.dbms == "sqlite":
        log.debug("Using SQLite")
        db_engine = create_engine(connection_string or 'sqlite:///openods.sqlite', echo=False)

    elif args.dbms == "postgres":
        log.debug("Using PostgreSQL")
        db_engine = create_engine(connection_string or "postgresql://openods:openods@localhost/openods", isolation_level="READ UNCOMMITTED")

    elif args.dbms is None:
        log.debug("No DBMS specified - using SQLite")
        db_engine = create_engine(connection_string or 'sqlite:///openods.sqlite', echo=False)

    return db_engine


if __name__ == '__main__':

    total_start_time = time.time()
    
    # Get the XML data
    ods_xml_data = File_manager.get_latest_xml()
    
    log.debug('Data Load Time = %s', time.strftime(
        "%H:%M:%S", time.gmtime(time.time() - total_start_time)))

    # Get a database engine (according to specified command line argument
    engine = get_engine()

    import_start_time = time.time()
    
    # Do the import into the empty database
    ODSDBCreator(engine).create_database(ods_xml_data, test_mode)
    
    log.debug('Data Processing Time = %s', time.strftime(
        "%H:%M:%S", time.gmtime(time.time() - import_start_time)))

    log.debug('Total Import Time = %s', time.strftime(
        "%H:%M:%S", time.gmtime(time.time() - total_start_time)))

    log.info("Database import finished")

