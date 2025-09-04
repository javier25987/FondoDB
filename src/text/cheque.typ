#import "var_cheque.typ" as var

#set page(width: 8cm, height: 16cm)
#set text(size: 13pt)

#align(center)[
  = `Fondo San Javier`
  `cheque de pago`
]

/ `Nombre:`: #h(1fr) #var.nombre
/ `Numero:`: #h(1fr) #var.numero
/ `Puestos:`: #h(1fr) #var.puestos
#line()
/ `Multas Pagas:`: #h(1fr) #var.multas_pagadas
/ `Valor De Una Multa:`: #h(1fr) #var.valor_multa
/ `Total Por Multas:`: #h(1fr) #var.total_multas
#line()
/ `Cuotas Pagas:`: #h(1fr) #var.cuotas_pagadas
/ `Valor De Una Cuota:`: #h(1fr) #var.valor_cuota
/ `Total Por Cuotas:`: #h(1fr) #var.total_cuotas
#line()
/ `Metodo De Pago:`: #h(1fr) #var.Metodo_de_pago
/ `TOTAL PAGADO:`: #h(1fr) #var.total_pagado
#line()
/ `Fecha:`: #h(1fr) #var.fecha
/ `Hora:`: #h(1fr) #var.hora
