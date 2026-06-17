# Fase 5: resultados reales Sensorium 2022

## Descarga

Se descargaron tres zips oficiales desde GIN Sensorium 2022:

| Dataset | Rol | Tamaño zip | SHA-256 |
|---|---|---:|---|
| `static26872-17-20-GrayImageNet-94c6ff995dac583098847cfecd43e7b6` | Sensorium competition mouse 1 | `416M` | `c004994ba0110dcff21273af3e7b759ca30881dabbdc74201e777e89a8ce68d0` |
| `static27204-5-13-GrayImageNet-94c6ff995dac583098847cfecd43e7b6` | Sensorium+ competition mouse 2 | `412M` | `bfafe3589131485ae1a20be643956618e3520c7fbaf25df39e9d7b1ccca9da5d` |
| `static22846-10-16-GrayImageNet-94c6ff995dac583098847cfecd43e7b6` | pretraining mouse | `397M` | `c5baf086e58ef303ebe62cb49da35b73c496f974cc990e973c3f104309cef6da` |

Los tres zips pasaron `unzip -t` sin errores. Los datos no se versionan en Git.

Uso local:

```text
data/sensorium/raw       1.2G
data/sensorium/extracted 3.6G
```

## Estructura observada

| Dataset | Trials | Neuronas | Tiers |
|---|---:|---:|---|
| `static22846` | `5997` | `7344` | `train=4498`, `validation=500`, `test=999` |
| `static26872` | `6955` | `7776` | `train=4474`, `validation=496`, `test=990`, `final_test=995` |
| `static27204` | `6959` | `7538` | `train=4471`, `validation=497`, `test=995`, `final_test=996` |

En los dos datasets de competición (`26872`, `27204`), las respuestas de `test`
y `final_test` están zeroed/retenidas, tal como indica el README oficial. Por
eso la evaluación directa usa `validation`. En `22846`, `test` contiene
respuestas reales y repeticiones, por lo que se ejecutó también como caso de
fiabilidad.

## Baseline usado

Se usa `stimulus_ridge`, una regresión ridge transparente sobre:

- descriptores globales de intensidad;
- descriptor espacial pooled `8 x 8`;
- control `scrambled_stimulus_ridge` con estímulos de entrenamiento permutados.

Además se calcula `stimulus_context_ridge`, que añade covariables de
comportamiento y posición pupilar cuando no están zeroed. El control
`scrambled_stimulus_context_ridge` conserva esas covariables y permuta solo los
estímulos de entrenamiento. Esto permite distinguir mejora por estado
conductual de mejora atribuible a imagen.

Esto sigue siendo un baseline ligero, no SOTA. Su función es comprobar si el
marco detecta señal predictiva antes de introducir modelos visuales profundos.

## Resultados

| Artefacto | Eval tier | Reliability | Mean | Stimulus ridge | Context ridge | Best Δ mean | Best Δ scrambled | MIS |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `static22846_test_mis.json` | `test` | `0.6532` | `0.2404` | `0.2964` | `0.3410` | `0.1006` | `0.0684` | fails |
| `static22846_validation_mis.json` | `validation` | `0.0000` | `0.2301` | `0.2962` | `0.3325` | `0.1024` | `0.0775` | fails |
| `static26872_validation_mis.json` | `validation` | `0.0000` | `0.2212` | `0.2725` | unavailable | `0.0513` | `0.0798` | fails |
| `static27204_validation_mis.json` | `validation` | `0.0000` | `0.2383` | `0.2824` | `0.3152` | `0.0769` | `0.0594` | fails |

`validation` no tiene estímulos repetidos, por eso `reliability=0.0` significa
"no estimable con este cálculo", no ausencia demostrada de fiabilidad neural.
El caso `static22846/test` sí contiene repeticiones y pasa el bloque de
reproducibilidad.

## Interpretación crítica

El caso real ya muestra el patrón que necesitamos para la tesis metodológica:

1. Un baseline visual simple mejora de forma consistente frente a media y frente
   a control permutado.
2. Las covariables conductuales/pupilares mejoran la predicción cuando están
   disponibles, especialmente en `22846`.
3. En `22846/test`, el target tiene fiabilidad por repeticiones.
4. Aun así, el MIS no pasa porque falta evidencia mecanística:
   estructura, perturbación, restricción causal u OOD formal.

Esto no es todavía una contribución Q1 fuerte. Es una base empírica válida para
el siguiente paso: introducir un modelo visual más competitivo o un baseline
oficial Sensorium y evaluar si su ganancia predictiva cambia o no la conclusión
mecanística.
