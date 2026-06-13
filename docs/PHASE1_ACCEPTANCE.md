# Criterios de aceptación de la Fase 1

La fase se acepta únicamente si:

- toda la suite de tests pasa;
- dos ejecuciones con misma configuración producen arrays idénticos;
- una lesión no muta la conectividad original y mantiene a cero su región activa;
- ambos modelos producen estados finitos;
- el CLI genera configuración, procedencia, métricas y resultados;
- se completan ejecuciones de 50 y 500 regiones;
- cada salida sintética se etiqueta como validación de ingeniería.

Los tiempos observados dependen del equipo y no se interpretan como benchmark
científico hasta definir un protocolo de hardware controlado.

## Resultado observado el 13 de junio de 2026

- Suite completa: 34 tests superados.
- Wilson-Cowan, 50 regiones, 201 muestras: estados finitos; artefacto de 164 KB.
- Linear-rate, 500 regiones, 51 muestras: estados finitos; artefacto de 452 KB.
- La conectividad sintética y todas las métricas derivadas quedan etiquetadas
  `engineering_validation_only`.
