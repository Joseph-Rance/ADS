from . import assess
from .access import sql_server, osm

import datetime
import numpy as np
import statsmodels.api as sm

TYPE_ENCODINGS = {
    "F": [1,0,0,0,0], "S": [0,1,0,0,0], "D": [0,0,1,0,0], "T": [0,0,0,1,0], "O": [0,0,0,0,1]
}

TAGS = {"amenity": ["college", "nightclub"], "building": "office", "railway": "station"}
TAG_NAMES = ["amenity=college", "amenity=nightclub", "building=office", "railway=station"]

def predict_price(latitude, longitude, date, property_type, dataset=None):  # we can pass a dataset in for debugging

    if dataset is None:
        dataset = sql_server.query_table(f"SELECT price, latitude, longitude, date_of_transfer, property_type \
                                           FROM `prices_coordinates_data` \
                                           WHERE 0.0068 > POWER(latitude - {latitude}, 2) + POWER(longitude - {longitude}, 2) \
                                           LIMIT 100;")

    if len(dataset) < 20:
        print("warning: poor prediction accuracy likely")

    x, y = [], []

    for r in dataset:
        
        t_closest_pois = osm.get_closest_pois((None, r[1], r[2]), TAGS, TAG_NAMES)
        t_closest_pois = [t_closest_pois[n][0] for n in TAG_NAMES]  # can't just iterate over .values() because that might
                                                                    # not be always same order (I think)

        t_date, t_property_type = r[3], r[4]

        y.append(float(r[0]))

        x.append([1] \
               + TYPE_ENCODINGS[t_property_type] \
               + t_closest_pois \
               + [(datetime.datetime.strptime(t_date, '%Y-%m-%d 00:00').date() - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60)])

    basis = sm.OLS(np.array(y), np.array(x))
    results_basis = basis.fit()

    closest_pois = osm.get_closest_pois((None, latitude, longitude), TAGS, TAG_NAMES)
    closest_pois = [closest_pois[n][0] for n in TAG_NAMES]

    features = np.array([1] \
                      + TYPE_ENCODINGS[property_type] \
                      + closest_pois \
                      + [(datetime.datetime.strptime(date, '%Y-%m-%d 00:00').date()  - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60)])

    pred = results_basis.get_prediction(np.array([features])).summary_frame(alpha=0.05)

    if results_basis.rsquared < 0.5:
        print("warning: poor prediction accuracy likely")

    return pred["mean"], results_basis.rsquared
