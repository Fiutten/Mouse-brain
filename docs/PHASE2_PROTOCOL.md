# Protocolo de Fase 2: cualificación del target empírico

## Pregunta

¿Existe un patrón regional de conectividad funcional espontánea suficientemente
estable entre sesiones Allen Visual Behavior Neuropixels como para servir de
objetivo de evaluación fuera de muestra?

## Decisiones fijadas antes del benchmark

- Dataset: Allen Visual Behavior Neuropixels, manifest `0.5.0`.
- Observable: tasa de disparo poblacional por región durante el bloque
  espontáneo más largo.
- Bin temporal: 1 segundo.
- Regiones: `VISp`, `VISl`, `VISal`, `VISrl`, `VISpm`, `VISam`.
- Mínimo: 20 unidades cualificadas por región y sesión.
- Filtro de unidad: `quality == good`, `valid_data`, `amplitude_cutoff < 0.1`,
  `presence_ratio > 0.9`, `isi_violations < 0.5`.
- Evaluación: correlación de FC de cada sesión contra la media de sesiones de
  los ratones restantes. Si un ratón tiene dos sesiones, ambas quedan fuera del
  conjunto de referencia al evaluarlo.
- Control nulo: 1000 permutaciones de etiquetas regionales por sesión.
- Cohorte mínima: 15 sesiones.

Se excluye `LP` porque solo siete sesiones locales alcanzan el mínimo fijado.
No se redujo el umbral de calidad para retenerla.

## Interpretación permitida

La prueba determina si el target agregado tiene fiabilidad entre sesiones y si
supera un control de etiquetas permutadas.

## Interpretación prohibida

- La FC no es conectividad anatómica ni causal.
- Superar el control nulo no valida ningún simulador.
- La agregación regional no representa todas las neuronas de cada área.
- Este análisis no constituye un gemelo digital.

## Puerta de decisión

Solo se construirá un benchmark de modelos sobre este target si:

1. se extraen al menos 15 sesiones;
2. todos los hashes de metadatos coinciden con el manifest;
3. la mediana de correlación FC leave-one-mouse-out es positiva;
4. al menos la mitad de sesiones supera su percentil nulo 95.
