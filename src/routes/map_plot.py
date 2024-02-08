"""Module for the `plot map` route"""
import asyncio
from collections import Counter
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LinearRing
from folium import plugins
from src.config import log
from datetime import datetime
import folium
import json
import geojson
import geopandas as gpd
import pandas as pd
import os

async def handler(city: str, period: str) -> (dict, int):
    plot = Plot(city, period)
    output, status = plot.run()
    return output, status


class Plot():
    def __init__(self, city, period):
        self.city = city
        if city == "chicago":
            self.base_map = folium.Map(location=[41.8781, -87.6298], zoom_start=12)
            self.city_name = "Chicago, IL"
        elif city == "london":
            self.base_map = folium.Map(location=[51.507278, -0.127690], zoom_start=12)
            self.city_name = "Greater London, London"
        else:
            self.base_map = folium.Map(location=[40.68402, -73.95704], zoom_start=12)
            self.city_name = "New York City, NY"
        
        if period == "1":
            self.fname = "monthly-jul-2018"
        elif period == "2":
            self.fname = "last-three-months-2018"
        else:
            self.fname = "all-2018"
        
        self.path = f"data/{city}"
        self.map_name = 'templates/map.html'
        self.max_length = 64
        self.max_properties = 10000 #Useful to avoid exceeding the response size limit of Cloud Run (32 MiB)
        self.truncate_n_properties = True
        return


    def get_regions(self):
        with open(f'{self.path}/{self.fname}.geojson','r') as geojson_file:
            regions = geojson.load(geojson_file)
        return regions


    def get_markers(self):
        df = pd.read_csv(f'{self.path}/markers_listings.csv', parse_dates=['last_review'])
        df = df[['id', 'room_type', 'neighbourhood',
                 'latitude', 'longitude', 'price']]

        if self.truncate_n_properties and df.shape[0]>self.max_properties:
           df =  df.sample(n = self.max_properties, random_state=27).reset_index()
        return df


    def update_texts(self, regions):
        for i, r in enumerate(regions["features"]):
            emotions = r["properties"]["display_emotions"].split(', ')
            emotions = [e.split('(', 1)[0] for e in emotions]
            regions["features"][i]["properties"]["display_emotions"] = ', '.join(emotions[:])

            sentiment = r["properties"]["display_sentiment"].split(', ')
            sentiment = [s.split('(', 1)[0] for s in sentiment]
            regions["features"][i]["properties"]["display_sentiment"] = ', '.join(sentiment[:])

            regions["features"][i]["properties"]["short_review"] = r["properties"]["display_review"][:self.max_length]+'... <b>Click to read more!</b>'
            regions["features"][i]["properties"]["display_review"] = r["properties"]["display_review"].replace('\n','<br>')

        return regions


    def plot_region_shapes(self, region_geo_df):
        ######## Add mini map ########    
        minimap = plugins.MiniMap()
        self.base_map.add_child(minimap)


        feature_region = folium.FeatureGroup(name='Neighbourhood Info')

        style_function = lambda x: {
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0
        }

        popup = folium.GeoJsonPopup(
            fields=["display_review"],
            aliases=["Review"],
            localize=True,
            labels=True,
            style="background-color: yellow;",
            max_width=1200
        )

        region_geo_df = self.update_texts(region_geo_df)

        folium.GeoJson(
            region_geo_df,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['display_name','display_emotions','display_sentiment','short_review'],
                aliases=['Neighborhood','Emotions','Sentiment','Review'],
                localize=True,
                sticky=False
            ),
            popup=popup
        ).add_to(feature_region)

        feature_region.add_to(self.base_map)
        return


    def plot_markers(self, df):
        feature_ea = folium.FeatureGroup(name='Entire home/apt')
        feature_pr = folium.FeatureGroup(name='Private room')
        feature_sr = folium.FeatureGroup(name='Shared room')


        locs_geometry = [Point(xy) for xy in zip(df.longitude,
                                         df.latitude)]
        crs = {'init': 'epsg:4326'}
        # Coordinate Reference Systems, "epsg:4326" is a common projection of WGS84 Latitude/Longitude
        locs_gdf = gpd.GeoDataFrame(df, crs=crs, geometry=locs_geometry)

        for i, v in locs_gdf.iterrows():
            popup = """
            Location id : <b>%s</b><br>
            Room type : <b>%s</b><br>
            Price : <b>%d</b><br>
            """ % (v['id'], v['room_type'], v['price'])
            #Neighbourhood : <b>%s</b><br> v['neighbourhood']
            if v['room_type'] == 'Entire home/apt':
                folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                    radius=5,
                                    tooltip=popup,
                                    color='#FFBA00',
                                    fill_color='#FFBA00',
                                    fill=True).add_to(feature_ea)
            elif v['room_type'] == 'Private room':
                folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                    radius=5,
                                    tooltip=popup,
                                    color='#087FBF',
                                    fill_color='#087FBF',
                                    fill=True).add_to(feature_pr)
            elif v['room_type'] == 'Shared room':
                folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                    radius=5,
                                    tooltip=popup,
                                    color='#FF0700',
                                    fill_color='#FF0700',
                                    fill=True).add_to(feature_sr)

        feature_ea.add_to(self.base_map)
        feature_pr.add_to(self.base_map)
        feature_sr.add_to(self.base_map)
        folium.LayerControl(collapsed=False).add_to(self.base_map)
        return


    def run(self):
        ## Plot Regions
        try:
            regions_geojson = self.get_regions()
            log('real-up.map_plot',{'event':'load regions', 'status':'success'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.plot_region_shapes(regions_geojson)
            log('real-up.map_plot',{'event':'plot regions', 'status':'success'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            reason = str(e)
            log('real-up.map_plot',{'event':'load/plot regions', 'status':'fail', 'reason':reason}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"type error": str(e)}, 500

        ## Plot Markers
        try:
            df = self.get_markers()
            log('real-up.map_plot',{'event':'load markers', 'status':'success'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.plot_markers(df)
            log('real-up.map_plot',{'event':'plot markers', 'status':'success'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            reason = str(e)
            log('real-up.map_plot',{'event':'load/plot markers', 'status':'fail', 'reason':reason}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"type error": str(e)}, 500
        
        ## Save Map
        try:
            self.base_map.save(self.map_name)
            log('real-up.map_plot',{'event':'save map', 'status':'success'}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            reason = str(e)
            log('real-up.map_plot',{'event':'save map', 'status':'fail', 'reason':reason}, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"type error": str(e)}, 500

        output = {
            "number_of_markers":df.shape[0],
            "map_name":self.map_name,
            "city":self.city_name
        }
        return output, 200