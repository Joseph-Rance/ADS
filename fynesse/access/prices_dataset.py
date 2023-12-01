from .sql_server import connect

import tqdm
import os
import requests

# source: https://github.com/dalepotter/uk_property_price_data/blob/master/create_db.sql
TABLE_SCHEMA = '''CREATE TABLE IF NOT EXISTS `pp_data` (
  `transaction_unique_identifier` tinytext COLLATE utf8_bin NOT NULL,
  `price` int(10) unsigned NOT NULL,
  `date_of_transfer` date NOT NULL,
  `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
  `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
  `new_build_flag` varchar(1) COLLATE utf8_bin NOT NULL,
  `tenure_type` varchar(1) COLLATE utf8_bin NOT NULL,
  `primary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
  `secondary_addressable_object_name` tinytext COLLATE utf8_bin NOT NULL,
  `street` tinytext COLLATE utf8_bin NOT NULL,
  `locality` tinytext COLLATE utf8_bin NOT NULL,
  `town_city` tinytext COLLATE utf8_bin NOT NULL,
  `district` tinytext COLLATE utf8_bin NOT NULL,
  `county` tinytext COLLATE utf8_bin NOT NULL,
  `ppd_category_type` varchar(2) COLLATE utf8_bin NOT NULL,
  `record_status` varchar(2) COLLATE utf8_bin NOT NULL,
  `db_id` bigint(20) unsigned NOT NULL
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;'''

@connect
def create_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS `pp_data`;")
        cursor.execute(TABLE_SCHEMA)
        cursor.execute("ALTER TABLE `pp_data` ADD PRIMARY KEY (`db_id`);")
        cursor.execute("ALTER TABLE `pp_data` MODIFY db_id bigint(20) unsigned \
                        NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;")
    connection.commit()

# Contains HM Land Registry data © Crown copyright and database right 2021.
# This data is licensed under the Open Government Licence v3.0.
URL = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-{year}-part{part}.csv"

@connect
def load_data(connection):
    sess = requests.Session()
    with connection.cursor() as cursor:
        for year in tqdm.tqdm(range(1995, 2024)):
            for part in [1, 2]:
                r = sess.get(URL.format(year=year, part=part))
                with open("temp_data.csv", 'wb') as f:
                    f.write(r.content)
                cursor.execute("LOAD DATA LOCAL INFILE 'temp_data.csv' \
                                INTO TABLE `pp_data` \
                                FIELDS TERMINATED BY ',' \
                                OPTIONALLY ENCLOSED by '\"' \
                                LINES STARTING BY '' \
                                TERMINATED BY '\\n';")
    connection.commit()
    os.remove("temp_data.csv")