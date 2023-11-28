from .sql_server import connect

import dask.dataframe as dd
import requests
import shutil

COLUMN_0 = [
    "postcode",
    "status",
    "usertype",
    "easting",
    "northing",
    "positional_quality_indicator",
    "country",
    "latitude",
    "longitude",
    "postcode_no_space",
    "postcode_fixed_width_seven",
    "postcode_fixed_width_eight",
    "postcode_area",
    "postcode_district",
    "postcode_sector",
    "outcode",
    "incode",
    "db_id"
]

COLUMN_1 = [
    "transaction_unique_identifier",
    "price",
    "date_of_transfer",
    "postcode",
    "property_type",
    "new_build_flag",
    "tenure_type",
    "primary_addressable_object_name",
    "secondary_addressable_object_name",
    "street",
    "locality",
    "town_city",
    "district",
    "county",
    "ppd_category_type",
    "record_status",
    "db_id"
]

COLUMN_2 = [
    "price",
    "date_of_transfer",
    "postcode",
    "property_type",
    "latitude",
    "longitude",
    "db_id"
]

TABLE_SCHEMA = '''CREATE TABLE IF NOT EXISTS `prices_coordinates_data` (
  `price` int(10) unsigned NOT NULL,
  `date_of_transfer` date NOT NULL,
  `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
  `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(10,8) NOT NULL,
  `db_id` bigint(20) unsigned NOT NULL
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;'''

@connect
def create_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS `prices_coordinates_data`;")
        cursor.execute(TABLE_SCHEMA)
        cursor.execute("ALTER TABLE `prices_coordinates_data` ADD PRIMARY KEY (`db_id`);")
        cursor.execute("ALTER TABLE `prices_coordinates_data` MODIFY db_id bigint(20) unsigned \
                        NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;")
    connection.commit()

URL_0 = "https://www.getthedata.com/downloads/open_postcode_geo.csv.zip"
URL_1 = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv"

@connect
def load_data(connection):

    r = requests.get(URL_0)
    with open("open_postcode_geo.csv.zip", 'wb') as f:
        f.write(r.content)
    import zipfile
    with zipfile.ZipFile("open_postcode_geo.csv.zip", "r") as z:
        z.extractall("temp_data_0")

    r = requests.get(URL_1)
    with open("temp_data_1.csv", 'wb') as f:
        f.write(r.content)

    table_0 = dd.read_csv("temp_data_0/open_postcode_geo.csv", header=None,
                         names=COLUMNS_0, dtype={a: str for a in COLUMNS_0}) \
                         [COLUMN_1[:-1]]  # this is to force db_id from dataset 1

    table_1 = dd.read_csv("temp_data_1.csv", header=None,
                         names=COLUMNS_1, dtype={a: str for a in COLUMNS_1})

    table_2 = dd.merge(table0, table1, on='postcode', how='inner') \
        .iloc[table_2["ppd_category_type"] == "A"][COLUMNS_2]

    table_2.to_csv("temp_data_2.csv", single_file=True)

    with connection.cursor() as cursor:
        cursor.execute("LOAD DATA LOCAL INFILE 'temp_data_2.csv' \
                        INTO TABLE `prices_coordinates_data` \
                        FIELDS TERMINATED BY ',' \
                        OPTIONALLY ENCLOSED by '\"' \
                        LINES STARTING BY '' \
                        TERMINATED BY '\\n';")
    connection.commit()
    shutil.rmtree("./temp_data_0")
    os.remove("temp_data_1.csv")
    #os.remove("temp_data_2.csv")