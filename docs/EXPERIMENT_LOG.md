# Registro de experimentos

## 2026-06-17 — Fase 5b: Dynamic Sensorium como prueba de consistencia

### Objetivo

Comprobar si el marco Sensorium/MIS se comporta de forma consistente al pasar
de imágenes estáticas a vídeos dinámicos, sin presentar un baseline ligero como
modelo predictivo moderno.

### Datos

Se descargaron los cinco zips públicos visibles de Dynamic Sensorium 2023 desde
GIN (`dynamic29515`, `dynamic29623`, `dynamic29647`, `dynamic29712`,
`dynamic29755`). Los cinco pasaron `unzip -t`; raw ocupa `48G` y la extracción
`94G`.

### Resultado

La evaluación se realizó sobre `oracle`, porque `live_test_*` y `final_test_*`
tienen respuestas retenidas/zeroed. El tier `oracle` contiene respuestas no
nulas, pero no vídeos repetidos exactos por hash, así que la fiabilidad por
repetición no es estimable.

| Métrica | Mediana |
|---|---:|
| Best predictive correlation | `0.4094` |
| Best Δ mean | `-0.0435` |
| Best Δ scrambled | `0.0521` |
| Reliability estimable | `0/5` |
| MIS score | `0.2222` |

### Decisión

**Caso negativo útil.** El descriptor temporal colapsado captura algo de señal
frente al control scrambled, pero no supera al predictor medio. El MIS falla de
forma correcta porque no hay reproducibilidad estimable, ganancia frente a mean
ni evidencia mecanística. El siguiente paso para una contribución fuerte es
añadir un adaptador a un modelo temporal competitivo u oficial Sensorium y
evaluarlo con la misma separación entre predicción, reproducibilidad e
identificabilidad.

## 2026-06-12 — Gate 1: estructura causal del entorno

### Objetivo

Comprobar antes de entrenar agentes que `SocialSurvivalWorld` contiene una
estructura resoluble, una señal social causalmente relevante y un coste medible
del engaño.

### Configuración

- 250 episodios por política.
- Semilla base: `20260612`.
- Azar y oráculo: entorno con cambio de régimen en el paso 40.
- Seguidores sociales: régimen fijo para aislar el efecto de fiabilidad.
- Comando: `.venv/bin/python scripts/validate_environment.py`.

### Resultado

| Política | Retorno | Peligros | Tasa peligro/paso | Recursos | Pasos |
|---|---:|---:|---:|---:|---:|
| azar | -0.6234 | 0.5080 | 0.0112 | 0.5160 | 63.1400 |
| oráculo privilegiado | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor útil | 14.6982 | 1.3320 | 0.0170 | 16.8280 | 79.7840 |
| seguidor engañado | -2.9876 | 3.0480 | 0.2360 | 0.2040 | 14.3600 |

### Interpretación

El entorno supera el Gate 1 mínimo:

- existe una política privilegiada claramente superior al azar;
- la señal social tiene consecuencias conductuales fuertes;
- el engaño reduce retorno, acceso a recursos y supervivencia;
- las ejecuciones son reproducibles por semilla.

El seguidor útil coincide con el oráculo en régimen fijo porque la señal apunta
directamente al recurso. Esto es útil como control positivo, pero hace que el
entorno sea insuficiente como evidencia científica única.

### Hallazgo metodológico durante la validación

La primera prueba esperaba más encuentros acumulados con peligro bajo engaño.
Falló porque el seguidor engañado muere antes y tiene menos tiempo de exposición.
Se sustituyó el conteo acumulado como contraste principal por la tasa de peligro
por paso. El fallo y la corrección se conservan porque muestran un sesgo de
supervivencia que también deberá controlarse en experimentos futuros.

### Decisión

**Gate 1 aprobado con limitaciones.** Se permite avanzar a baselines simples,
pero no a módulos cognitivos complejos. El siguiente gate debe demostrar que un
agente recurrente puede inferir cambios de régimen mejor que PPO sin memoria.

## 2026-06-12 — Gate 2a: PPO frente a RecurrentPPO en el entorno original

### Objetivo

Comprobar aprendibilidad y buscar una señal recurrente exploratoria antes de
implementar componentes cognitivos.

### Configuración

- PPO: 11 142 parámetros entrenables.
- RecurrentPPO: 30 214 parámetros entrenables.
- 30 000 transiciones por algoritmo y semilla.
- Semillas: 11, 23 y 37.
- 100 episodios de evaluación compartidos por modelo.

### Resultado resumido

| Algoritmo | Semilla | Retorno | Supervivencia | Recursos | Movimiento | Entropía acciones |
|---|---:|---:|---:|---:|---:|---:|
| PPO | 11 | -0.3110 | 0.30 | 0.40 | 0.2205 | 0.7911 |
| PPO | 23 | -0.6144 | 0.02 | 0.06 | 0.2413 | 0.7282 |
| PPO | 37 | -0.6700 | 0.00 | 0.00 | 0.0285 | 0.6926 |
| RecurrentPPO | 11 | -0.6612 | 0.00 | 0.08 | 0.0513 | 0.0000 |
| RecurrentPPO | 23 | -0.6257 | 0.00 | 0.07 | 0.0375 | 0.0000 |
| RecurrentPPO | 37 | -0.6612 | 0.00 | 0.08 | 0.0889 | 0.1067 |

### Interpretación

**Gate 2a rechazado.** Ningún algoritmo aprende de manera estable. RecurrentPPO
colapsa prácticamente a una sola acción y PPO también muestra políticas de baja
movilidad que evitan amenazas, pero no encuentran recursos.

El problema no se resuelve entrenando más. En el régimen engañoso, la única señal
global apunta a la amenaza y no existe una fuente alternativa que informe dónde
está el recurso. Ignorar la señal obliga a una búsqueda casi ciega. El entorno
confunde necesidad de memoria con ausencia de información.

### Decisión

Se congela `SocialSurvivalWorld` como ejemplo negativo. Se diseñará un entorno
separado con dos fuentes observables, una útil y otra engañosa, cuya identidad
oculta cambia. No se permite implementar workspace mientras el nuevo entorno no
supere Gate 1 y Gate 2.

## 2026-06-12 — Gate 2b: dos consejeros observables en rejilla

### Cambio realizado

`SocialInferenceWorld` presenta simultáneamente dos direcciones: una conduce al
recurso y otra a la amenaza. La identidad del consejero útil es oculta y cambia.
El oráculo alcanza retorno `14.6982`; elegir consejero al azar obtiene `-0.5393`.

### Resultado de aprendizaje

Con el mismo protocolo de 30 000 transiciones y tres semillas, ningún PPO ni
RecurrentPPO aprende una política estable. Los retornos están entre `-0.6257` y
`-0.6700`, salvo variaciones menores; la supervivencia es esencialmente cero y
el seguimiento del consejero útil también.

### Decisión

**Gate 2b rechazado.** La tarea todavía confunde inferencia de fuente,
navegación, recompensa dispersa y homeostasis. No se aumentará retrospectivamente
el presupuesto. Se aislará primero la hipótesis de memoria en una tarea mínima
de cambio de consejero.

## 2026-06-12 — Gate 2c: diagnóstico aislado de memoria

### Diseño

`AdvisorSwitchTask` elimina navegación, metabolismo y recompensa dispersa. El
agente elige uno de dos consejeros. Solo observa el resultado anterior; para
aplicar una estrategia `win-stay/lose-shift` debe recordar también su acción
anterior. La identidad útil cambia antes de puntuar la acción del paso 20.

El criterio fijado antes de ejecutar fue que RecurrentPPO superase `0.80` de
precisión post-cambio en las tres semillas.

### Resultados

| Algoritmo | Semilla | Retorno | Precisión pre | Precisión post | Primeros 5 post |
|---|---:|---:|---:|---:|---:|
| PPO | 11 | -1.80 | 0.7395 | 0.2405 | 0.2020 |
| PPO | 23 | -1.80 | 0.7395 | 0.2405 | 0.2020 |
| PPO | 37 | -2.20 | 0.7342 | 0.2357 | 0.1980 |
| RecurrentPPO | 11 | 29.09 | 0.8692 | 0.8586 | 0.5050 |
| RecurrentPPO | 23 | 22.89 | 0.8421 | 0.7355 | 0.4950 |
| RecurrentPPO | 37 | 25.11 | 0.6613 | 0.9519 | 0.7980 |

La media post-cambio es aproximadamente `0.239` para PPO y `0.849` para
RecurrentPPO. La precisión máxima posible en los primeros cinco pasos post-cambio
es `0.80`, porque la primera elección ocurre antes de disponer de evidencia del
cambio.

### Decisión

**Gate 2c rechazado según el umbral preregistrado:** RecurrentPPO supera `0.80`
en dos de tres semillas, no en las tres.

Existe una señal clara de que el estado recurrente permite resolver la tarea,
pero la optimización no es suficientemente estable para usarla como baseline
científico. No se implementará workspace todavía.

El siguiente paso permitido es desarrollar una configuración recurrente estable
usando semillas distintas de 11, 23 y 37. Después se congelará la configuración
y se realizará una confirmación única con semillas nuevas.

## 2026-06-12 — Gate 2d: estabilización y confirmación independiente

### Desarrollo

Se evaluaron cuatro configuraciones con semillas 41, 43 y 47. La selección se
realizó por la peor precisión post-cambio:

| Configuración | Peor precisión post | Media post | Parámetros |
|---|---:|---:|---:|
| `shared_default` | 0.7119 | 0.8172 | 25 667 |
| `shared_low_lr` | 0.5912 | 0.6659 | 25 667 |
| `shared_long_rollout` | 0.4950 | 0.8237 | 25 667 |
| `separate_actor_critic` | 0.4243 | 0.7608 | 42 819 |

`shared_default` fue congelada antes de abrir las semillas confirmatorias. El
rollout largo tenía mejor media, pero colapsó en una semilla y fue descartado
por el criterio robusto preregistrado.

### Confirmación única

El criterio exigía superar `0.80` en las cinco semillas:

| Semilla | Precisión post | Supera 0.80 |
|---:|---:|---:|
| 101 | 0.4810 | no |
| 103 | 0.6926 | no |
| 107 | 0.8110 | sí |
| 109 | 1.0000 | sí |
| 113 | 0.5050 | no |

### Decisión

**Gate 2d rechazado.** RecurrentPPO no es un baseline estable para esta tarea
bajo el protocolo fijado. No habrá más ajuste sobre estas semillas ni se usará
su mejor ejecución como evidencia.

Para separar validez de tarea y fallo de optimización, se evalúa a continuación
un controlador determinista de memoria mínima `win-stay/lose-shift`.

## 2026-06-12 — Gate 2e: control de validez con memoria mínima

### Resultados

| Referencia | Retorno | Precisión pre | Precisión post | Primeros 5 post |
|---|---:|---:|---:|---:|
| azar | -0.3920 | 0.4943 | 0.4958 | 0.4856 |
| siempre consejero 0 | 0.0320 | 0.4920 | 0.5080 | 0.5080 |
| `win-stay/lose-shift` | 36.9240 | 0.9717 | 0.9524 | 0.8000 |

### Interpretación y decisión

La tarea diagnóstica es válida y puede resolverse casi óptimamente con memoria
funcional mínima. El fallo confirmatorio corresponde a la optimización de
RecurrentPPO, no a una tarea irresoluble.

No se continuará ajustando RecurrentPPO. El siguiente experimento deberá añadir
explícitamente la acción anterior a la observación de PPO, convirtiendo la tarea
en Markov. Esto permitirá contrastar:

- PPO reactivo sin estado suficiente;
- PPO reactivo con estado mínimo explícito;
- controlador determinista con un bit funcional de memoria;
- RecurrentPPO que debe aprender internamente ese estado.

Este control es obligatorio antes de diseñar workspace: el benchmark actual solo
requiere recordar una acción, no coordinación cognitiva global.

## 2026-06-13 — Gate 2f: PPO con estado mínimo explícito

### Diseño

`MarkovAdvisorSwitchTask` añade únicamente la acción anterior a la observación.
Se mantuvieron PPO, dinámica, presupuesto de 30 000 transiciones y evaluación de
200 episodios. El criterio exigía precisión post-cambio superior a `0.90` en las
cinco semillas selladas.

### Resultados

| Semilla | Retorno | Precisión pre | Precisión post | Supera 0.90 |
|---:|---:|---:|---:|---:|
| 127 | 18.00 | 0.7342 | 0.7167 | no |
| 131 | 18.00 | 0.7342 | 0.7167 | no |
| 137 | 18.00 | 0.7395 | 0.7119 | no |
| 139 | 18.00 | 0.7342 | 0.7167 | no |
| 149 | 37.01 | 0.9739 | 0.9524 | sí |

### Auditoría de la política

Las semillas 127, 131 y 139 aprenden tres transiciones correctas, pero cambian
erróneamente a la acción 0 después de obtener recompensa positiva con la acción
1. La semilla 137 presenta el fallo simétrico para la acción 0. La semilla 149
aprende las cuatro transiciones `win-stay/lose-shift`.

### Decisión

**Gate 2f rechazado.** Exponer el estado mínimo eleva fuertemente el rendimiento,
pero PPO continúa siendo inestable por ruptura de simetría y exploración
insuficiente de uno de los estados positivos.

Según el roadmap, se pausa el desarrollo arquitectónico. El siguiente paso no
es ajustar PPO ni construir workspace: se auditará el stack mediante un baseline
tabular exacto sobre el mismo MDP.

## 2026-06-15 — MouseBrainBench Fase 2c: confirmación funcional externa

### Diseño

Las 21 sesiones locales de desarrollo se usaron para seleccionar una única
transformación temporal. `temporal_derivative` quedó sellada antes de descargar
una cohorte confirmatoria de 20 sesiones pertenecientes a 20 ratones nuevos,
equilibrada entre Familiar y Novel.

### Confirmación única

| Métrica | Resultado | Umbral | Pasa |
|---|---:|---:|---|
| Correlación mediana entre ratones | 0.8908 | > 0.50 | sí |
| Split-half mediano | 0.9896 | > 0.70 | sí |
| Sesiones sobre nulo individual 95% | 75% | >= 50% | sí |
| Límite inferior bootstrap agrupado | 0.8417 | > 0 | sí |

Se procesaron las 20 sesiones sin fallos. El intervalo bootstrap agrupado fue
`[0.8417, 0.9214]`. El análisis se ejecutó una vez desde el commit `3b07ce3`.

### Decisión

**Target confirmado.** Puede utilizarse como variable funcional fuera de muestra
para evaluar modelos mesoscópicos. El resultado no valida un mecanismo,
conectividad efectiva ni un gemelo digital.

La siguiente puerta comprobará si conectividad Allen MCModels predice el target
mejor que topologías nulas emparejadas, calibrando únicamente sobre la cohorte de
desarrollo.

## 2026-06-15 — MouseBrainBench Fase 3: benchmark anatómico-funcional

### Diseño

Se construyó una matriz dirigida de seis áreas visuales a partir de 200
experimentos oficiales de trazado Allen. `LinearRateModel` y `WilsonCowanModel`
se calibraron sobre 21 sesiones de desarrollo. El modelo lineal fue seleccionado
y comparado contra un grafo desconectado, el grafo transpuesto y cien
permutaciones de pesos, todas recalibradas en desarrollo.

### Desarrollo

Allen obtuvo correlación mediana `0.5836`, pero solo superó el 27% de
permutaciones. El desconectado obtuvo `0.5731` y el transpuesto `0.5875`. La
configuración completa se selló en el commit `673e5cc`.

### Confirmación única

| Topología | Correlación mediana |
|---|---:|
| Allen | 0.5281 |
| Desconectada | 0.5246 |
| Transpuesta | 0.5313 |
| Mediana de permutaciones | 0.5335 |

Allen superó solo el 21% de permutaciones. La ventaja pareada frente a la
mediana de permutaciones fue negativa, con IC95%
`[-0.0075, -0.0012]`.

### Decisión

**Hipótesis anatómica rechazada bajo el protocolo.** La dinámica lineal captura
parte de la respuesta temporal, pero la topología Allen no explica ese
rendimiento. No se añadirá complejidad al mismo target para rescatar la
hipótesis.

La siguiente puerta deberá demostrar primero que existe una firma funcional
reproducible de propagación dirigida.

## 2026-06-16 — MouseBrainBench Fase 4: identificabilidad dirigida

### Diseño

Se analizaron únicamente las 21 sesiones de desarrollo. Se midieron latencias
regionales y signos lead-lag con bins de `50 ms`, comparando split-half,
leave-one-mouse-out, permutaciones de etiquetas regionales y pseudo-eventos
desplazados `+10 s`.

### Resultados

| Criterio | Resultado | Decisión |
|---|---:|---|
| Latencia cross-mouse tau | 0.0000 | falla |
| Latencia split-half tau | 0.0000 | falla |
| Latencias sobre nulo 95% | 0% | falla |
| Pares con latencia resoluble | 0.0000 | falla |
| Lead-lag cross-mouse | 1.0000 | pasa |
| Lead-lag split-half | 1.0000 | pasa |
| Lead-lag sobre nulo 95% | 0% | falla |
| Pares lead-lag no simultáneos | 0.0000 | falla |

### Decisión

**Firma dirigida no soportada.** La respuesta confirmada en Fase 2c es
reproducible, pero no identifica propagación dirigida a esta resolución. No se
debe construir un modelo anatómico más complejo sobre este target.
