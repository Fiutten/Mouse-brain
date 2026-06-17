# Mechanistic Identifiability Score

## Propósito

El `Mechanistic Identifiability Score` (MIS) no mide si un modelo predice bien
en abstracto. Mide si una afirmación mecanística parcial es defendible con la
evidencia disponible.

La motivación viene de un riesgo concreto del proyecto: una señal neural puede
ser reproducible, predictible y aun así no identificar el mecanismo anatómico o
dinámico que queremos evaluar.

## Definición operacional

El MIS se compone de tres bloques no intercambiables:

1. `reproducibility`: el target empírico es estable entre sesiones, animales o
   particiones independientes.
2. `topology_specificity`: el modelo que conserva la hipótesis anatómica supera
   controles nulos razonables, como grafos permutados, desconectados o
   transpuestos recalibrados.
3. `directed_identifiability`: el target contiene información suficiente para
   resolver dirección, latencia, lead-lag o una firma dinámica equivalente.

Cada bloque contiene criterios preregistrados. Cada criterio tiene:

- nombre;
- valor observado;
- umbral;
- dirección de comparación;
- decisión binaria;
- puntuación normalizada descriptiva en `[0, 1]`.

La decisión global es conjuntiva:

```text
MIS pasa si y solo si pasan todos los bloques.
```

Esto es deliberado. Un resultado excelente en reproducibilidad no puede
compensar un fallo en topología o dirección, porque esos bloques responden
preguntas científicas distintas.

## Interpretación

`passed = true` significa que el modelo/target supera los requisitos mínimos
para una afirmación mecanística parcial dentro de la definición usada.

`passed = false` no significa que el dataset sea inútil ni que el modelo no
prediga. Significa que el paquete modelo-target no soporta la afirmación
mecanística concreta.

## Casos incluidos

### Benchmark sintético con verdad conocida

El script `mousebrainbench-synthetic-mis` genera dos casos:

- `directed_truth`: señal dirigida con latencias regionales conocidas.
- `common_drive_nonidentifiable`: señal reproducible y predictible, pero sin
  estructura dirigida identificable.

El resultado esperado es que el primer caso pase MIS y el segundo falle. Esto
comprueba que el score no confunde reproducibilidad con mecanismo.

Artefacto:

```text
results/synthetic_identifiability_benchmark.json
```

### Allen VBN como caso negativo real

El script `mousebrainbench-allen-mis` aplica MIS a los resultados sellados de
Fase 2c, Fase 3 y Fase 4.

Resultado actual:

- `reproducibility`: pasa.
- `topology_specificity`: falla.
- `directed_identifiability`: falla.

Conclusión:

```text
reproducible_target_without_mechanistic_identifiability
```

Este resultado es útil porque evita una afirmación excesiva: Allen VBN contiene
un target evocado reproducible, pero este target no debe usarse como evidencia
de conectividad anatómico-dinámica dirigida.

Artefacto:

```text
results/allen_vbn_mechanistic_identifiability_score.json
```

## Límites

El MIS no es todavía un estándar externo. Es una propuesta interna formalizada
para hacer falsables nuestras afirmaciones. Para convertirlo en contribución Q1
necesitamos aplicarlo a más de un régimen:

- un caso negativo real, ya cubierto por Allen VBN;
- un caso positivo/predictivo moderno, candidato: Sensorium/Dynamic Sensorium;
- opcionalmente un caso estructura-función de alta resolución, candidato:
  MICrONS en escala piloto.

