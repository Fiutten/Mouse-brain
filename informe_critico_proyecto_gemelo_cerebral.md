# Informe critico del proyecto: gemelo cerebral modular de raton

Fecha: 3 de junio de 2026

## 1. Veredicto ejecutivo

La propuesta original, entendida como "simular un cerebro de mamifero por regiones y afinarlo todo al detalle", no es defendible como innovacion cientifica fuerte si se mantiene en esos terminos. Es demasiado amplia, demasiado dificil de validar y demasiado cercana a promesas habituales del area de digital brain twins.

La version defendible debe ser mas estrecha:

> Construir un gemelo funcional modular de cerebro de raton para tareas de percepcion-decision-accion, calibrado y evaluado contra datos abiertos de actividad neural y conducta, con capacidad de lesion virtual, prediccion contrafactual y analisis de contribucion regional.

El potencial cientifico no esta en afirmar que hemos simulado conciencia ni en hacer una maqueta anatomica. Esta en convertir datos neurofisiologicos distribuidos en un modelo causal, modular y falsable que permita responder preguntas del tipo:

- que regiones son necesarias para transformar estimulos visuales en decisiones y acciones;
- que variables internas explican eleccion, accion, engagement, memoria corta y sesgo previo;
- que ocurre al lesionar virtualmente talamo, corteza visual, ganglios basales, hipocampo o modulos de arousal;
- hasta que punto una arquitectura regional biologicamente restringida predice mejor que una red generica no modular.

Mi recomendacion es no intentar un "whole-brain digital twin" en sentido fuerte. Recomiendo un proyecto incremental con primer objetivo publicable en modelado computacional/neuroAI:

> Regional causal digital twin of mouse visual decision-making.

## 2. Estado del arte relevante

### 2.1 Digital twins cerebrales

El concepto de virtual brain twin ya existe y esta bien establecido, sobre todo en neuroimagen, epilepsia, medicina personalizada y simulacion mecanicista de redes cerebrales. Revisiones recientes definen estos modelos como replicas generativas, personalizadas y adaptativas del cerebro a nivel de sistema, ligadas a datos estructurales/funcionales y a inferencia.

Implicacion: no podemos vender "digital twin cerebral" como novedad por si mismo.

Referencias clave:

- Virtual brain twins: from basic neuroscience to clinical use. National Science Review, 2024.
- Principles and Operation of Virtual Brain Twins. IEEE Reviews in Biomedical Engineering, 2025.
- Digital Twin Brain: A Bridge between Biological and Artificial Intelligence. Intelligent Computing, 2023.

### 2.2 Digital twins de corteza visual de raton

En 2025 hubo un resultado fuerte: un foundation model de actividad neural de corteza visual de raton, publicado en Nature, predice respuestas neuronales a estimulos visuales nuevos y se presenta como avance hacia un gemelo funcional del sistema visual de raton.

Esto es importante porque bloquea una ruta facil: no podemos proponer simplemente "predecir actividad de V1 con un modelo profundo". Eso ya existe con muy alto nivel.

Referencias clave:

- Foundation model of neural activity predicts response to new stimulus types. Nature, 2025.
- Functional connectomics spanning multiple areas of mouse visual cortex. Nature, 2025.
- Functional connectomics reveals general wiring rule in mouse visual cortex. Nature, 2025.

### 2.3 Datos disponibles de raton

Aqui esta nuestra ventaja practica. Hay datasets abiertos y suficientemente ricos:

- Allen Brain Observatory Visual Coding y Visual Behavior Neuropixels.
- International Brain Laboratory, con datos brain-wide de decision-making.
- MICrONS, con funcional connectomics de corteza visual.
- DANDI, AllenSDK y recursos asociados.

Estos datasets permiten validar modelos contra actividad real, no solo contra tareas simuladas.

Referencias clave:

- Distributed coding of choice, action and engagement across the mouse brain. Nature, 2019.
- Brain-wide dynamics linking sensation to action during decision-making. Nature, 2024.
- Brain-wide representations of prior information in mouse decision-making. Nature, 2025.
- Allen Visual Behavior Neuropixels dataset.

### 2.4 Conciencia

No hay base para afirmar que el sistema simularia conciencia. En 2025 se publico un test adversarial entre Global Neuronal Workspace e Integrated Information Theory. El resultado relevante para nosotros es que incluso teorias principales siguen en disputa y requieren protocolos experimentales especificos.

Podemos modelar correlatos funcionales:

- acceso global;
- broadcasting;
- memoria activa;
- integracion sensoriomotora;
- estados de arousal/engagement;
- sensibilidad a perturbacion.

No podemos afirmar experiencia subjetiva.

Referencia clave:

- Adversarial testing of global neuronal workspace and integrated information theories of consciousness. Nature, 2025.

## 3. Donde esta realmente el potencial

### Potencial 1: modelo regional causal, no solo predictivo

Los modelos fundacionales de corteza visual predicen actividad neural con mucha potencia, pero tienden a ser cajas negras centradas en vision. Nuestro potencial seria construir un modelo que no solo prediga actividad, sino que permita intervenciones virtuales:

- lesion de regiones;
- bloqueo de conexiones;
- alteracion de ganancia talamica;
- cambios de arousal;
- modificacion de sesgo previo;
- perturbacion de circuitos de accion.

Esto es mas cercano a una herramienta cientifica que a un predictor.

### Potencial 2: puente entre datos brain-wide y arquitectura funcional

Los datasets brain-wide muestran que decision, accion y engagement estan distribuidos. La contribucion posible es imponer una arquitectura modular biologicamente motivada y evaluar si explica mejor la distribucion de variables conductuales/neuronales que modelos sin estructura regional.

La pregunta defendible:

> La modularidad neuroanatomica mejora la capacidad de generalizar y hacer contrafactuales en tareas de decision visual?

### Potencial 3: simulador falsable de lesiones virtuales

Un resultado publicable podria ser que el modelo reproduce deficits esperados bajo lesiones:

- lesion de corteza visual: baja sensibilidad al estimulo;
- lesion talamica: degradacion de gating y ganancia sensorial;
- lesion de ganglios basales: deficit de seleccion de accion o perseveracion;
- lesion de hipocampo/contexto: peor adaptacion en cambios de regla;
- lesion de arousal: cambios en latencia, engagement y variabilidad.

Esto debe compararse con datos reales si existen o con predicciones claramente formuladas.

### Potencial 4: benchmark de gemelos cerebrales funcionales

Hay una oportunidad metodologica: definir un benchmark que mida no solo prediccion neural, sino tambien:

- prediccion de conducta;
- generalizacion a nuevas sesiones/animales;
- interpretabilidad regional;
- robustez a perturbaciones;
- calidad de contrafactuales;
- coste computacional.

Esto puede ser mas novedoso que otra arquitectura.

## 4. Lo que no es novedoso

No es novedoso:

- decir "digital twin brain";
- modelar corteza visual de raton con deep learning;
- usar datos Allen/MICrONS/IBL;
- construir un grafo regional;
- usar neural mass models;
- usar SNNs por plausibilidad biologica;
- hablar de conciencia sin protocolo experimental.

Si el paper se queda en cualquiera de esos puntos, sera debil.

## 5. Es plausible?

### Plausible

Es plausible construir:

- un modelo regional funcional;
- un pipeline de datos Allen/IBL;
- prediccion de variables conductuales y actividad agregada por region;
- lesiones virtuales;
- comparacion contra baselines;
- visualizaciones interpretables;
- un prototipo reproducible en Python.

### Dificil pero posible

Es dificil pero posible:

- calibrar parametros por animal/sesion;
- inferir actividad no observada en regiones no registradas;
- validar contrafactuales de lesion;
- combinar actividad neural, conducta y conectividad en un unico modelo generativo.

### No plausible en este proyecto

No es plausible:

- simular todo el cerebro a escala celular;
- representar todos los tipos neuronales relevantes;
- obtener un modelo consciente;
- validar experiencia subjetiva;
- superar modelos fundacionales en prediccion visual pura sin recursos masivos;
- hacer un gemelo individual completo del cerebro de raton.

## 6. Sirve para algo?

Si se ejecuta bien, sirve para tres cosas:

1. Ciencia computacional:
   - probar hipotesis sobre distribucion regional de decision, accion y engagement.

2. NeuroAI:
   - estudiar si restricciones neuroanatomicas mejoran generalizacion, interpretabilidad y contrafactuales.

3. Herramienta experimental:
   - priorizar regiones/conexiones para perturbaciones futuras.

No sirve, al menos inicialmente, para:

- crear AGI;
- demostrar conciencia;
- reemplazar experimentos in vivo;
- modelar clinicamente cerebros individuales.

## 7. Innovacion defendible

La innovacion defendible debe formularse asi:

> Un marco de gemelo funcional regional, calibrado con datos abiertos brain-wide, que integra prediccion neural, prediccion conductual y perturbacion contrafactual en tareas de decision visual de raton.

La innovacion no es el modelo aislado. Es la combinacion de:

- arquitectura regional biologicamente restringida;
- objetivo dual neural + conductual;
- evaluacion contrafactual;
- ablations regionales;
- generalizacion entre animales/sesiones;
- comparacion contra modelos no modulares.

## 8. Riesgos cientificos

### Riesgo 1: que la modularidad sea decorativa

Si una RNN o Transformer pequeno predice igual o mejor y nuestras regiones no aportan nada, el proyecto pierde fuerza.

Mitigacion:

- ablations estrictas;
- comparar contra modelos no modulares de mismo numero de parametros;
- medir generalizacion fuera de distribucion y contrafactuales, no solo accuracy.

### Riesgo 2: validacion de lesiones debil

Las lesiones virtuales pueden ser retoricas si no se comparan con predicciones empiricas o literatura.

Mitigacion:

- definir antes de entrenar que deficit esperamos para cada lesion;
- registrar hipotesis;
- usar datasets con manipulaciones si estan disponibles.

### Riesgo 3: exceso de ambicion biologica

Mas detalle no implica mejor ciencia. Puede introducir parametros libres imposibles de estimar.

Mitigacion:

- avanzar por niveles;
- cada nivel debe mejorar alguna metrica;
- no anadir tipos celulares si no hay validacion asociada.

### Riesgo 4: confusion con conciencia

Si usamos el lenguaje de conciencia de forma fuerte, el proyecto se vuelve especulativo.

Mitigacion:

- hablar de acceso global, no de conciencia;
- usar GNWT/IIT solo como marcos de variables medibles;
- no hacer afirmaciones ontologicas.

## 9. Modularizacion del proyecto

### Modulo A: revision SOTA y matriz critica

Objetivo:

- establecer que existe, que falta y que afirmaciones son defendibles.

Entregables:

- matriz de 40-60 papers;
- clasificacion por datos, metodo, validacion, limitaciones y codigo;
- lista de claims prohibidos y claims defendibles.

Criterio de exito:

- identificar un hueco concreto no cubierto por Nature 2025 visual cortex digital twins, The Virtual Brain, IBL y modelos genericos.

### Modulo B: datos y reproduccion

Objetivo:

- cargar datasets reales y reproducir un baseline simple.

Datasets prioritarios:

- Allen Visual Behavior Neuropixels;
- IBL decision-making;
- Allen Visual Coding Neuropixels;
- MICrONS solo si entramos en corteza visual fina.

Entregables:

- pipeline de descarga/carga;
- normalizacion de spikes, conducta y regiones;
- baseline de prediccion conductual;
- baseline de prediccion neural agregada por region.

Criterio de exito:

- reproducir metricas razonables en una tarea publica sin arquitectura nueva.

### Modulo C: modelo regional Nivel 0

Objetivo:

- construir un modelo dinamico regional, no spiking, falsable y barato.

Componentes:

- nodos regionales;
- conectividad dirigida;
- dinamica de estado latente;
- entradas visuales;
- salida de decision/accion;
- variables de arousal/engagement.

Baselines:

- GLM;
- RNN;
- GRU/LSTM;
- Transformer temporal pequeno;
- modelo regional sin conectividad biologica.

Criterio de exito:

- el modelo regional mejora generalizacion, interpretabilidad o contrafactuales frente a baselines comparables.

### Modulo D: contrafactuales y lesiones

Objetivo:

- convertir el modelo en una herramienta causal aproximada.

Experimentos:

- lesion de regiones;
- lesion de conexiones;
- perturbacion de ganancia;
- perturbacion de estado de engagement;
- cambio de regla/reversal si el dataset lo permite.

Criterio de exito:

- deficits coherentes, pre-registrados y medibles.

### Modulo E: escalado biologico Nivel 1

Objetivo:

- introducir poblaciones excitatorias/inhibitorias solo donde aporte.

Componentes:

- poblaciones E/I por region;
- dinamica rate-spiking o spiking ligera;
- balance E/I;
- retardos y ganancia.

Criterio de entrada:

- Nivel 0 debe haber demostrado valor.

Criterio de exito:

- mejora en prediccion de actividad, estabilidad dinamica o interpretabilidad fisiologica.

### Modulo F: microcircuitos Nivel 2

Objetivo:

- detallar 1-2 circuitos, no todo el cerebro.

Prioridad:

- talamo-corteza visual;
- ganglios basales para accion;
- hipocampo solo si la tarea exige contexto/memoria.

Criterio de exito:

- el detalle local explica un resultado que el modelo regional no podia explicar.

### Modulo G: publicacion

Objetivo:

- preparar paper con claims sobrios.

Estructura posible:

- problema: los digital twins cerebrales suelen ser predictivos o clinicos, pero no integran bien prediccion neural, conducta y contrafactuales regionales en tareas brain-wide;
- metodo: regional causal digital twin;
- datos: Allen/IBL;
- resultados: prediccion, generalizacion, lesiones, ablations;
- discusion: utilidad y limites.

Venue realista:

- Nature Computational Science: ambicioso, exigiria resultados muy fuertes.
- PLOS Computational Biology: mas realista si la contribucion es neurocomputacional solida.
- Nature Communications: posible solo con validacion fuerte y mensaje amplio.
- NeurIPS/ICLR: posible si la contribucion metodologica ML es clara; menos probable si domina neurociencia descriptiva.
- Journal of Neural Engineering / Network Neuroscience / eLife: opciones segun resultados.

## 10. Plan de trabajo recomendado

### Fase 0: cierre de alcance

Duracion: 1 semana.

Decisiones:

- dataset inicial;
- tarea inicial;
- regiones incluidas;
- metricas primarias;
- baselines obligatorios.

Resultado:

- protocolo tecnico de 3-5 paginas.

### Fase 1: datos y baselines

Duracion: 2-4 semanas.

Trabajo:

- cargar dataset;
- extraer eventos, spikes, regiones y conducta;
- entrenar baselines simples;
- comprobar si hay senal suficiente.

Decision go/no-go:

- si los baselines no aprenden nada estable, cambiar dataset o tarea.

### Fase 2: modelo regional Nivel 0

Duracion: 4-6 semanas.

Trabajo:

- implementar modelo regional;
- entrenar objetivo neural + conductual;
- comparar contra baselines;
- analizar variables latentes.

Decision go/no-go:

- si la modularidad no aporta nada, no escalar.

### Fase 3: contrafactuales

Duracion: 3-5 semanas.

Trabajo:

- lesiones virtuales;
- perturbaciones de conexiones;
- analisis de sensibilidad;
- comparacion con literatura.

Decision go/no-go:

- si los contrafactuales son arbitrarios o no interpretables, reformular.

### Fase 4: detalle biologico selectivo

Duracion: 6-10 semanas.

Trabajo:

- introducir E/I o microcircuito en el componente que mas limite el modelo;
- repetir ablations;
- comprobar mejora real.

Decision:

- solo mantener detalle biologico si mejora una metrica o explica un fenomeno.

### Fase 5: paper

Duracion: 4-8 semanas.

Trabajo:

- consolidar resultados;
- reproducibilidad;
- figuras;
- ablations;
- limitaciones;
- redaccion.

## 11. Criterios de abandono

Abandonar o pivotar si:

- no encontramos dataset adecuado para validar;
- los baselines genericos superan al modelo regional en todo;
- las lesiones virtuales no producen deficits interpretables;
- el modelo requiere demasiado ajuste manual;
- el resultado depende de claims de conciencia;
- el proyecto se convierte en una simulacion visual sin hipotesis falsable.

## 12. Proxima decision

La decision tecnica inmediata es elegir el primer dataset.

Recomendacion:

1. Empezar con IBL si priorizamos decision-making brain-wide.
2. Empezar con Allen Visual Behavior Neuropixels si priorizamos visual behavior con pipeline mas alineado con AllenSDK.
3. Usar MICrONS solo si el proyecto se estrecha a corteza visual y conectomica funcional.

Mi recomendacion actual: empezar con Allen Visual Behavior Neuropixels para prototipo inicial, y usar IBL como validacion secundaria si el enfoque funciona.

