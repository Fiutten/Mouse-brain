# Procedencia de datos

## Allen Visual Behavior Neuropixels

- Release local: `visual-behavior-neuropixels-0.5.0`.
- Pipeline declarado en manifest: AllenSDK `2.16.2`.
- Manifest:
  `data/allen/visual-behavior-neuropixels_project_manifest_v0.5.0.json`.
- Sesiones NWB disponibles localmente: 30.
- Tamaño local total de `data/`: aproximadamente 88 GB.
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
