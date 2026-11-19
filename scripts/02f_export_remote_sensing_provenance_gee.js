/** RS-01: APPEND this file to the unchanged 02_remote_sensing_gee.js in Code Editor.
 * Not executed in this remediation: authenticated operator required.
 * This creates a NEW replay; it cannot reconstruct a lost historical task log.
 * Archive the exact concatenated source and its SHA256 BEFORE running any task.
 * Save task status JSON (IDs, creation/start/update/completion times, state, errors)
 * and downloaded file SHA256 values in an operator manifest after completion.
 * Keep replay rasters separate from frozen inputs until comparison and review.
 * No acquisition metadata is inferred from the local GeoTIFF or its file mtime.
 */
var RECIPE_ID = 'RS01_2024_provenance_replay_v1';
var replayRecordedAtUtc = new Date().toISOString(); // recipe evaluation, NOT task completion
var sceneFields = ['dataset_id', 'image_id', 'system_index', 'acquired_at_utc',
  'wrs_path', 'wrs_row', 'processing_level', 'product_id', 'date_product_generated', 'recipe_id'];

function sceneRows(collection, dataset, isLandsat) {
  return ee.FeatureCollection(collection.toList(collection.size()).map(function(item) {
    var img = ee.Image(item);
    return ee.Feature(null, {
      dataset_id: dataset,
      image_id: ee.String(dataset).cat('/').cat(ee.String(img.get('system:index'))),
      system_index: img.get('system:index'),
      acquired_at_utc: ee.Date(img.get('system:time_start')).format("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", 'UTC'),
      wrs_path: isLandsat ? img.get('WRS_PATH') : null,
      wrs_row: isLandsat ? img.get('WRS_ROW') : null,
      processing_level: isLandsat ? img.get('PROCESSING_LEVEL') : null,
      product_id: isLandsat ? img.get('LANDSAT_PRODUCT_ID') : null,
      date_product_generated: isLandsat ? img.get('DATE_PRODUCT_GENERATED') : null,
      recipe_id: RECIPE_ID
    });
  }));
}
var dwSources = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(roi).filterDate(START, END);
var allScenes = sceneRows(landsatRaw, 'LANDSAT/LC09/C02/T1_L2', true)
  .merge(sceneRows(dwSources, 'GOOGLE/DYNAMICWORLD/V1', false));
Export.table.toDrive({collection: allScenes, description: 'RS01_scene_manifest',
  folder: EXPORT_FOLDER, fileNamePrefix: 'remote_sensing_scene_manifest_replay',
  fileFormat: 'CSV', selectors: sceneFields});

// At 30 m on the explicit frozen thermal grid, per month and AOI:
// sum(count * pixelArea) / sum(pixelArea) is clear observations / AOI pixel area.
// Count * area is m2-observations, not unique observed area. Export both.
var thermalTransform = [30, 0, 686580, 0, -30, 9326670];
var monthly = ee.FeatureCollection(ee.List.sequence(1, 12).map(function(month) {
  var start = ee.Date.fromYMD(YEAR, month, 1);
  var end = start.advance(1, 'month');
  var raw = landsatRaw.filterDate(start, end);
  // A fully masked seed makes an empty month return count 0 with correct band schema.
  var seed = ee.Image.constant(0).rename('lst_c').updateMask(ee.Image.constant(0));
  var clean = landsatClean.filterDate(start, end).select('lst_c').merge(ee.ImageCollection([seed]));
  var count = clean.count().unmask(0).clip(roi);
  var area = ee.Image.pixelArea().clip(roi);
  var sums = ee.Image.cat([
    area.rename('aoi_sampled_area_m2'),
    count.multiply(area).rename('clear_support_m2_observations'),
    count.gt(0).multiply(area).rename('observed_area_m2')
  ]).reduceRegion({reducer: ee.Reducer.sum(), geometry: roi, crs: 'EPSG:32748',
    crsTransform: thermalTransform, maxPixels: 1e9, tileScale: 4});
  return ee.Feature(null, sums).set({month_utc: start.format('yyyy-MM', 'UTC'),
    scene_count: raw.size(), dw_image_count: dwSources.filterDate(start, end).size(),
    recipe_id: RECIPE_ID, state: 'NEW_REPLAY_NOT_ORIGINAL_EXPORT'});
}));
Export.table.toDrive({collection: monthly, description: 'RS01_monthly_support',
  folder: EXPORT_FOLDER, fileNamePrefix: 'rs_monthly_temporal_support_replay', fileFormat: 'CSV'});

// Exact asset geometry export for hashing; local boundary hash is not a substitute.
Export.table.toDrive({collection: ee.FeatureCollection([ee.Feature(roi, {asset_id: BOUNDARY_ASSET,
  recipe_id: RECIPE_ID})]), description: 'RS01_AOI', folder: EXPORT_FOLDER,
  fileNamePrefix: 'rs_aoi_replay', fileFormat: 'GeoJSON'});
var recipe = ee.Feature(null, {
  recipe_id: RECIPE_ID, recipe_evaluated_at_utc: replayRecordedAtUtc,
  period_start_inclusive: START, period_end_exclusive: END,
  aoi_asset: BOUNDARY_ASSET, landsat_scene_count: landsatRaw.size(), dw_image_count: dwSources.size(),
  landsat_collection: 'LANDSAT/LC09/C02/T1_L2', dw_collection: 'GOOGLE/DYNAMICWORLD/V1',
  landsat_processing_level: 'L2SP', qa_pixel_clear_bits: '0-5', qa_radsat: 0,
  lst_scale: 0.00341802, lst_offset_k: 149.0, kelvin_to_celsius: -273.15,
  sr_scale: 0.0000275, sr_offset: -0.2, st_qa_scale_k: 0.01,
  temporal_reducer: 'independent per-band median', crs: 'EPSG:32748',
  thermal_scale_m: 30, dw_scale_m: 10, nodata: -9999,
  original_task_provenance: 'UNRECOVERED; this table describes a new replay'
});
Export.table.toDrive({collection: ee.FeatureCollection([recipe]), description: 'RS01_recipe',
  folder: EXPORT_FOLDER, fileNamePrefix: 'rs_recipe_replay', fileFormat: 'GeoJSON'});
print('RS-01: run original TWO image tasks AND FOUR metadata tasks; save actual task status separately.');
