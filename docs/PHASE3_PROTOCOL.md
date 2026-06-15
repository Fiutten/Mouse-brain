# Protocolo de Fase 3: valor predictivo de conectividad anatómica

## Pregunta

¿La conectividad mesoscópica regional derivada del Allen Mouse Brain
Connectivity Atlas mejora la predicción fuera de muestra del target funcional
temporal confirmado frente a topologías nulas emparejadas?

## Conectividad anatómica

Se usan experimentos de trazado del producto Allen `5` cuya estructura primaria
de inyección coincide exactamente con una de seis áreas visuales. Para cada par
dirigido se agrega la mediana de `normalized_projection_volume` bilateral.

La diagonal se fija a cero porque la señal local puede estar dominada por el
sitio de inyección. La matriz se normaliza por radio espectral antes de simular.
No se interpreta como conectoma sináptico ni conectividad efectiva.

## Separación de datos

- Desarrollo: las 21 sesiones usadas en Fase 2c.
- Confirmación: las 20 sesiones nuevas selladas en Fase 2c.
- El vector de entrada exógena se estima únicamente en desarrollo.
- La confirmación se ejecuta una sola vez tras sellar el modelo.

## Modelos y controles

Se comparan `LinearRateModel` y `WilsonCowanModel`. La familia y parámetros del
modelo Allen se eligen por correlación mediana en desarrollo.

Después de seleccionar la familia, cada control calibra sus propios parámetros
dentro de la misma rejilla:

1. grafo desconectado;
2. orientación transpuesta;
3. cien permutaciones de pesos fuera de diagonal, conservando exactamente la
   densidad y distribución de pesos.

Permitir recalibración a los controles hace la prueba conservadora. La ventaja
no puede atribuirse simplemente a parámetros elegidos para Allen.

## Target y puntuación

Se predice `temporal_derivative`, confirmado en Fase 2c. La entrada exógena es
el primer bin postevento medio de desarrollo. Ese bin y el periodo preevento se
excluyen de la puntuación; el modelo debe predecir la evolución posterior.

La puntuación por sesión es la correlación entre la matriz temporal-regional
predicha y observada dentro de la ventana evaluada.

## Puerta confirmatoria

La conectividad Allen pasa solo si cumple simultáneamente:

- correlación mediana confirmatoria `> 0.30`;
- ventaja sobre la mediana de permutaciones `> 0.05`;
- supera al menos el 95% de permutaciones;
- límite inferior bootstrap agrupado de la ventaja pareada `> 0`;
- ventaja sobre el grafo desconectado `> 0.05`.

Si falla, se rechaza que esta conectividad regional y estas dinámicas aporten
valor predictivo suficiente para el target. No se añadirá complejidad para
rescatar retrospectivamente la prueba.
