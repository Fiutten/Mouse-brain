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

## Conectividad regional de Fase 3

La matriz de seis áreas procede de la API oficial del Allen Mouse Brain
Connectivity Atlas. Incluye 200 experimentos del producto `5` cuya estructura
primaria de inyección coincide exactamente con la región fuente. Cada arista es
la mediana bilateral de `normalized_projection_volume`; la diagonal se fija a
cero para excluir contaminación del sitio de inyección.

El recurso derivado y la lista de experimentos se versionan en
`mousebrainbench/data/reference/allen_visual_connectivity.json`. La cobertura
por fuente es desigual y se conserva explícitamente como limitación.

## Sensorium/Dynamic Sensorium

La procedencia oficial verificada es:

- portal: `https://sensorium-competition.net/`;
- código Sensorium 2022: `https://github.com/sinzlab/sensorium`;
- código Dynamic Sensorium 2023: `https://github.com/ecker-lab/sensorium_2023`;
- datos Sensorium 2022: `https://gin.g-node.org/cajal/Sensorium2022`;
- datos Dynamic Sensorium 2023:
  `https://gin.g-node.org/pollytur/sensorium_2023_dataset`.

La estructura oficial documentada contiene zips por ratón que, al descomprimir,
incluyen `data/images` o `data/videos`, `data/responses`, variables
conductuales y metadatos bajo `meta/trials` y `meta/neurons`.

Se ha implementado un adaptador compatible con esa estructura y un smoke
sintético reproducible. Esto verifica el código sin versionar datos externos ni
infringir condiciones de licencia. Cualquier análisis publicable sobre Dynamic
Sensorium debe revisar la licencia `CC BY-NC-ND 4.0` y, si procede, solicitar
permiso a los responsables del dataset.

El 17 de junio de 2026 se descargó la cohorte completa Sensorium 2022 estática:
siete zips (`21067`, `22846`, `23343`, `23656`, `23964`, `26872`, `27204`) y se
validaron con `unzip -t`. Los hashes, tamaños y resultados están en
[PHASE5_SENSORIUM_REAL_RESULTS.md](PHASE5_SENSORIUM_REAL_RESULTS.md). Los datos
permanecen fuera de Git bajo `data/sensorium/`.

Sensorium 2022 no contiene 17 ratones adicionales. Una ampliación a ese orden de
magnitud requiere otro recurso, como Dynamic Sensorium u otro benchmark visual.

El 17 de junio de 2026 se descargó la cohorte pública visible Dynamic Sensorium
2023 desde GIN: cinco zips (`29515`, `29623`, `29647`, `29712`, `29755`). Los
cinco pasaron `unzip -t` y se extrajeron bajo
`data/dynamic_sensorium/extracted/`. El uso local observado fue `48G` para raw y
`94G` para extraído. Los hashes, tamaños, tiers y resultados están en
[PHASE5_DYNAMIC_SENSORIUM_RESULTS.md](PHASE5_DYNAMIC_SENSORIUM_RESULTS.md).

Los tiers `live_test_*` y `final_test_*` de Dynamic Sensorium contienen
respuestas retenidas/zeroed en la release pública, por lo que no se usan para
evaluación directa. El tier `oracle` contiene respuestas no nulas, pero no
contiene vídeos repetidos exactos; la fiabilidad por repetición se marca como
no estimable en los artefactos.

El adaptador `calibrated_residual_ridge` se ejecutó sobre la misma extracción y
guardó sus artefactos en `results/dynamic_sensorium_adapter/`. La selección de
`alpha` y `beta` se realiza exclusivamente por CV interna en `train`; `oracle`
queda como held-out. Los resultados y limitaciones están en
[PHASE5_DYNAMIC_SENSORIUM_ADAPTER.md](PHASE5_DYNAMIC_SENSORIUM_ADAPTER.md).

El 18 de junio de 2026 se verificó también la release legacy enlazada desde el
README oficial de Dynamic Sensorium 2023 como "previous dataset" con respuestas
OOD liberadas. Se descargó y extrajo inicialmente un animal:

```text
dynamic29156-11-10-Video-8744edeac3b4d1ce16b680916b5267ce.zip
sha256 61915fa4e3f29da6c136cf71185e4cc38b0eb2c16fe2559db24fe8efffb178e7
```

El zip pasó `unzip -t`. Uso local observado tras interrumpir la descarga del
segundo zip parcial: `data/dynamic_sensorium_ood/raw` `7.7G` y
`data/dynamic_sensorium_ood/extracted` `8.6G`. La release contiene respuestas
no nulas en `live_test_main`, `live_test_bonus`, `final_test_main` y
`final_test_bonus`, por lo que permite una prueba OOD pública que no estaba
disponible en la cohorte principal descargada antes. Los artefactos quedan en
`results/dynamic_sensorium_ood/`.

Nota legal: el README de GIN indica licencia `CC BY-NC-ND 4.0` y solicita
permiso de publicación a los organizadores. Cualquier uso en artículo debe
respetar esa condición antes de enviar resultados.
