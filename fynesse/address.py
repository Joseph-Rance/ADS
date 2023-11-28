from . import assess

features: type (OHE), distance to shops, date

type_encodings = {
    "F": [1,0,0,0,0], "S": [0,1,0,0,0], "D": [0,0,1,0,0], "T": [0,0,0,1,0], "O": [0,0,0,0,1]
}

def predict_price(latitude, longitude, date, property_type):
    pois = assess.get_closest_pois((latitude, longitude))

    features = type_encodings[property_type] + list(pois) + (i[1] - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60)