from .config import config

from math import log
import datetime
from geopy import distance
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import osmnx as ox
import statsmodels.api as sm

def plot_poi_data(poi_data, tag_idx, tag_names, ax=plt):

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

def plot_country(country):

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    return world[world.name == country].plot(color='white', edgecolor='black')

def scatter_prices_lat_lon(lat_lon_data, bounds, ax=plt):

    cmap = plt.cm.jet
    norm = matplotlib.colors.Normalize(vmin=min([float(i[0]) for i in lat_lon_data]), vmax=max([float(i[0]) for i in lat_lon_data]))

    ax.scatter([float(i[2]) for i in lat_lon_data], [float(i[1]) for i in lat_lon_data],
                alpha=0.1, zorder=10, c=cmap(norm([float(i[0]) for i in lat_lon_data])), edgecolors="none", cmap=plt.cm.rainbow)
    plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), label="price (£)")  # for some reason this doesn't work with existing axes

    plt.title("Prices against location")

    plt.xlim([bounds["west"], bounds["east"]])
    plt.ylim([bounds["south"], bounds["north"]])
    plt.xlabel("longitude")
    plt.ylabel("latitude")

def plot_roads(bounds, ax=plt):

    graph = ox.graph_from_bbox(bounds["north"], bounds["south"], bounds["east"], bounds["west"])
    nodes, edges = ox.graph_to_gdfs(graph)
    edges.plot(ax=ax, linewidth=1, edgecolor="lightgray")

def get_matrix(data, f):

    out = np.zeros((len(data), len(data)))

    for i, a in enumerate(data):
        for j, b in enumerate(data):
            out[i, j] = f(a, b)

    return out

def plot_prices_distances(prices, distances, max_distance, ax=plt):
    flat_prices = [0.]
    flat_distances = [0]

    for i in range(prices.shape[0]):
        for j in range(0, i):
            if distances[i, j] < max_distance:
                flat_prices.append(prices[i, j])
                flat_distances.append(distances[i, j])

    ax.scatter(flat_distances, flat_prices)

def scatter_prices_date(date_data, ax=plt):
    prices = np.array([float(i[0]) for i in date_data])
    dates = np.array([(i[1] - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60) for i in date_data])
    ax.scatter(dates, prices, zorder=2, alpha=0.2)

def model_prices_date(date_data, ax=plt):

    prices = np.array([float(i[0]) for i in date_data])
    dates = np.array([(i[1] - datetime.date(1995, 1, 1)).total_seconds() // (30*24*60*60) for i in date_data])
    dates_design = np.array([[1, i] for i in dates])

    basis = sm.OLS(prices, dates_design).fit()

    x = np.concatenate((np.ones((50, 1)), np.linspace(dates.min(), dates.max(), 50).reshape(-1, 1)), axis=1)
    y = basis.get_prediction(x).summary_frame(alpha=0.05)

    ax.plot(x, y['mean'], color='cyan',linestyle='--',zorder=1)
    ax.fill_between(np.linspace(dates.min(), dates.max(), 50), y['obs_ci_lower'], y['obs_ci_upper'],
                    color='cyan', alpha=0.3, zorder=1)