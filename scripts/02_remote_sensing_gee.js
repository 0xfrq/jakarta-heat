/**
 * JAKARTA HEAT INEQUALITY MAPPER - PERSON 1
 * Landsat 9 Level-2 (2024) + optional Dynamic World (2024)
 * Prepared for Google Earth Engine Code Editor, JavaScript.
 * AOI uses temporary bounding rectangle until Person 2 sends finalized boundary.
 * Source: USGS Landsat 9 C2 L2 and Google Dynamic World V1.
 * Outputs: 2 GeoTIFF files: thermal QA (4 bands), land-cover probabilities (2 bands).
 * Each export is a server-side Google Drive task; run in Tasks panel.
 */

// ============== CONFIGURATION ==============
var YEAR = 2024;
var START = YEAR + '-01-01';
var END = (YEAR + 1) + '-01-01';
var USE_BOUNDARY_ASSET = true;
var BOUNDARY_ASSET = 'projects/nodemailer-mailer/assets/jakarta_5kota';
var EXPORT_FOLDER = 'Jakarta_Heat_Project';

// Rectangle: prototype only, not five administrative cities.
var roi = ee.Geometry.Rectangle([106.68, -6.38, 107.00, -6.08]);
if (USE_BOUNDARY_ASSET) {
  roi = ee.FeatureCollection(BOUNDARY_ASSET).geometry();
}
Map.centerObject(roi, 10);
Map.addLayer(roi, {color: 'white'}, 'AOI (check before exporting)');

// ============== JOB 2: LANDSAT 9 ==============
function preprocessLandsat(img) {
  // QA bits 0 through 5: fill, dilated cloud, cirrus,
  // cloud, cloud shadow and snow. 63 = 0b111111.
  var qa = img.select('QA_PIXEL');
  var clear = qa.bitwiseAnd(63).eq(0)
    .and(img.select('QA_RADSAT').eq(0));

  // Surface reflectance: Collection 2 scaling factors.
  var red = img.select('SR_B4').multiply(0.0000275).add(-0.2);
  var nir = img.select('SR_B5').multiply(0.0000275).add(-0.2);
  var denominator = nir.add(red);
  var ndvi = nir.subtract(red).divide(denominator)
    .updateMask(denominator.abs().gt(0.000001))
    .rename('ndvi');

  // LST: ST_B10 in Kelvin, convert to Celsius.
  var lst = img.select('ST_B10')
    .multiply(0.00341802).add(149.0).subtract(273.15)
    .rename('lst_c');

  // Per-scene surface temperature uncertainty (scale = 0.01 K).
  var stQa = img.select('ST_QA').multiply(0.01)
    .rename('lst_unc_k');

  return ee.Image.cat([lst, ndvi, stQa])
    .updateMask(clear)
    .copyProperties(img, ['system:time_start']);
}

var landsatRaw = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
  .filterBounds(roi)
  .filterDate(START, END)
  .filter(ee.Filter.eq('PROCESSING_LEVEL', 'L2SP'));
print('Number of 2024 Landsat 9 L2SP scenes:', landsatRaw.size());

var landsatClean = landsatRaw.map(preprocessLandsat);
var med = landsatClean.median();
var validObs = landsatClean.select('lst_c').count().rename('lst_obs');
var validLst = validObs.gt(0).unmask(0).rename('lst_valid');

// Four primary bands plus valid coverage flag.
var thermal = med.select(['lst_c', 'ndvi', 'lst_unc_k'])
  .addBands(validObs)
  .addBands(validLst)
  .clip(roi);

Map.addLayer(thermal.select('lst_c'),
  {min: 25, max: 45, palette: ['navy', 'cyan', 'yellow', 'red']},
  'Landsat median LST (C), 2024');
Map.addLayer(thermal.select('ndvi'),
  {min: -0.2, max: 0.8, palette: ['brown', 'yellow', 'green']},
  'Landsat median NDVI, 2024');
Map.addLayer(thermal.select('lst_obs'),
  {min: 0, max: 10, palette: ['white', 'orange', 'purple']},
  'Number of valid LST observations, 2024', false);

// Lightweight QA: numerical stats at 100m for rapid preview.
print('Thermal stats (approx., 100m)', thermal.reduceRegion({
  reducer: ee.Reducer.minMax(),
  geometry: roi,
  scale: 100,
  maxPixels: 1e8,
  tileScale: 4
}));

Export.image.toDrive({
  image: thermal.toFloat().unmask(-9999),
  description: 'JKT_2024_LST_NDVI_QA',
  folder: EXPORT_FOLDER,
  fileNamePrefix: 'jakarta_2024_lst_ndvi_qa',
  region: roi,
  scale: 30,
  crs: 'EPSG:32748',
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF',
  formatOptions: {noData: -9999}
});

// ============== JOB 3: DYNAMIC WORLD (OPTIONAL) ==============
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
  .filterBounds(roi)
  .filterDate(START, END)
  .select(['trees', 'built']);
print('Number of 2024 Dynamic World images:', dw.size());

// Median of per-acquisition probabilities (NOT land cover fractions).
var dwMedian = dw.median()
  .rename(['trees_prob', 'built_prob'])
  .clip(roi);
Map.addLayer(dwMedian.select('trees_prob'),
  {min: 0, max: 1, palette: ['white', 'lightgreen', 'darkgreen']},
  'Dynamic World tree probability, 2024', false);
Map.addLayer(dwMedian.select('built_prob'),
  {min: 0, max: 1, palette: ['white', 'orange', 'red']},
  'Dynamic World built probability, 2024', false);

Export.image.toDrive({
  image: dwMedian.toFloat().unmask(-9999),
  description: 'JKT_2024_DynamicWorld_probabilities',
  folder: EXPORT_FOLDER,
  fileNamePrefix: 'jakarta_2024_trees_built_probability',
  region: roi,
  scale: 10,
  crs: 'EPSG:32748',
  maxPixels: 1e10,
  fileFormat: 'GeoTIFF',
  formatOptions: {noData: -9999}
});

/**
 * JOB 2 — ADDITIONAL QUALITY VALIDATION
 * Jakarta Heat Inequality Mapper
 * Landsat 9, 2024
 */

// ==========================================
// 1. PERCENTILE STATISTICS
// ==========================================

var percentiles = thermal
  .select([
    'lst_c',
    'ndvi',
    'lst_unc_k',
    'lst_obs'
  ])
  .reduceRegion({
    reducer: ee.Reducer.percentile([
      5, 25, 50, 75, 95, 99
    ]),
    geometry: roi,
    scale: 100,
    maxPixels: 1e9,
    tileScale: 4
  });

print('Distribusi indikator:', percentiles);


// ==========================================
// 2. LST VALID COVERAGE
// ==========================================

// lst_valid sudah dibuat sebelumnya:
// 1 = memiliki observasi LST valid
// 0 = tidak memiliki observasi LST valid

var coverage = thermal
  .select('lst_valid')
  .reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: roi,
    scale: 100,
    maxPixels: 1e9,
    tileScale: 4
  });

var coveragePercent = ee.Number(
  coverage.get('lst_valid')
).multiply(100);

print('LST coverage (%):', coveragePercent);


// ==========================================
// 3. ADDITIONAL QUALITY STATISTICS
// ==========================================

var qualityStats = thermal
  .select(['lst_unc_k', 'lst_obs'])
  .reduceRegion({
    reducer: ee.Reducer.mean()
      .combine({
        reducer2: ee.Reducer.minMax(),
        sharedInputs: true
      }),
    geometry: roi,
    scale: 100,
    maxPixels: 1e9,
    tileScale: 4
  });

print('Quality statistics:', qualityStats);


// ==========================================
// 4. QUALITY MAP
// ==========================================

Map.addLayer(
  thermal.select('lst_valid'),
  {
    min: 0,
    max: 1,
    palette: ['red', 'green']
  },
  'LST Valid Coverage',
  false
);

Map.addLayer(
  thermal.select('lst_unc_k'),
  {
    min: 0,
    max: 10,
    palette: ['green', 'yellow', 'red']
  },
  'LST Uncertainty (K)',
  false
);

print('Quality validation completed.');


var validPixels = thermal.select('lst_valid').eq(1);

var qualityFlags = ee.Image.cat([
  thermal.select('lst_c')
    .gt(50).rename('hot_gt50'),

  thermal.select('lst_unc_k')
    .gt(5).rename('unc_gt5'),

  thermal.select('lst_obs')
    .lt(8).rename('obs_lt8')
]).updateMask(validPixels);

var flagStats = qualityFlags.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: roi,
  scale: 100,
  maxPixels: 1e9,
  tileScale: 4
});

print('Quality flag proportions:', flagStats);

