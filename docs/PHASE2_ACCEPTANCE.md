# Aceptación de Fase 2

## Ejecución del 13 de junio de 2026

- Sesiones NWB locales: 30.
- Sesiones cualificadas y extraídas: 21.
- Ratones únicos: 19.
- Fallos de extracción: 0.
- Hashes BLAKE2b de metadatos Allen válidos: 5 de 5.
- Mediana FC leave-one-mouse-out: `0.5203`.
- Media FC leave-one-mouse-out: `0.4881`.
- Mediana de correlación del perfil regional de tasas: `0.6875`.
- Mediana del control de etiquetas permutadas: `-0.0655`.
- Fracción de sesiones sobre su percentil nulo 95: `0.3810`.
- Mediana split-half dentro de sesión, exploratoria: `0.7537`.
- Mediana leave-one-mouse-out Familiar, exploratoria: `0.6178`.
- Mediana leave-one-mouse-out Novel, exploratoria: `0.4956`.

## Decisión

**Puerta rechazada.** Se cumplen integridad, tamaño de cohorte y mediana positiva,
pero solo el 38.1% de las sesiones supera su control nulo individual, frente al
50% exigido.

No se compararán simuladores contra este target como métrica primaria. El
siguiente trabajo permitido es estudiar, de forma explícitamente exploratoria,
la fuente de variabilidad y preregistrar un observable alternativo. El resultado
negativo se conserva.

Ese trabajo se completó en Fase 2b. Consulta `PHASE2B_ACCEPTANCE.md`.

La diferencia entre la fiabilidad split-half (`0.7537`) y la fiabilidad entre
ratones (`0.5203`) sugiere que la principal limitación no es solo duración de la
ventana. Son plausibles la heterogeneidad entre animales, el muestreo distinto
de unidades y las diferencias de estado/experiencia. Esta interpretación es
exploratoria y no identifica causalmente ninguna fuente.

## Sesiones excluidas por el criterio fijado

| Sesión | Regiones con menos de 20 unidades cualificadas |
|---:|---|
| 1044594870 | VISam |
| 1053718935 | VISrl |
| 1053925378 | VISl |
| 1062755779 | VISp, VISl |
| 1081079981 | VISrl |
| 1081090969 | VISrl |
| 1087720624 | VISam |
| 1092283837 | VISl |
| 1093864136 | VISrl |
