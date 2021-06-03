"""
Process and convert infrastructure data.

Written by Ed Oughton.

March 2021

"""
import os
import configparser
from pathlib import Path
import json
import pandas as pd
import fiona
import geopandas as gpd
# from dataprep.clean import clean_lat_long
from tqdm import tqdm
from re import search
from zipfile import ZipFile

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def grep_folder():
    """
    Load in all desired shapes.

    """
    directory = os.path.join(
        DATA_RAW,
        'Data Request (GIS)',
    )

    folders = [
        os.path.join(DATA_INTERMEDIATE, 'CHL', 'existing_network', 'Mobile Broadband'),
        os.path.join(DATA_INTERMEDIATE, 'CHL', 'existing_network', 'Fiber Optic Backbone'),
        # os.path.join(DATA_INTERMEDIATE, 'Fixed Broadband'),

    ]

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    excl_files = [
        'dbf', '.prj', '.cpg', '.shx'#, ''
        # '', '.gdbtablx', '.zip', '.gdbtable', '.freelist', '.gdbindexes',
        # '.idx', '.xlsx', '.CPG', '.qpj', '.spx', '.lyr', '.mxd', '.KMZ',
        # '.mpk', '.atx', '.lock', '.sbx', '.kmz', '.rar'
        ]

    files_included = set()
    files_not_included = set()
    file_extensions_excluded = set()
    not_in_inclusions = set()

    inclusions_fiber = [
        "Celeo Redes.gdb",
        "Troncales CLARO_2 LD3T -A.shp",
        "Trazado_FO_CMET_2018.shp",
        "RUTA TRONCAL CLARO.shp",
        "Trazado_FO_CMET_2018.shp",
        "RUTA TRONCAL CLARO.shp",
        "TRONCAL - P.shp",
        "Troncales CLARO_2 LD3T -B.shp",
        "TRONCAL FANOR - EL SALTO.shp",
        "RED GAS ANDES.shp",
        "Trazado_FO_PACIFICOCABLE_2018.shp",
        "Trazado_FO_SILICA_2018.shp",
        "TRONCAL ACCESO.shp",
        "TRONCAL - FANOR ACCESO NORTE.shp",
        "Rutas FO plug_Play.gdb",
        "RED 03_FO_Serena - Stgo.gdb",
        "Of Cir 138-C-2018 ESA FO.gdb",
        "Red_05_Santiago-Temuco.shp",
        "Fibra_Optica_LD.shp",
        "TRONCAL ENTEL.shp",
        "Red_03_FO_Serena-Santiago.shp",
        "RED 07_FO_Austral_2019_kmz.gdb",
        "Red_06_FO_Temuco-Puerto Montt.shp",
        "Century.gdb",
        "PolylinesRutaChile.shp",
        "RUTA CLARO EL SALTO - SILICA.shp",
        "RED_Shape_NODO.shp",
        "FO.shp",
        "RED 02_FO_Antofa - La Serena.gdb",
        "Trazado_FO_VTR_2018.shp",
        "Red_07_FO_Austral.shp",
        "RED_01_FO_2019_xls.shp",
        "RED 04_FO_Stgo - Calera_2019_kmz.gdb",
        "RED_Shape_TRAMO.shp",
        "Red_04_FO_Stgo_Calera.shp",
        "TRONCAL CLARO 2.shp",
        "Geometria_de_redes_ITXC.shp",
        "RED 05_FO_Stgo - Temuco.gdb",
        "RED 06_FO_Temuco - P.Montt.gdb",
        "RED 06_FO_Temuco - P.Montt_2019_kmz.gdb",
        "PAR_PNTL_kml.gdb",
        "Red_09_FO_Locales.shp",
        "RED 07_FO_Austral.gdb",
        "RED_07_FO_Austral_2019_xls.shp",
        "RED_02_FO_Antofa_-_La_Serena_2019_xls.shp",
        "RED 02_FO_Antofa - La Serena_2019_kmz.gdb",
        "RED 08_FO_Metro_2019_kmz.gdb",
        "RED_01_FO_Arica_-_Antofa_2019_xls.shp",
        "Nodos_oficio_138_emailv2.gdb",
        "RED 09_FO_Locales_2019_kmz.gdb",
        "RED 01_FO_Arica - Antofa_kmz.gdb",
        "RED 01_FO_Arica - Antofa_2019_kmz.gdb",
        "RED 10_FO_BCap_2019_kmz.gdb",
        "NODOS TRONCAL CLARO.shp",
        "RED 03_FO_Serena - Stgo_2019_kmz.gdb",
        "RED_09_FO_Locales_2019_xls.shp",
        "Claro_KML_Sitios_of138.gdb",
        "Red_02_FO_Antofa-La Serena.shp",
        "Red_10_FO_BCap.shp",
        "RED_03_FO_Serena_-_Stgo_2019_xls.shp",
        "RED_06_FO_Temuco_-_PMontt_2019_xls.shp",
        "Of Cir 138-C-2018 ESA FO.kml",
        "RED 05_FO_Stgo - Temuco_2019_kmz.gdb",
        "Red_01_FO_Arica-Antofagasta.shp",
        "RED_05_FO_Stgo_-_Temuco_2019_xls.shp",
        "RED_04_FO_Stgo_-_Calera_2019_xls.shp",
        "Nodos.shp",
        "Red_08_FO_Metro.shp",
        "FOA 2.kmz",
        "Fibra Ã“ptica TarapacÃ¡.kmz",
        "Ultima Milla Ohiggins (Movil + TxFO).kmz",
        "Fibra Optica en Complejos Fronterizos.kmz",
        "Ultima Milla BioBio.kmz",
        "Ultima Milla Atacama.kmz",
        "Yafun_mapa_camino_sin_postacion.shp",
        "Yafun_mapa_ferry.shp",
        "Yafun_mapa_fibra.shp",
        "Yafun_mapa_fibra_cobre.shp",
        "Yafun_mapa_fibra_cuatruple.shp",
        "Yafun_mapa_fibra_doble.shp",
        "Yafun_mapa_fibra_internacional.shp",
        "Yafun_mapa_fibra_magallanes.shp",
        "Yafun_mapa_fibra_soterrada.shp",
        "Yafun_mapa_fibra_triple.shp",
        "Yafun_mapa_foa.shp",
    ]

    inclusions_mobile = [
        'ELEMENTOS_AUTORIZATORIOS_EN_SERVICIO.shp',
        'CELLID_2021_03.shp',

    ]

    inclusions = inclusions_mobile #+ inclusions_fiber

    for path in Path(directory).rglob('*'):

        if 'mobile' in str(path).lower():
            folder = os.path.join(DATA_INTERMEDIATE, 'CHL',
                'existing_network','Mobile Broadband')
        elif 'fiber' in str(path).lower():
            folder = os.path.join(DATA_INTERMEDIATE, 'CHL',
                'existing_network', 'Fiber Optic Backbone')
        elif 'Fiber 2' in str(path).lower():
            folder = os.path.join(DATA_INTERMEDIATE, 'CHL',
                'existing_network', 'Fiber Optic Backbone')
        else:
            folder = os.path.join(DATA_INTERMEDIATE, 'CHL',
                'existing_network', 'unknown')

        file_extension = os.path.splitext(path)[1].lower()

        file_name = os.path.basename(path)

        # if not file_name == 'Of Cir 138-C-2018 ESA FO.kml':
        #     continue

        if not file_name in inclusions:
            not_in_inclusions.add(file_name)
            continue

        #extract .kml from .kmz before processing
        if file_extension == '.kmz':

            with ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(path))

        if file_extension == '.gdb':
            layers = fiona.listlayers(path)
            for layer in layers:
                gdf = gpd.read_file(path, layer=layer)
                filename = '{}_{}'.format(
                    os.path.basename(os.path.splitext(path)[0]),
                    layer
                )
                path_out = os.path.join(folder, filename + '.shp')
                gdf.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
                continue

        elif file_extension == '.kml':
            gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
            try:
                gdf = gpd.read_file(path, driver='KML')
            except:
                files_not_included.add(file_name)
                continue

            if 'Point' in [i for i in gdf['geometry'].geom_type]:
                points = gdf.loc[gdf['geometry'].geom_type == 'Point']
                path_out = os.path.join(folder, file_name + '_points' + '.shp')
                points.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
            elif 'LineString' in [i for i in gdf['geometry'].geom_type]:
                linestrings = gdf.loc[gdf['geometry'].geom_type == 'LineString']
                path_out = os.path.join(folder, file_name + '_lines' + '.shp')
                linestrings.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
            else:
                files_not_included.add(file_name)

        elif file_extension == '.shp':
            filename = os.path.basename(path)[:-4]
            try:
                gdf = gpd.read_file(path, crs='epsg:4326')
            except:
                files_not_included.add(file_name)
                continue
            path_out = os.path.join(folder,  filename + '.shp')
            gdf.to_file(path_out, crs='epsg:4326')
            files_included.add(file_name)

        elif file_extension == '.kmz':
            continue
        else:
            if file_extension in excl_files:
                file_extensions_excluded.add(file_name)
                continue
            files_not_included.add(file_name)
            continue

    output = pd.DataFrame({
        'files_included': pd.Series(list(files_included)),
        # 'files_not_included': pd.Series(list(files_not_included)),
        # 'file_extensions_excluded': pd.Series(list(file_extensions_excluded)),
        'files_not_included': pd.Series(list(not_in_inclusions)),
    })

    path = os.path.join(DATA_INTERMEDIATE, 'file_inclusions_and_exclusions.csv')
    output.to_csv(path, index=False)


if __name__ == "__main__":

    #automated search and extract
    grep_folder()

    # get_electricity_data()
