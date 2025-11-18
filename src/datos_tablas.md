```sql
CREATE TABLE ajustes (
	ajuste TEXT,
	valor_n INTEGER,
	valor_t TEXT
);

CREATE TABLE anotaciones (
	idx INTEGER,
	anotacion TEXT,
	tipo TEXT,
	fecha TEXT
);

CREATE TABLE boletas_rifa_1 (
	idx INTEGER,
	boleta TEXT,
	dada_a INTEGER
);

CREATE TABLE boletas_rifa_2 (
	idx INTEGER,
	boleta TEXT,
	dada_a INTEGER
);

CREATE TABLE boletas_rifa_3 (
	idx INTEGER,
	boleta TEXT,
	dada_a INTEGER
);

CREATE TABLE boletas_rifa_4 (
	idx INTEGER,
	boleta TEXT,
	dada_a INTEGER
);

CREATE TABLE cuotas (
	id INTEGER,
	pagas INTEGER,
	adeudas INTEGER,
	multas TEXT,
	multas_pagas TEXT,
	revisiones INTEGER,
	bloqueos TEXT
);

CREATE TABLE datos_de_rifas (
	id INTEGER,
	numero_de_boletas INTEGER,
	premios TEXT,
	costo_de_boletas INTEGER,
	costos_de_administracion INTEGER,
	ganancias_por_boleta INTEGER
);

CREATE TABLE deudas_rifa (
	id INTEGER,
	deuda INTEGER
);

CREATE TABLE informacion_general (
	id INTEGER,
	nombre TEXT,
	puestos INTEGER,
	telefono TEXT,
	estado BOOLEAN
);

CREATE TABLE prestamos (
	id INTEGER,
	deudas_por_fiador INTEGER,
	fiador_de TEXT
);

CREATE TABLE prestamos_hechos (
	codigo INTEGER PRIMARY KEY AUTOINCREMENT,
	idx INTEGER,
	estado_de_pago BOOLEAN,
	interes INTEGER,
	interes_vencido INTEGER,
	interes_generado INTEGER,
	deuda INTEGER,
	monto INTEGER,
	fechas_de_pago TEXT,
	revisiones INTEGER,
	fiadores TEXT,
	deuda_con_fiadores TEXT,
	motivo TEXT
);

CREATE TABLE registros (
	fecha TEXT,
	ingreso INTEGER,
	egreso INTEGER
);

CREATE TABLE transferencias (
	idx INTEGER,
	fecha TEXT,
	monto INTEGER
);

CREATE TABLE multas (
	id INTEGER,
	semanales INTEGER,
	extras INTEGER
);

CREATE TABLE capital (
	id INTEGER,
	pago INTEGER,
	retirado INTEGER,
	proyectado INTEGER
);


```