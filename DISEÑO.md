# HabitCodex – Documento de diseño (v0.1)

## Qué es
Programa de terminal en Python para estudiantes de software que ayuda a crear
hábitos, marcarlos como cumplidos cada día y mantener una racha.

## Problema
No saber por dónde empezar y terminar distraído aunque uno se propuso programar.
HabitCodex hace visible si cumpliste o no lo que te propusiste.

## Alcance v0.1
Sí: crear hábitos, marcar hábitos del día, escribir una nota de cómo te sientes,
ver la racha, ver un consejo.
No (por ahora): estadísticas, recordatorios, mediciones automáticas, interfaz
gráfica, usuarios múltiples.

## Pantalla principal
- Arriba: racha actual.
- Centro: menú (marcar hábitos de hoy, crear hábito, escribir nota, salir).
- Abajo: un consejo al azar de una lista fija de 5.

## Datos (conceptual)
- Hábito: nombre, fecha de creación.
- Registro: qué hábito se cumplió y en qué fecha.
- Nota: fecha y texto de cómo te sientes.

## Reglas
- Un hábito se marca como cumplido una vez por día.
- Un día cuenta para la racha si se cumplió al menos un hábito.
- La racha se calcula con los registros; no se guarda como número.
- Hoy aún sin cumplir no rompe la racha; se pierde al terminar el día sin cumplir ninguno.

## Decisiones tomadas
- Lenguaje: Python 3.13, solo librería estándar.
- Almacenamiento: SQLite, archivo en ~/.local/share/habitcodex/.
- Interfaz: menú en terminal.

## Pendientes
- Nota de cómo te sientes: ¿una por día o una por hábito?
- Escribir los 5 consejos.