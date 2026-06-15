# Desarrollo de Fase 3

## Cohorte y selección

- Cohorte de desarrollo: 21 sesiones.
- Conectividad: 200 experimentos Allen de trazado regional.
- Familia seleccionada: `LinearRateModel`.
- Parámetros Allen: `tau=0.05`, `coupling=1.0`, `drive_scale=0.5`.
- La selección y todos los controles se calibraron sin usar resultados
  confirmatorios de Fase 3.

## Resultados de desarrollo

| Modelo o topología | Correlación mediana |
|---|---:|
| Allen + LinearRate | 0.5836 |
| Allen + Wilson-Cowan | 0.4368 |
| Desconectado recalibrado | 0.5731 |
| Allen transpuesto recalibrado | 0.5875 |
| Mediana de 100 permutaciones recalibradas | 0.5860 |

Allen supera solo el 27% de las permutaciones. Su ventaja frente al desconectado
es `0.0104` y su diferencia frente al transpuesto es `-0.0040`.

## Interpretación previa a confirmación

El modelo lineal obtiene capacidad predictiva moderada, pero el desarrollo no
apoya que esa capacidad proceda de la topología anatómica Allen. El rendimiento
parece dominado por el vector de entrada estimado y la relajación temporal
regional.

Esta interpretación no sustituye la confirmación externa. La familia,
parámetros, controles, semillas, conectividad y umbrales quedan congelados en
`configs/allen_visual_phase3_confirmation_sealed.json`.

## Limitación anatómica

La cobertura de experimentos por fuente es muy desigual:

| Fuente | Experimentos |
|---|---:|
| VISp | 137 |
| VISl | 24 |
| VISal | 4 |
| VISrl | 10 |
| VISpm | 9 |
| VISam | 16 |

Por ello, un resultado negativo no demostraría que la anatomía sea irrelevante;
rechazaría únicamente esta matriz agregada, escala regional y familia dinámica
para predecir el target definido.
