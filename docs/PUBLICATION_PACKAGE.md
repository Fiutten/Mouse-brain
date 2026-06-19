# Paquete publicable actual

## Tesis publicable

La afirmación defendible no es que hayamos construido un cerebro digital. La
afirmación defendible es:

> Un target funcional puede ser altamente reproducible entre animales y aun así
> no ser válido para evaluar modelos anatómico-dinámicos. Proponemos y
> demostramos un protocolo reproducible de validación falsable para distinguir
> reproducibilidad, predictibilidad y valor mecanístico en modelos digitales
> parciales del cerebro de ratón.

## Contribución real

1. Pipeline reproducible para Allen VBN:
   - cualificación por metadatos;
   - extracción NWB read-only;
   - cohortes desarrollo/confirmación;
   - hashes y planes sellados;
   - controles nulos por sesión y por topología.

2. Confirmación positiva de un target temporal:
   - `temporal_derivative`;
   - 20 sesiones confirmatorias;
   - 20 ratones nuevos;
   - correlación mediana `0.8908`;
   - split-half `0.9896`.

3. Falsación de interpretación anatómica:
   - Allen `0.5281`;
   - desconectado `0.5246`;
   - transpuesto `0.5313`;
   - permutaciones `0.5335`;
   - ventaja Allen negativa frente a permutaciones.

4. Diagnóstico de por qué falla:
   - latencias colapsadas en `75 ms`;
   - pares resolubles `0.0`;
   - pares lead-lag no simultáneos `0.0`;
   - la señal está bloqueada al evento y no identifica dirección.

## Claim principal

**Claim fuerte defendible:**

La validación de modelos digitales parciales requiere demostrar que el target
empírico no solo es reproducible, sino también identificador del mecanismo que
se pretende evaluar.

**Claim empírico defendible:**

En Allen VBN, una respuesta visual regional agregada puede ser reproducible y
predictible por un modelo simple, pero no distinguir conectividad anatómica
dirigida de controles nulos.

## Claims que no debemos hacer

- No hemos construido un gemelo digital de cerebro de ratón.
- No hemos demostrado ausencia de propagación visual en ratón.
- No hemos invalidado la conectividad Allen.
- No hemos demostrado un mecanismo neuronal.
- No hemos superado BMTK, TVB, MICrONS ni Allen models.

## Posible estructura de artículo

### Título tentativo

`Reproducible but not mechanistically identifiable: falsifiable validation of
partial digital mouse-brain targets`

### Abstract técnico

1. Motivación: recursos abiertos de cerebro de ratón son potentes pero
   fragmentados.
2. Problema: se confunde reproducibilidad funcional con validez mecanística.
3. Método: protocolo en tres puertas: confirmación del target, benchmark
   anatómico, identificabilidad dirigida.
4. Resultado: target confirmado, hipótesis anatómica rechazada, causa
   diagnosticada.
5. Conclusión: antes de construir modelos más complejos debe validarse la
   identificabilidad del target.

### Secciones

1. Introduction
2. Related work and risk of overclaiming digital twins
3. Dataset and reproducibility protocol
4. Gate 1: functional target confirmation
5. Gate 2: anatomical-topology benchmark
6. Gate 3: directed-signature identifiability
7. Discussion: reproducibility is not mechanism
8. Limitations and future datasets

## Figuras recomendadas

1. **Pipeline completo.**
   Desarrollo, sellado, descarga confirmatoria, confirmación, controles y
   decisión de parada.

2. **Fase 2c positiva.**
   Barras o violín de correlaciones por sesión frente a nulo individual.

3. **Fase 3 negativa.**
   Comparación Allen/desconectado/transpuesto/permutaciones.

4. **Fase 4 diagnóstica.**
   Heatmap de latencias por sesión y región mostrando colapso a `75 ms`.

5. **Diagrama conceptual.**
   Reproducible target ≠ mechanistic target ≠ digital twin.

## Tablas recomendadas

1. Cohortes y filtros.
2. Umbrales preregistrados por fase.
3. Resultados confirmatorios de Fase 2c.
4. Benchmark topológico de Fase 3.
5. Identificabilidad temporal de Fase 4.
6. Qué queda soportado y qué queda rechazado.

## Nivel de novedad

La novedad no está en una arquitectura cerebral nueva. Está en el protocolo:

- separación estricta desarrollo-confirmación;
- cierre explícito de hipótesis negativas;
- controles topológicos recalibrados;
- prueba de identificabilidad antes de complejizar modelos;
- trazabilidad reproducible con datos públicos.

Esto es más metodológico que algorítmico.

## Riesgo editorial

El resultado puede ser visto como demasiado negativo si se presenta como
benchmark sin contribución conceptual. Para hacerlo publicable hay que centrar
el artículo en el problema general:

> cómo evitar construir modelos digitales sobre targets que son reproducibles
> pero no mecanísticamente identificables.

## Venues razonables

Más realistas:

- journals de computational neuroscience;
- journals de neuroinformatics;
- workshops o tracks de reproducibility/benchmarking;
- revistas metodológicas de datos y modelos.

Más difíciles:

- Q1 de IA generalista de alto impacto, salvo que reforcemos la parte de
  benchmarking, reproducibilidad y falsación automática;
- conferencias top de IA, porque no hay un nuevo algoritmo que supere SOTA.

## Qué faltaría para subir ambición

1. Usar el `Mechanistic Identifiability Score` como contribución formal, no
   solo como interpretación verbal.
2. Mantener Allen VBN como caso negativo real.
3. Añadir Sensorium/Dynamic Sensorium como caso predictivo moderno.
4. Decidir MICrONS solo tras un piloto estructura-función acotado.
5. Automatizar generación de tablas finales y auditoría en instalación limpia.

Los detalles técnicos están en
[MECHANISTIC_IDENTIFIABILITY_SCORE.md](MECHANISTIC_IDENTIFIABILITY_SCORE.md) y
[Q1_TECHNICAL_STRATEGY.md](Q1_TECHNICAL_STRATEGY.md).

## Decisión recomendada

Actualización 2026-06-19:

Preparar primero un **paper metodológico fuerte** con el caso Allen VBN cerrado,
el benchmark sintético MIS ampliado, Sensorium/Dynamic Sensorium como caso
predictivo moderno y Sensorium static como caso parcial positivo de fiabilidad y
topografía.

La ruta congelada es:

```text
methodological_benchmark_paper_now_q1_requires_external_piece
```

Esto significa:

- el paquete actual puede sostener un artículo metodológico reproducible;
- no debe venderse todavía como Q1 fuerte de IA;
- el stack oficial Sensorium ya es ejecutable a nivel de smoke test;
- para Q1 hace falta entrenar/evaluar un baseline oficial Sensorium o aprobar
  un piloto MICrONS estructura-función acotado.

Artefactos de decisión:

- `results/publication_freeze/summary.json`
- `results/q1_sensitivity/summary.json`
- `results/sensorium_official_baseline_audit/summary.json`
- `results/microns_pilot_gate/summary.json`
- `results/sensorium_official_baseline_audit/official_model_smoke.json`
