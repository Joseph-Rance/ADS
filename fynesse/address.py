from . import assess

import datetime

type_encodings = {
    "F": [1,0,0,0,0], "S": [0,1,0,0,0], "D": [0,0,1,0,0], "T": [0,0,0,1,0], "O": [0,0,0,0,1]
}

def predict_price(latitude, longitude, date, property_type):

    dataset = fynesse.access.sql_server.query_table(f"SELECT p.price, l.latitude, l.longitude, p.date_of_transfer, p.property_type \
                                              FROM `pp_data` as p \
                                               INNER JOIN `postcode_data` as l \
                                               ON p.postcode = l.postcode AND 0.0001 > \
                                               POWER(l.latitude - {latitude}, 2) + POWER(l.longitude - {longitude}, 2);")

    x = []
    y = []

    for price, lat, lon, t_date, p_type in dataset:

        y.append(float(price))

        x.append([1] \
               + type_encodings[p_type] \
               + list(assess.get_closest_pois((lat, lon))) \
               + (datetime.strptime(t_date, '%y/%m/%d') - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60))

    basis = sm.OLS(np.array(y), np.array(x))
    results_basis = basis.fit()

    features = np.array([[1] \
               + type_encodings[property_type] \
               + list(assess.get_closest_pois((latitude, longitude))) \
               + (datetime.strptime(date, '%y/%m/%d')  - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60)])

    pred = results_basis.get_prediction(features).summary_frame(alpha=0.05)

    if results_basis.rsquared < 0:
        print("warning: poor prediction accuracy likely")

    return pred, results_basis.rsquared