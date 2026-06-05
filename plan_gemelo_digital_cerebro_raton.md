# Plan critico: gemelo digital modular de cerebro de raton

## Decision principal

La especie base debe ser **Mus musculus, raton de laboratorio adulto**.

Motivo: es el mamifero con mejor ecosistema abierto para construir un modelo defendible:

- Allen Mouse Brain Common Coordinate Framework como atlas 3D de referencia.
- Allen Mouse Brain Connectivity Atlas para conectividad mesoscale.
- Allen Brain Observatory y Visual Behavior Neuropixels para actividad neural y conducta.
- bases de datos de tipos celulares, transcriptomica, morfologia y electrofisiologia.
- literatura abundante sobre corteza, talamo, hipocampo, ganglios basales, cerebelo y tronco.

No elegimos reptil como especie principal. Aunque un reptil tiene interes evolutivo y una organizacion pallial distinta, hay menos datos estandarizados, menos conectividad sistematica y menos benchmarks funcionales. Usarlo ahora aumentaria el riesgo de construir una maqueta especulativa.

## Pregunta cientifica defendible

No vamos a intentar demostrar "conciencia digital".

La pregunta defendible es:

> Que arquitectura neurocomputacional minima, organizada por regiones cerebrales de mamifero, reproduce integracion sensoriomotora, memoria activa, seleccion flexible de accion y estados globales comparables a correlatos funcionales de acceso consciente?

Esto permite hablar de:

- integracion global;
- acceso/broadcasting;
- estados de vigilia/sueno simplificados;
- atencion;
- memoria de trabajo;
- seleccion de accion;
- perturbacion y recuperacion del sistema.

Pero no permite afirmar experiencia subjetiva.

## Tesis provisional

Un modelo modular por regiones, calibrado con conectividad mesoscale y dinamica neural simplificada, puede reproducir propiedades funcionales asociadas a acceso global y control adaptativo con menos detalle celular del que requiere una emulacion completa.

La contribucion potencial no seria "hemos creado conciencia", sino:

1. una arquitectura regional biologicamente restringida;
2. un protocolo de validacion contra datos reales y tareas conductuales;
3. un analisis de que modulos son necesarios para integracion global y conducta flexible;
4. una ruta incremental hacia mayor detalle biologico.

## Nivel de escala

El proyecto debe avanzar en capas. Cada capa tiene que funcionar y validarse antes de pasar a la siguiente.

### Nivel 0: grafo regional funcional

Representacion:

- cada region cerebral es un nodo dinamico;
- las conexiones son pesos dirigidos derivados de conectividad mesoscale;
- la dinamica puede ser neural mass, rate model o sistema de estado;
- entrada sensorial y salida motora simplificadas.

Regiones iniciales:

- corteza visual primaria y areas visuales superiores;
- talamo visual;
- hipocampo;
- corteza prefrontal/association cortex aproximada;
- ganglios basales;
- amigdala;
- hipotalamo;
- cerebelo;
- tronco encefalico/arousal system.

Objetivo:

- tener un sistema cerrado que percibe, mantiene estado interno, elige accion y cambia de regimen dinamico.

Validacion:

- estabilidad dinamica;
- oscilaciones/regimenes globales plausibles;
- respuesta a lesiones virtuales;
- comparacion cualitativa/cuantitativa con conectividad y actividad regional.

### Nivel 1: poblaciones neuronales por region

Representacion:

- cada region contiene poblaciones excitatorias, inhibitorias y moduladoras;
- dinamica spiking LIF/AdEx o rate-spiking hibrida;
- conectividad interregional fija o parcialmente aprendible;
- neuromodulacion global simplificada.

Objetivo:

- pasar de regiones abstractas a poblaciones con spikes, sparsity y retardos.

Validacion:

- firing rates plausibles por region;
- balance excitacion/inhibicion;
- propagacion sensorial;
- patrones de sincronizacion/desincronizacion;
- sensibilidad a perturbaciones.

### Nivel 2: microcircuitos seleccionados

No detallaremos todo el cerebro. Elegiremos 2-3 regiones criticas:

- V1/talamo visual para entrada sensorial;
- hipocampo para memoria espacial/contextual;
- ganglios basales para seleccion de accion;
- opcion posterior: corteza prefrontal/association cortex para memoria de trabajo.

Representacion:

- capas corticales donde proceda;
- tipos celulares principales;
- retardos sinapticos;
- plasticidad local;
- neuromodulacion dopaminergica en seleccion/aprendizaje.

Objetivo:

- explicar como los detalles locales cambian la funcion global.

Validacion:

- tareas de decision visual;
- navegacion simple;
- aprendizaje por recompensa;
- lesion virtual de hipocampo/ganglios basales/talamo.

### Nivel 3: gemelo digital calibrable

Solo cuando los niveles anteriores funcionen.

Representacion:

- parametros inferidos desde datos reales;
- ajuste por individuo/dataset cuando exista;
- asimilacion de datos de actividad neural.

Objetivo:

- pasar de "modelo generico del raton" a "instancia calibrada contra datos".

Validacion:

- prediccion de actividad retenida;
- generalizacion a estimulos no vistos;
- prediccion de efecto de perturbaciones.

## Arquitectura funcional inicial

El primer prototipo no debe ser biologicamente maximalista. Debe ser cerrado, medible y extensible.

### Modulos

1. Sensorial:
   - entrada visual simplificada;
   - codificacion temporal/event-based opcional.

2. Talamo:
   - relay y gating sensorial;
   - control de ganancia.

3. Corteza sensorial:
   - extraccion de caracteristicas;
   - recurrent processing local.

4. Hipocampo:
   - memoria de estado/contexto;
   - asociacion episodio-lugar-objetivo.

5. Ganglios basales:
   - seleccion de accion;
   - aprendizaje por recompensa;
   - competencia entre politicas.

6. Sistema de arousal/neuromodulacion:
   - variable global de alerta;
   - dopamina para error de recompensa;
   - acetilcolina/noradrenalina simplificadas como incertidumbre y ganancia.

7. Workspace funcional:
   - no se presenta como "conciencia";
   - sirve como mecanismo de acceso global entre percepcion, memoria y accion.

## Tareas iniciales

Las tareas deben ser lo bastante simples para correr, pero no triviales.

1. Decision visual con memoria corta:
   - estimulo visual;
   - retardo;
   - eleccion;
   - recompensa.

2. Navegacion 2D simplificada:
   - agente en entorno pequeno;
   - claves visuales;
   - objetivo cambiante;
   - memoria contextual.

3. Reversal learning:
   - cambia la regla de recompensa;
   - mide adaptacion, perseveracion y recuperacion.

4. Lesion virtual:
   - apagar hipocampo, talamo, ganglios basales o workspace;
   - comprobar deficits esperados.

## Criterios de exito

El modelo solo avanza de nivel si cumple criterios medibles.

- reproduce patrones cualitativamente esperados tras lesion;
- mejora sobre ablations no regionales;
- mantiene conducta flexible bajo cambio de regla;
- genera dinamicas internas interpretables;
- permite mapear variables del modelo a regiones/circuitos;
- no depende de un ajuste manual fragil.

## Criterios de fracaso

Debemos descartar o pivotar si ocurre alguno:

- el modelo solo funciona por aprendizaje end-to-end sin que la arquitectura regional importe;
- las regiones son decorativas y no explican conducta;
- no hay datos suficientes para calibrar o validar;
- la dinamica interna no es mas informativa que una RNN/Transformer pequena;
- el argumento de conciencia empieza a depender de retorica en vez de mediciones.

## Stack tecnico recomendado

Fase inicial:

- Python;
- PyTorch;
- NumPy/SciPy;
- NetworkX;
- Gymnasium/PettingZoo o entorno 2D propio;
- Matplotlib/Plotly;
- AllenSDK para datos cuando empecemos calibracion.

Fase spiking:

- snnTorch o SpikingJelly para SNN entrenables;
- Brian2 para simulacion neurocientifica mas explicita;
- Brian2CUDA solo si necesitamos escala GPU.

Fase multiescala:

- formato de configuracion YAML/JSON para regiones;
- exportacion de actividad a NWB/HDF5 si queremos alinearnos con neurodatos.

## Declaracion sobre conciencia

No afirmaremos que el sistema es consciente.

Podremos estudiar:

- acceso global;
- integracion funcional;
- memoria de trabajo;
- sensibilidad a perturbacion;
- estados globales;
- reportabilidad en sentido computacional;
- correlatos dinamicos inspirados en teorias de conciencia.

La frase cientificamente aceptable seria:

> El modelo permite investigar condiciones funcionales y arquitectonicas asociadas a correlatos de acceso consciente en cerebros de mamifero, sin asumir ni demostrar experiencia subjetiva.

## Primer entregable recomendado

Construir un prototipo Nivel 0:

- grafo regional de raton simplificado;
- dinamica regional;
- tarea visual con memoria y seleccion de accion;
- lesiones virtuales;
- visualizacion de actividad por region;
- comparacion contra un baseline no modular.

Si Nivel 0 no muestra ventajas interpretables frente a un baseline simple, no debemos pasar a niveles mas biologicos.

