# Protocolo experimental preliminar

Este documento fija las reglas antes de entrenar arquitecturas complejas. No es
una preregistración pública todavía; es un contrato interno contra decisiones
retrospectivas.

## Pregunta primaria

¿Un canal de broadcast limitado entre módulos mejora la adaptación después de
un cambio de régimen oculto frente a arquitecturas emparejadas sin broadcast?

## Hipótesis

### H1: adaptación fuera de distribución

Un agente con broadcast limitado tendrá menor arrepentimiento acumulado durante
los primeros pasos posteriores a un cambio de régimen no visto.

### H2: lesión específica

Corromper o retrasar el broadcast reducirá especialmente el rendimiento en
tareas que requieren integrar información social, espacial y corporal, pero no
en controles unimodales.

### H3: cuello de botella

Existirá un rango intermedio de capacidad del workspace que preserve
generalización. Si más capacidad siempre mejora el resultado, la explicación de
cuello de botella no estará apoyada.

## Variable experimental primaria

Mecanismo de comunicación entre módulos:

- broadcast competitivo limitado;
- concatenación completa emparejada;
- memoria recurrente emparejada;
- broadcast barajado o retrasado;
- módulos aislados.

Todos los agentes deben recibir la misma información, usar un presupuesto de
parámetros comparable y entrenarse con el mismo número de transiciones.

## Entorno mínimo

`SocialSurvivalWorld` es un POMDP de rejilla destinado a validar el protocolo,
no a sostener por sí solo una publicación.

- El agente observa únicamente una vecindad local.
- Una señal social recomienda una dirección.
- La señal puede ser útil o engañosa según un régimen oculto.
- El régimen puede cambiar durante el episodio.
- Energía y estrés introducen consecuencias homeostáticas observables.
- Las variables ocultas solo aparecen en `info` para evaluación, nunca en la
  observación del agente.

## Métrica primaria

Arrepentimiento post-cambio durante una ventana fijada antes del entrenamiento:

`retorno del oráculo - retorno del agente`.

## Métricas secundarias

- retorno y supervivencia;
- tasa de peligro por paso, evitando sesgo por distinta supervivencia;
- tiempo hasta recuperar rendimiento tras el cambio;
- calibración de confianza;
- éxito al integrar modalidades;
- información mutua entre broadcast y variables latentes;
- efecto causal de lesiones;
- coste computacional y eficiencia muestral.

## Diseño de evaluación

- Semillas de entrenamiento y evaluación separadas.
- Regímenes, mapas y composiciones retenidos durante entrenamiento.
- Intervalos de confianza por semilla.
- Comparaciones pareadas y corrección por multiplicidad.
- Una métrica primaria; el resto se declara secundario.
- Reportar resultados negativos.

## Puertas de decisión

### Gate 1: validez del entorno

Debe existir una política simple mejor que azar, una política oráculo claramente
superior y ninguna fuga de las variables ocultas.

### Gate 2: baselines

PPO y un baseline recurrente deben aprender de forma estable. Si no lo hacen,
no se evaluará ninguna arquitectura cognitiva.

El primer piloto PPO/RecurrentPPO es una prueba de aprendibilidad, no una
comparación causal entre arquitecturas. Se registrarán parámetros y presupuesto,
pero no se afirmará una ventaja de memoria hasta construir controles emparejados.

#### Protocolo piloto fijado

- Algoritmos: PPO `MultiInputPolicy` y RecurrentPPO `MultiInputLstmPolicy`.
- Transiciones de entrenamiento: 30 000 por algoritmo y semilla.
- Semillas de entrenamiento: 11, 23 y 37.
- Episodios de evaluación: 100 por semilla, con semillas no usadas al entrenar.
- Métrica primaria del gate: retorno post-cambio medio.
- Métricas secundarias: retorno total, retorno pre-cambio, supervivencia,
  recursos, tasa de peligro por paso y seguimiento de la señal social antes y
  después del cambio.
- Interpretación permitida: aprendibilidad y presencia o ausencia de señal
  recurrente exploratoria.
- Interpretación prohibida: superioridad causal de memoria o workspace.

#### Gate 2c: diagnóstico aislado de memoria

Tras rechazar los entornos de rejilla como pruebas de aprendibilidad, se fija
una tarea diagnóstica mínima antes de ejecutarla:

- Tarea: escoger entre dos consejeros; la identidad útil cambia una vez.
- Observación: únicamente el resultado anterior.
- Información necesaria: resultado anterior + acción anterior.
- PPO feed-forward no recibe la acción anterior.
- RecurrentPPO puede mantenerla en estado recurrente.
- Presupuesto: 30 000 transiciones, semillas 11, 23 y 37.
- Evaluación: 200 episodios retenidos.
- Métrica primaria: precisión post-cambio.
- Umbral de continuidad: RecurrentPPO debe superar `0.80` de precisión
  post-cambio en las tres semillas.
- Si no supera el umbral, se rechaza esta configuración recurrente.

#### Gate 2d: estabilización y confirmación recurrente

La estabilización se divide estrictamente en desarrollo y confirmación.

- Semillas de desarrollo: 41, 43 y 47.
- Presupuesto por entrenamiento: 30 000 transiciones.
- Episodios de evaluación por modelo: 200.
- Criterio de selección: maximizar la peor precisión post-cambio entre semillas;
  desempatar por media post-cambio y después por menor número de parámetros.
- Configuraciones candidatas:
  - `shared_default`: configuración usada en Gate 2c.
  - `shared_low_lr`: recurrencia compartida con tasa `1e-4`.
  - `shared_long_rollout`: rollout `512`, batch `128`, diez épocas.
  - `separate_actor_critic`: LSTM separadas para actor y crítico.
- Semillas confirmatorias selladas: 101, 103, 107, 109 y 113.
- La configuración seleccionada se congelará antes de abrir la confirmación.
- Criterio confirmatorio: precisión post-cambio superior a `0.80` en las cinco
  semillas.
- No se reajustará la configuración después de observar la confirmación.

#### Gate 2f: control Markov con acción anterior explícita

Este control prueba si la inestabilidad observada procede de aprender y
conservar internamente el único estado faltante.

- Entorno: misma dinámica que `AdvisorSwitchTask`.
- Diferencia única: la observación incluye `previous_action`.
- Algoritmo: PPO feed-forward con la configuración base ya utilizada.
- Presupuesto: 30 000 transiciones por semilla.
- Semillas selladas: 127, 131, 137, 139 y 149.
- Evaluación: 200 episodios retenidos por modelo.
- Métrica primaria: precisión post-cambio.
- Criterio de éxito: precisión post-cambio superior a `0.90` en las cinco
  semillas.
- No se ajustarán hiperparámetros después de observar este resultado.

### Gate 3: prueba del workspace

La ventaja debe sobrevivir al emparejamiento de parámetros, información,
entrenamiento y búsqueda de hiperparámetros.

### Gate 4: generalización

La ventaja debe replicarse en al menos otra familia de entornos o se considerará
específica del benchmark.
