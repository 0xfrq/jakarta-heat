"""Run with installed QGIS Python; creates an auditor project without opening a GUI."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['GDAL_PAM_ENABLED']='NO'
from pathlib import Path
from qgis.core import (QgsApplication,QgsProject,QgsVectorLayer,QgsRasterLayer,
                       QgsFillSymbol,QgsLineSymbol,QgsSingleSymbolRenderer)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/qa/agent2'
app=QgsApplication([],False)
app.initQgis()
project=QgsProject.instance()
project.setTitle('Agent2 GIS QA | provisional model outputs | EPSG32748')
tree=project.layerTreeRoot()
inputs=tree.addGroup('01 Master and sources')
qa=tree.addGroup('02 Investigate 226 missing and 66 far snaps')
roads_group=tree.addGroup('02b Walking road context (read-only main repo)')
models=tree.addGroup('03 Agent3 frozen provisional maps')
rasters=tree.addGroup('04 Real 2024 satellite rasters')


def add(path,name,group,layer=None,raster=False):
    uri=str(path)+(f'|layername={layer}' if layer else '')
    obj=QgsRasterLayer(uri,name) if raster else QgsVectorLayer(uri,name,'ogr')
    if not obj.isValid():raise RuntimeError(f'Invalid QGIS layer {uri}')
    project.addMapLayer(obj,False);group.addLayer(obj)
    return obj


grid=add(ROOT/'data/processed/grid_500m_jakarta.gpkg','Master grid 500m clipped',inputs)
grid.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'240,240,240,255','outline_color':'160,160,160,255','outline_width':'0.05'}))
cities=add(ROOT/'data/processed/jakarta_5kota.gpkg','Five mainland cities',inputs)
cities.renderer().setSymbol(QgsFillSymbol.createSimple({'style':'no','outline_color':'20,20,20,255','outline_width':'0.3'}))
parks=add(ROOT/'data/processed/parks_jakarta.gpkg','OSM candidate parks, public access unverified',inputs)
parks.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'30,130,70,255','outline_style':'no'}))
for layer,title in [('grid_area','Clipped analysis areas'),('unreachable','226 routes not computed'),
                    ('far_snap','66 far-snap cells'),('far_snap_grid_points','Far-snap origin points'),
                    ('far_snap_nodes','Snapped road nodes'),('far_snap_connectors','Unverified straight connectors'),
                    ('eastern_lst_coverage','Eastern LST coverage anomalies'),
                    ('original_park_polygons','Original park polygons recovered from cache'),
                    ('explicit_restricted_osm_nodes','Explicit node restrictions (unverified OSM tags)')]:
    add(OUT/'geographic_qa.gpkg',title,qa,layer)
for slug in ['barat','pusat','selatan','timur','utara']:
    add(ROOT/f'data/processed/roads_walk_jakarta_{slug}.gpkg',f'Walk road geometry Jakarta {slug}',roads_group)
add(OUT/'final_model_features.gpkg','Full source features (2765 rows)',models,'source_features')
add(OUT/'baseline/agent3/outputs/gis/priority_models.gpkg','Frozen provisional M1-M4 (baseline)',models)
for name in ['jakarta_2024_lst_ndvi_qa','jakarta_2024_trees_built_probability']:
    add(ROOT/f'data/processed/remote_sensing/{name}.tif',name,rasters,raster=True)
project.setCrs(grid.crs())
for group in [qa,roads_group,models,rasters]:group.setItemVisibilityChecked(False)
project.viewSettings().setDefaultViewExtent(__import__('qgis.core',fromlist=['QgsReferencedRectangle']).QgsReferencedRectangle(grid.extent(),grid.crs()))
project.setFilePathStorage(__import__('qgis.core',fromlist=['Qgis']).Qgis.FilePathType.Relative)
target=ROOT/'qgis/agent2_gis_qa.qgz'
if not project.write(str(target)):raise RuntimeError('QGIS project save failed')
print(f'Saved {target}: {len(project.mapLayers())} valid layers, {project.crs().authid()}',flush=True)
project.clear()
app.exitQgis()
