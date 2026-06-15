# Confirmación externa de Fase 3

## Decisión

La hipótesis de que la topología anatómica Allen aporta valor predictivo para
el target temporal confirmado queda **rechazada bajo este protocolo**.

La confirmación se ejecutó una vez sobre 20 sesiones de 20 ratones nuevos desde
el commit sellado `673e5cc`.

## Resultados confirmatorios

| Métrica | Resultado | Umbral | Pasa |
|---|---:|---:|---|
| Correlación mediana Allen | 0.5281 | > 0.30 | sí |
| Allen menos mediana de permutaciones | -0.0054 | > 0.05 | no |
| Permutaciones superadas | 21% | >= 95% | no |
| Límite inferior bootstrap de ventaja pareada | -0.0075 | > 0 | no |
| Allen menos desconectado | 0.0035 | > 0.05 | no |

El intervalo bootstrap 95% de la ventaja pareada frente a la mediana de
permutaciones fue `[-0.0075, -0.0012]`.

## Controles

| Topología | Correlación mediana confirmatoria |
|---|---:|
| Allen | 0.5281 |
| Desconectada | 0.5246 |
| Allen transpuesta | 0.5313 |
| Mediana de permutaciones | 0.5335 |

Cada control fue recalibrado exclusivamente en desarrollo dentro de la misma
familia `LinearRateModel`. Por tanto, el resultado no se explica porque Allen
recibiera parámetros menos favorables que los controles.

## Interpretación

El modelo produce una predicción temporal moderada, pero esta capacidad no
depende de la topología Allen. Las predicciones Allen y desconectada tienen
correlación `0.9964` dentro de la ventana evaluada. Esto indica que la forma
predicha está dominada por el vector de entrada regional derivado de desarrollo
y por una relajación temporal común.

El resultado separa dos afirmaciones:

1. **Soportada:** una dinámica lineal simple condicionada por una entrada
   regional compartida captura parte del target.
2. **No soportada:** la conectividad anatómica regional Allen explica esa
   capacidad predictiva.

## Alcance del rechazo

No se demuestra que la anatomía cerebral sea irrelevante. Se rechaza una
afirmación mucho más limitada:

> La matriz regional agregada de seis áreas visuales, combinada con
> `LinearRateModel` o `WilsonCowanModel`, aporta valor predictivo específico para
> `temporal_derivative` bajo este protocolo.

La agregación anatómica tiene cobertura desigual por región y el target está
fuertemente bloqueado al evento. Añadir más complejidad al mismo benchmark para
rescatar la hipótesis produciría una inferencia post hoc y no está permitido.

## Siguiente decisión científica

Antes de construir modelos más detallados debe demostrarse, usando únicamente
desarrollo, que existe un target sensible a propagación dirigida:

- latencias regionales robustas;
- estructura lead-lag reproducible;
- ventaja frente a permutación de identidad regional;
- estabilidad entre ratones.

Si no existe esa señal, Allen VBN no es adecuado para evaluar topología
anatómica con este nivel de agregación. Si existe, deberá sellarse y confirmarse
en una tercera cohorte independiente antes de probar nuevos modelos.
