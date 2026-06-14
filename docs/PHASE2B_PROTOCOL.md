# Protocolo de Fase 2b: descomposición de variabilidad y selección de target

## Objetivo

Determinar por qué la FC espontánea regional falló la puerta de Fase 2 y evaluar
dos observables alternativos antes de comparar simuladores.

## Cohorte congelada

Se mantienen sin cambios las 21 sesiones, seis regiones, filtros de unidad y
separación leave-one-mouse-out de Fase 2.

## Análisis confirmatorios de selección

Se comparan tres candidatos:

1. FC espontánea regional con bins de 1 segundo.
2. Perfil regional de tasa espontánea media.
3. Perfil regional de respuesta a cambios visuales, corregido por baseline,
   usando ventanas de 250 ms.

Para cada vector o matriz se calcula:

- correlación leave-one-mouse-out contra la media de ratones restantes;
- fiabilidad interna split-half;
- control nulo con 1000 permutaciones de etiquetas regionales por sesión.
- intervalo bootstrap agrupado por ratón con 5000 remuestras.

Un candidato pasa solo si:

- mediana leave-one-mouse-out `> 0.5`;
- mediana split-half `> 0.5`;
- al menos 50% de sesiones supera su percentil nulo 95.

Si varios candidatos pasan, se elige el de mayor fracción sobre el nulo; se
desempata por mediana leave-one-mouse-out.

## Diagnósticos exploratorios

- sensibilidad de FC a bins de `0.5`, `1`, `2` y `5` segundos;
- sensibilidad a ventanas iniciales de `60`, `120`, `240` segundos y ventana completa;
- asociación de fiabilidad con número mínimo/medio de unidades;
- diferencias descriptivas Familiar/Novel;
- permutación exploratoria de experiencia a nivel de ratón, excluyendo ratones
  con ambas condiciones;
- correlación entre sesiones repetidas del mismo ratón.

Estos diagnósticos no pueden rescatar retrospectivamente un candidato.

## Interpretación prohibida

Ningún target seleccionado constituye conectividad anatómica, conectividad
causal ni validación de un modelo cerebral.
