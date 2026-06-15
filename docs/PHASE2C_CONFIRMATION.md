# Confirmación externa de Fase 2c

## Decisión

El target `temporal_derivative` queda **confirmado** como representación
funcional evocada reproducible bajo el protocolo sellado. Esta decisión procede
de una única ejecución sobre la cohorte confirmatoria.

## Separación de cohortes

- Desarrollo: 21 sesiones de 19 ratones.
- Confirmación: 20 sesiones de 20 ratones no usados en desarrollo.
- Balance confirmatorio: diez sesiones Familiar y diez Novel.
- Sesiones procesadas con éxito: 20/20.
- Fallos de extracción: ninguno.
- Integridad: cada NWB confirmatorio coincide con el hash BLAKE2b del manifest.

El plan, las sesiones, la transformación y los umbrales se sellaron antes de
descargar la cohorte confirmatoria. El análisis se ejecutó desde el commit
`3b07ce3`.

## Resultado primario

| Métrica sellada | Umbral | Resultado | Decisión |
|---|---:|---:|---|
| Correlación mediana entre ratones | > 0.50 | 0.8908 | pasa |
| Split-half mediano | > 0.70 | 0.9896 | pasa |
| Sesiones sobre nulo individual 95% | >= 50% | 75% | pasa |
| Límite inferior bootstrap agrupado | > 0 | 0.8417 | pasa |

El intervalo bootstrap agrupado por ratón para la mediana fue
`[0.8417, 0.9214]`.

## Diagnóstico secundario

La correlación mediana fue `0.8806` en Familiar y `0.9047` en Novel. Superaron
su nulo individual el 60% y el 90%, respectivamente. Estas comparaciones son
descriptivas y no estaban definidas como contrastes confirmatorios.

Una sesión Novel (`1067790400`) presentó correlación `0.3793`, claramente menor
que el resto. No se excluye ni se reanaliza de forma selectiva. Debe conservarse
como caso de heterogeneidad para futuros análisis de robustez.

## Qué demuestra y qué no

El resultado demuestra que la derivada temporal de la respuesta regional a
cambios visuales contiene una estructura compartida y estable entre ratones en
estas seis áreas visuales y bajo estos filtros.

No demuestra:

- que la representación sea un mecanismo neuronal;
- que describa conectividad anatómica o efectiva;
- que un modelo mesoscópico pueda predecirla;
- que generalice fuera de Allen Visual Behavior Neuropixels;
- que exista un gemelo digital del cerebro de ratón.

La siguiente fase debe evaluar si modelos limitados por conectividad anatómica
predicen este target mejor que controles estructurales emparejados.
