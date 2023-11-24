from .sql_server import connect

import os
import requests
import zipfile

TABLE_SCHEMA = '''CREATE TABLE IF NOT EXISTS `postcode_data` (
  `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
  `status` enum('live','terminated') NOT NULL,
  `usertype` enum('small', 'large') NOT NULL,
  `easting` int unsigned,
  `northing` int unsigned,
  `positional_quality_indicator` int NOT NULL,
  `country` enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(10,8) NOT NULL,
  `postcode_no_space` tinytext COLLATE utf8_bin NOT NULL,
  `postcode_fixed_width_seven` varchar(7) COLLATE utf8_bin NOT NULL,
  `postcode_fixed_width_eight` varchar(8) COLLATE utf8_bin NOT NULL,
  `postcode_area` varchar(2) COLLATE utf8_bin NOT NULL,
  `postcode_district` varchar(4) COLLATE utf8_bin NOT NULL,
  `postcode_sector` varchar(6) COLLATE utf8_bin NOT NULL,
  `outcode` varchar(4) COLLATE utf8_bin NOT NULL,
  `incode` varchar(3)  COLLATE utf8_bin NOT NULL,
  `db_id` bigint(20) unsigned NOT NULL
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;'''

@connect
def create_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS `postcode_data`;")
        cursor.execute(TABLE_SCHEMA)
        cursor.execute("ALTER TABLE `postcode_data` ADD PRIMARY KEY (`db_id`);")
        cursor.execute("ALTER TABLE `postcode_data` MODIFY db_id bigint(20) unsigned \
                        NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;")
    connection.commit()

URL = "https://www.getthedata.com/downloads/open_postcode_geo.csv.zip"

@connect
def load_data(connection):
    r = requests.get(URL)
    with open("temp_data.csv.zip", 'wb') as f:
        file.write(r.content)
    import zipfile
    with zipfile.ZipFile("temp_data.csv.zip", "r") as z:
        z.extractall()
    cursor.execute("LOAD DATA LOCAL INFILE 'temp_data.csv' \
                    INTO TABLE `postcode_data` \
                    FIELDS TERMINATED BY ',' \
                    OPTIONALLY ENCLOSED by '\"' \
                    LINES STARTING BY '' \
                    TERMINATED BY '\\n';")
    cursor.commit()
    os.remove("temp_data.csv")