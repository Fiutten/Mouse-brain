# Protocolo de Fase 2c: target temporal y confirmación externa

## Desarrollo

Las 21 sesiones ya analizadas son exclusivamente cohorte de desarrollo. Se
extrae una respuesta temporal regional alrededor de cambios visuales activos y
no omitidos:

- intervalo: `[-250, +750] ms`;
- bin: `50 ms`;
- seis regiones visuales;
- mismos filtros de unidades de Fases 2 y 2b.

Se comparan exactamente tres transformaciones:

1. `baseline_subtracted`: resta por región de la media preevento;
2. `region_peak_normalized`: anterior, dividida por el máximo absoluto regional;
3. `temporal_derivative`: diferencia temporal de la respuesta corregida.

Cada target conserva tiempo y región; la evaluación aplana la matriz únicamente
para calcular correlación. El nulo permuta identidades regionales conservando la
dinámica temporal.

## Puerta de desarrollo

Un candidato pasa solo si cumple simultáneamente:

- mediana leave-one-mouse-out `> 0.50`;
- split-half mediano `> 0.70`;
- al menos 50% de sesiones sobre su nulo individual del 95%;
- límite inferior bootstrap agrupado por ratón `> 0`.

Como máximo se selecciona uno, priorizando fracción sobre nulo y después
correlación entre ratones.

## Sellado confirmatorio

Si existe candidato, se genera antes de descargar datos una lista sellada de 20
sesiones de ratones no usados en desarrollo:

- diez Familiar y diez Novel;
- un máximo de una sesión por ratón;
- orden determinista por ID de sesión;
- cada sesión debe cumplir la misma cobertura regional;
- URL y hash BLAKE2b proceden del manifest Allen `0.5.0`.

## Confirmación única

La transformación seleccionada y los umbrales no pueden modificarse. La
confirmación requiere al menos 16 sesiones descargadas y utiliza referencia
leave-one-mouse-out exclusivamente dentro de la cohorte nueva.

Si falla, se abandona este target funcional como objetivo primario y se prioriza
integración anatómica Allen MCModels/CCF.
