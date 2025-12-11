CREATE TABLE deudas (
	codigo INTEGER PRIMARY KEY AUTOINCREMENT,
	idx INTEGER,
	monto INTEGER,
	fecha_de_creacion TEXT,
	fecha_de_pago TEXT,
	is_multa BOOLEAN,
	motivo TEXT,
	estado BOOLEAN
);
