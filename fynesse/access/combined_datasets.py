from .sql_server import connect

TABLE_SCHEMA = '''CREATE TABLE IF NOT EXISTS `prices_coordinates_data` (
  `price` int(10) unsigned NOT NULL,
  `date_of_transfer` date NOT NULL,
  `postcode` varchar(8) COLLATE utf8_bin NOT NULL,
  `property_type` varchar(1) COLLATE utf8_bin NOT NULL,
  `new_build_flag` varchar(1) COLLATE utf8_bin NOT NULL,
  `tenure_type` varchar(1) COLLATE utf8_bin NOT NULL,
  `locality` tinytext COLLATE utf8_bin NOT NULL,
  `town_city` tinytext COLLATE utf8_bin NOT NULL,
  `district` tinytext COLLATE utf8_bin NOT NULL,
  `county` tinytext COLLATE utf8_bin NOT NULL,
  `country` enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
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

@connect
def load_data(connection):
    r = requests.get(URL)
    with open("open_postcode_geo.csv.zip", 'wb') as f:
        f.write(r.content)
    import zipfile
    with zipfile.ZipFile("open_postcode_geo.csv.zip", "r") as z:
        z.extractall("temp_data")
    with connection.cursor() as cursor:
        cursor.execute("LOAD DATA LOCAL INFILE 'temp_data/open_postcode_geo.csv' \
                        INTO TABLE `postcode_data` \
                        FIELDS TERMINATED BY ',' \
                        OPTIONALLY ENCLOSED by '\"' \
                        LINES STARTING BY '' \
                        TERMINATED BY '\\n';")
    connection.commit()
    shutil.rmtree("./temp_data")