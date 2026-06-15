# Procedencia de datos

## Allen Visual Behavior Neuropixels

- Release local: `visual-behavior-neuropixels-0.5.0`.
- Pipeline declarado en manifest: AllenSDK `2.16.2`.
- Manifest:
  `data/allen/visual-behavior-neuropixels_project_manifest_v0.5.0.json`.
- Sesiones NWB disponibles localmente: 50.
- Tamaño local total de `data/`: aproximadamente 140 GB.
- Integridad: los cinco CSV de metadatos coinciden con sus hashes BLAKE2b del
  manifest.

Los datos originales no se versionan en Git. El benchmark guarda el path del
manifest, versión, filtros, sesiones incluidas/excluidas y hashes verificados.

## Transformación de Fase 2

1. Cualificar unidades desde `units.csv`.
2. Cualificar sesiones antes de abrir NWB.
3. Leer el bloque espontáneo más largo mediante campos NWB/HDF5 estándar.
4. Agregar spikes por región y segundo, normalizados por número de unidades.
5. Calcular FC de Pearson regional.
6. Evaluar cada sesión contra referencias que excluyen todas las sesiones del
   mismo ratón.
7. Comparar contra etiquetas regionales permutadas.

La transformación produce una representación funcional derivada. No produce
conectividad anatómica, conectividad efectiva ni un conectoma.

## Transformación de Fase 2b

Además de reutilizar la FC y tasa espontáneas, se extraen eventos de cambio
visual desde la única tabla NWB cuyo nombre sigue
`Natural_Images_Lum_Matched_set_ophys_*_presentations`. Se incluyen únicamente
cambios activos y no omitidos. La respuesta regional es la diferencia de tasa
entre `[0, 250 ms)` y `[-250 ms, 0)` agregada sobre eventos y unidades
cualificadas.

La búsqueda de la tabla admite conjuntos de imágenes `G` y `H`; fijar solo uno
sesgaría la cohorte. Los resultados conservan versión, filtros, configuración y
commit de código.

## Transformación y confirmación de Fase 2c

La respuesta temporal conserva veinte bins de `50 ms` entre `-250 ms` y
`+750 ms` respecto al cambio visual. El target confirmado resta el baseline por
región y calcula su derivada temporal.

La cohorte de desarrollo contiene 21 sesiones de 19 ratones. La cohorte
confirmatoria contiene 20 sesiones de 20 ratones nuevos, equilibradas entre
Familiar y Novel. La lista, URLs y hashes se sellaron en
`configs/allen_vbn_phase2c_confirmation_sealed.json` antes de descargar sus NWB.
Los veinte archivos confirmatorios pasaron verificación BLAKE2b.
