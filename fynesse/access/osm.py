from geopy import distance
import osmnx as ox


def get_closest_pois(point, tags, tag_names):

    # ~2km radius seems reasonable
    pois = ox.features.features_from_bbox(float(point[1]) + 0.02, float(point[1]) - 0.02,
                                          float(point[2]) - 0.02, float(point[2]) + 0.02, tags)

    distances = {n:[10, 10] for n in tag_names}  # first and second closest distances in km

    for _, row in pois.iterrows():

        # using straight distance not walking distance because it is generally very similar
        d = distance.distance((row["geometry"].centroid.y, row["geometry"].centroid.x), (float(point[1]), float(point[2]))).km

        for k in tags.keys():
            if k not in row.keys():
                continue
            # if the row is an instance of feature k
            if tags.get(k, False) != True and (row[k] == tags.get(k, []) or type(tags.get(k, [])) != str and row[k] in tags.get(k, [])):
                if distances[k+"="+row[k]][0] > d:
                    distances[k+"="+row[k]] = [d, distances[k+"="+row[k]][0]]
                else:
                    distances[k+"="+row[k]][1] = min(distances[k+"="+row[k]][1], d)

    return distances