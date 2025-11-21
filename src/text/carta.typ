#set text(lang: "es", size: 14pt)//, font: "PT Sans")
#set par(justify: true)

#align(center)[= `Solicitud De Prestamo`]
\

#h(1fr) `________`/`_____`/`_____`\
\

Señores de el fondo, yo `___________________________` usuari@ № `_______` del fondo San Javier identificado con cedula de ciudadanía № `_________________` solicito un préstamo por el valor de `_________________ `, con el interés de `_____ ` %, tengo la intención de pagar el préstamo en `_______` mes(es), si mi dinero no llegase a ser suficiente solicito como fiador(es) a (...), con sus respectivas deudas especificadas a continuación:

\

#table(
  columns: (10%, 15%, 45%, 20%),
  align: (center, center, center, left),
  stroke: none,
  gutter: 1em,
  table.header([`№`], table.vline(), [*`Puesto`*], [*`Nombre`*], [*`Deuda`*]),
  table.hline(),
  [1],[],[],[],
  [2],[],[],[],
  [3],[],[],[],
  [4],[],[],[],
  [5],[],[],[],
)


#v(6cm)

#grid(
  columns: (50%, 50%), 
  align: (center, center)
)[
  `_________________________`\ 
  usuario del fondo
][
  `_________________________`\ 
  tesorero
]
