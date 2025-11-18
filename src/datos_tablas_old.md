# Estructura de la base de datos

## Tablas

### Tabla `informacion_general`

| Columna         | Tipo de valor    |
| --------------- | ---------------- |
| id              | INTEGER          |
| nombre          | TEXT NOT NULL    |
| puestos         | INTEGER          |
| telefono        | TEXT NOT NULL    |
| estado          | BOOLEAN NOT NULL |
| capital         | INTEGER          |
| aporte_a_multas | INTEGER          |
| multas_extra    | INTEGER          |

### Tabla `cuotas`

| Columna    | Tipo de valor |
| ---------- | ------------- |
| id         | INTEGER       |
| pagas      | INTEGER       |
| adeudas    | INTEGER       |
| multas     | TEXT NOT NULL |
| revisiones | INTEGER       |

### Tabla `rifas`

| Columna    | Tipo de valor |
| ---------- | ------------- |
| id         | INTEGER       |
| r1_boletas | TEXT NOT NULL |
| r1_deudas  | INTEGER       |
| r2_boletas | TEXT NOT NULL |
| r2_deudas  | INTEGER       |
| r3_boletas | TEXT NOT NULL |
| r3_deudas  | INTEGER       |
| r4_boletas | TEXT NOT NULL |
| r4_deudas  | INTEGER       |

### Tabla `prestamos`

| Columna              | Tipo de valor |
| -------------------- | ------------- |
| id                   | INTEGER       |
| prestamos_hechos     | INTEGER       |
| dinero_en_prestamos  | INTEGER       |
| dinero_por_si_mismo  | INTEGER       |
| dinero_por_intereses | INTEGER       |
| deudas_por_fiador    | INTEGER       |
| fiador_de            | TEXT NOT NULL |

### Tabla `prestamos_hechos`

| Columna             | Tipo de valor                     |
| ------------------- | --------------------------------- |
| codigo              | INTEGER PRIMARY KEY AUTOINCREMENT |
| id                  | INTEGER                           |
| estado              | BOOLEAN NOT NULL                  |
| interes             | INTEGER                           |
| intereses_vencidos  | INTEGER                           |
| revisiones          | INTEGER                           |
| deuda               | INTEGER                           |
| fiadores            | TEXT NOT NULL                     |
| deuda_con_fiadores  | TEXT NOT NULL                     |
| fechas_de_pago      | TEXT NOT NULL                     |
| cargar_intereses    | BOOLEAN NOT NULL                  |

### Tabla `datos_de_rifas`

| Columna                  | Tipo de valor    |
| ------------------------ | ---------------- |
| id                       | INTEGER          |
| estado                   | BOOLEAN NOT NULL |
| numero_de_boletas        | INTEGER          |
| numeros_por_boleta       | INTEGER          |
| premios                  | TEXT NOT NULL    |
| costo_de_boleta          | INTEGER          |
| boletas_por_talonario    | INTEGER          |
| costos_de_administracion | INTEGER          |
| ganancia_por_boleta      | INTEGER          |
| fecha_de_cierre          | TEXT NOT NULL    |

### Tabla `ajustes`

| Columna | Tipo de valor |
| ------- | ------------- |
| ajuste  | TEXT NOT NULL |
| valor_n | INTEGER       |
| valor_a | TEXT NOT NULL |

### Tabla `registros`

| Columna | Tipo de valor |
| ------- | ------------- |
| fecha   | TEXT NOT NULL |
| ingreso | INTEGER       |
| egreso  | INTEGER       |

### Tabla `anotaciones`

| Columna   | Tipo de valor |
| --------- | ------------- |
| id        | INTEGER       |
| general   | TEXT NOT NULL |
| monetaria | TEXT NOT NULL |
| multa     | TEXT NOT NULL |
| acuerdo   | TEXT NOT NULL |

### Tabla `transferencias`

| Columna | Tipo de valor |
| ------- | ------------- |
| id      | INTEGER       |
| fecha   | TEXT NOT NULL |
| monto   | INTEGER       |
