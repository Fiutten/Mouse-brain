# Fase 4: identificabilidad de propagación dirigida

## Decisión

La firma dirigida queda **rechazada en desarrollo**. No existe evidencia
suficiente de latencias regionales o estructura lead-lag no trivial que justifique
modelos anatómicos más complejos sobre este target de Allen VBN.

El análisis se ejecutó desde el commit `5b2200d` y usa exclusivamente las 21
sesiones de desarrollo.

## Resultado agregado

| Criterio | Resultado | Umbral | Pasa |
|---|---:|---:|---|
| Kendall tau split-half de latencias | 0.0000 | > 0.50 | no |
| Kendall tau cross-mouse de latencias | 0.0000 | > 0.30 | no |
| Latencias sobre nulo individual 95% | 0% | >= 50% | no |
| Pares con latencias resolubles | 0.0000 | >= 0.50 | no |
| Acuerdo split-half lead-lag | 1.0000 | > 0.70 | sí |
| Acuerdo cross-mouse lead-lag | 1.0000 | > 0.65 | sí |
| Lead-lag sobre nulo individual 95% | 0% | >= 50% | no |
| Ventaja frente a eventos desplazados | 0.3333 | > 0.10 | sí |
| Pares lead-lag no simultáneos | 0.0000 | >= 0.25 | no |

## Interpretación

Las latencias medianas de las seis regiones son todas `75 ms`. La fracción
mediana de pares regionales separados por al menos un bin de `50 ms` es `0.0`.
Esto significa que el target confirmado de Fase 2c es reproducible, pero está
dominado por una respuesta común bloqueada al evento.

El acuerdo lead-lag alto no es evidencia de dirección. La firma real es
mayoritariamente simultánea: la fracción mediana de pares no simultáneos es
`0.0`. Además, el lead-lag no supera su control de permutación regional.

Por tanto, Allen VBN no proporciona aquí una señal temporal suficientemente
identificadora para decidir si una topología anatómica dirigida es correcta.

## Alcance

Este resultado no afirma que no exista propagación visual en el cerebro de ratón.
Afirma algo más limitado y defendible:

> Con bins de `50 ms`, seis regiones visuales agregadas y cambios visuales
> naturales de Allen VBN, la señal funcional disponible no distingue de forma
> robusta una firma de propagación dirigida.

No procede descargar una tercera cohorte ni construir un modelo más complejo
sobre este target.

## Consecuencia metodológica

La línea Allen VBN queda cerrada para evaluación de topología dirigida. Puede
seguir siendo útil como benchmark de respuesta evocada reproducible, pero no
como prueba anatómico-dinámica.

Para avanzar científicamente hay dos rutas realistas:

1. cambiar a un recurso con mejor resolución temporal o perturbaciones
   explícitas;
2. formular una publicación metodológica sobre falsación progresiva de targets
   digitales parciales, incluyendo Fases 2c, 3 y 4 como caso de estudio.
