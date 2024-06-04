import numpy as np

# Haversine Distance を計算する関数
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance (in kilometers) between two points
    on the Earth's surface given their latitude and longitude in decimal degrees.
    """
    # Convert decimal degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Earth radius in kilometers
    earth_radius = 6371.0

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = earth_radius * c

    return distance
