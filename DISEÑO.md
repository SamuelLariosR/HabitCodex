# HabitCodex – Documento de diseño (v0.1)

## Qué es
Aplicación de escritorio en Python, con ventana, para estudiantes de software.
Ayuda a crear hábitos, marcarlos como cumplidos cada día y mantener una racha.

## Problema
No saber por dónde empezar y terminar distraído aunque uno se propuso programar.
HabitCodex hace visible si cumpliste o no lo que te propusiste.

## Alcance v0.1
Sí: crear hábitos, marcar los hábitos del día, escribir una nota de cómo te
sientes, ver la racha, ver un consejo.
No (por ahora): estadísticas, recordatorios, mediciones automáticas, usuarios
múltiples, versión web.

## Pantalla principal (ventana)
- Arriba: racha actual.
- Centro: lista de hábitos de hoy, cada uno con su casilla; botón "Agregar
  hábito"; cuadro para la nota de cómo te sientes hoy.
- Abajo: un consejo al azar de una lista fija de 5.

## Arquitectura (tres capas)
- Datos: base de datos SQLite. Guarda y lee; no decide nada.
- Lógica: crear hábitos, marcar cumplidos, calcular la racha. No sabe cómo se
  ve la pantalla.
- Interfaz: la ventana. Solo muestra información y le pide cosas a la lógica.
Regla: la interfaz nunca calcula nada (por ejemplo, la racha no se calcula
dentro de un botón).

## Datos (conceptual)
- Hábito: nombre, fecha de creación.
- Registro: qué hábito se cumplió y en qué fecha.
- Nota: fecha y texto de cómo te sientes.

## Reglas
- Un hábito se marca como cumplido una vez por día.
- Un día cuenta para la racha si se cumplió al menos un hábito.
- La racha se calcula con los registros; no se guarda como número.
- Hoy aún sin cumplir no rompe la racha; se pierde al terminar el día sin
  cumplir ninguno.

## Decisiones tomadas
- Lenguaje: Python 3.13, solo librería estándar.
- Interfaz: ventana con Tkinter (si se confirma que funciona en mi instalación).
- Almacenamiento: