#import "var_estado_usr.typ" as var

#set page(margin: 2cm)

// tabla de multas
#let semana = range(1, 51)
#let estado = range(50).map(_ => "")
#let multas_vigentes = range(50).map(_ => "")
#let multas_pagas = range(50).map(_ => "")
#{
  for i in var.bloqueos {
    estado.at(i) = "|"
  }

  let semanas_pagas = var.cuotas_pagas
  let semanas_deudas = var.cuotas_deudas

  let count = 0
  while semanas_pagas > 0 {
    if estado.at(count) == "" {
      estado.at(count) = "$"
      semanas_pagas -= 1
    }
    count += 1
  }

  while semanas_deudas > 0 {
    if estado.at(count) == "" {
      estado.at(count) = "X"
      semanas_deudas -= 1
    }
    count += 1
  }

  for i in var.multas {
    multas_vigentes.at(i.at(0)) = i.at(1)
  }

  for i in var.multas_pagas {
    multas_pagas.at(i.at(0)) = i.at(1)
  }
}

#align(center)[
  #v(5pt)
  #text(size:30pt)[*№ #var.id - #var.nombre*]\
  #datetime.today().display()
]

#align(center)[
  = Estado actual del pago semanal
  paga:`$`, deuda:`X`, bloqueada:`|`
]

#grid(
  columns: (50%, 50%)
)[
  #table(
    columns: 4,
    stroke: none,
    align: center,
    table.header(
      [*semana*], //table.vline(), 
      [*estado*], //table.vline(), 
      [*multas*],
      [*multas pagas*]
    ),
    table.hline(),
    ..semana.slice(0, 25)
    .zip(
      estado.slice(0, 25), 
      multas_vigentes.slice(0, 25),
      multas_pagas.slice(0, 25)
    ).map(
      d => (
        [#d.at(0)],
        [#d.at(1)],
        [#d.at(2)],
        [#d.at(3)],
        table.hline(stroke: gray + .5pt)
      )
    ).flatten(),
  )
][
  #table(
    columns: 4,
    stroke: none,
    align: center,
    table.header(
      [*semana*], //table.vline(), 
      [*estado*], //table.vline(), 
      [*multas*],
      [*multas pagas*]
    ),
    table.hline(),
    ..semana.slice(25, 50)
    .zip(
      estado.slice(25, 50), 
      multas_vigentes.slice(25, 50),
      multas_pagas.slice(25, 50)
    ).map(
      d => (
        [#d.at(0)],
        [#d.at(1)],
        [#d.at(2)],
        [#d.at(3)],
        table.hline(stroke: gray + .5pt)
      )
    ).flatten(),
  )
]

Este grafico muestra todas las fechas pagas, las multas pagas y las multas pagadas hasta la fecha estipulada al inicio del documento

#align(center)[
  = Informacion del usuario
]

#grid(
  columns: (50%, 50%),
)[
  == Informacion General
  - / Puestos: #var.puestos
  - / Telefono: #var.telefono
  - / Estado: #var.estado
  == Pagos Semanales
  - / Total Pagado: #var.capital_pago
  - / Total En Multas: #var.multas_semanales
]
