from .config import config

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

    # cap at 2km since this is driving distance
    pois = ox.geometries_from_bbox(float(p[1]) + 0.02, float(p[1]) - 0.02, float(p[2]) - 0.02, float(p[2]) + 0.02, TAGS)

    closest_shop = second_closest_shop = closest_leisure = closest_school = log(2.2)

    for index, row in pois.iterrows():

        d = log(distance.distance((row["geometry"].centroid.y, row["geometry"].centroid.x), (float(p[1]), float(p[2]))).km)

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