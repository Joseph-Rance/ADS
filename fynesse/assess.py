from .config import config

import matplotlib.pyplot as plt
import osmnx as ox
import geopandas as gpd
from math import log
from geopy import distance


def plot_poi_data(poi_data, tag_idx, tag_names, ax=None):

    if not ax:
        ax = plt

    ax.set_title(("closest " if tag_idx%2 == 0 else "second closest ") + "/".join(tag_names[tag_idx // 2].split("=")))

    x, y = [], []
    for data_idx, _ in enumerate(poi_data):
        v = [i for l in poi_data[data_idx][1].values() for i in l][tag_idx]  # flatten data so we can directly index
                                                                             # the distance of the tag we want
        if v != 10 and poi_data[data_idx][0] <= 1_000_000:  # 10 is the default value (i.e. no close instances), and houses
            y.append(poi_data[data_idx][0])                 # more than £1,000,000 make the graphs confusing
            x.append(log(v))

    if not x:
        return  # if we have no instances of the facility nearby, return now

    dist_design = np.array([[1, i] for i in x])
    basis = sm.OLS(np.array(y), dist_design).fit()

    xn = np.concatenate((np.ones((50, 1)), np.linspace(-4, 1, 50).reshape(-1, 1)), axis=1)
    yn = basis.get_prediction(xn).summary_frame(alpha=0.05)

    ax.scatter(x, y, color="red", alpha=0.3)
    ax.plot(xn, yn['mean'], color='blue', linestyle='--', zorder=1)
    ax.fill_between(np.linspace(-4, 1, 50), yn['obs_ci_lower'], yn['obs_ci_upper'], color='cyan', alpha=0.3, zorder=1)
    ax.set_ylim(-0.5e6, 1.5e6)
    ax.set_xlabel("distance (log scale)")
    ax.set_ylabel("price (£)")









def view_on_map(n, s, e, w, ps):
    fig, ax = plt.subplots()

    graph = ox.graph_from_bbox(n, s, e, w)
    nodes, edges = ox.graph_to_gdfs(graph)

    edges.plot(ax=ax, linewidth=1, edgecolor="lightgray")

    ax.set_xlim([w, e])
    ax.set_ylim([s, n])
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")

    ax.scatter([float(i[2]) for i in ps], [float(i[1]) for i in ps], c="red", alpha=0.25, zorder=10,
            s=[float(i[0])/max([float(i[0]) for i in ps])*200 for i in ps], edgecolors="none")
    plt.tight_layout()
    plt.show()

def view_on_uk(n, s, e, w, ps):
    # unfortunately the osm outline for uk includes maritime borders so we will have to go with this low res version
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    ax = world[world.name == 'United Kingdom'].plot(color='white', edgecolor='black')

    ax.set_xlim([west, east])
    ax.set_ylim([south, north])
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")

    ax.scatter([float(i[2]) for i in data_uk], [float(i[1]) for i in data_uk], c="red", alpha=0.25, zorder=10,
            s=[float(i[0])/max([float(i[0]) for i in data_uk])*200 for i in data_uk], edgecolors="none")
    plt.tight_layout()
    plt.show()

TAGS = {"leisure": True, "shop": True, "school:trust": True, "school:type": True, "school:boarding": True,
        "school:gender": True, "school:selective": True}

def get_closest_pois(p):

    # cap at ~2km since this is driving distance
    pois = ox.geometries_from_bbox(float(p[0]) + 0.02, float(p[0]) - 0.02, float(p[1]) - 0.02, float(p[1]) + 0.02, TAGS)

    closest_shop = second_closest_shop = closest_leisure = closest_school = log(2.2)

    for index, row in pois.iterrows():

        d = log(distance.distance((row["geometry"].centroid.y, row["geometry"].centroid.x), (float(p[0]), float(p[1]))).km)

        try:
            if row["shop"] != "NaN":
                if d < closest_shop:
                    second_closest_shop = closest_shop
                    closest_shop = d
                elif d < second_closest_shop:
                    second_closest_shop = d
        except:
            pass

        try:
            if row["leisure"] != "NaN":
                closest_leisure = min(closest_leisure, d)
        except:
            pass

        try:
            if row["amenity"] != "NaN":  # school
                closest_leisure = min(closest_school, d)
        except:
            pass

    return closest_shop, second_closest_shop, closest_leisure, closest_school
