# Listado de comandos

## Modificar datos

```sql
UPDATE <nombre_tabla>
SET <columna> = <valor>, <columna> = <valor>
WHERE <condicion>
```

> El `WHERE` sirve para filtrar todas las filas que se deseen afectar, de no hacerlo todas se veran afectadas


## Insertar datos

```sql
INSERT INTO <tabla> (
    <columna1>, <columna2>, <columna3>, ...
)
VALUES (<valor1>, <valor2>, <valor3>, ...)
```

## Desactivar todos los usuarios

```sql
UPDATE informacion_general
SET estado = **1**
```
