# Proyecto fondo san javier

> Link al repositorio [padre](https://github.com/javier25987/fondo_new_version)

## Anotaciones

> En el fondo hay una gerarquia de simbolos para separar los elementos de un string la gerarquia es la siguiente `_ >> # >> ?`

> El simbolo `/` se reserva unicamente para las fechas y para nada mas

> En el apartado de prestamos el orden de la informacion es el siguiente `interes_"intereses vencidos"_revisiones_deuda_fiadores_"deuda con fiadores"`

## Deuda tecnica

* algoritmo para identificar boletas repetidas (seccion de rifas)

## Secciones finalizadas

* [X]  arranque
* [X]  menu
* [X]  cuotas
* [ ]  prestamos
* [X]  rifas
* [X]  registros
* [X]  transferencias
* [X]  ver socios
* [ ]  Anotaciones
* [X]  ajustes (temporal)
* [ ]  modificar socios
* [ ]  analizar usuarios

## Errores de el programa

actualmenre solo hay que añadir un boton de actualizacion que copie todos los hechos en el repositorio padre esto no se considera como un error ya que es solo una funcion que puede ser descartada por el problema de que git no resuelve los conflictos de un merge automaticamente

## Codigo que elimine y podria servir en un futuro

vacio

## Datos a tener en cuenta para mostara en la tabla

* cuanto ha pagado
* cuotas que tiene pagas
* cunto ha pagado en multas
* multas adeudas
* prestamos activos
* dinero pagado en intereses
* deuda de prestamos activos

## Agradecimiento

Este proyecto fue hecho para mi padre y mi madre a los cuales les agradezo todo lo que me han dado y la educacion que me estan pagando ya que gracias a eso obtuve los conocimientos para realizar este proyecto,

GRACIAS PAPA Y MAMA

```
def rectificar_cuotas(index: int) -> None:
    semanas_revisadas: int = msql.obtener_valor("cuotas", "revisiones", index)

    if semanas_revisadas >= 50:
        return

    calendario: list[datetime.datetime] = list(
        map(
            lambda x: datetime.datetime(*x),
            map(
                lambda y: map(int, y.split("/")),
                msql.obtener_ajuste("calendario", False).split("_"),
            ),
        )
    )
    fecha_actual = datetime.datetime.now()
    semanas_a_revisar: int = sum(map(lambda x: int(x < fecha_actual), calendario))


    if semanas_a_revisar > semanas_revisadas:
        multas: list[int] = descomprimir_to_array(
            msql.obtener_valor("cuotas", "multas", index)
        )

        cobrar_multas: bool = bool(msql.obtener_ajuste("cobrar multas"))

        pagas: int = msql.obtener_valor("cuotas", "pagas", index)
        deudas: int = 0

        bloqueos: set[int, ] = set(obtener_bloqueos(index))

        for i in range(50):
            if calendario[i] > fecha_actual:
                break

            if i in bloqueos:
                multas[i] += 1
                continue

            if pagas < 1:
                if cobrar_multas:
                    multas[i] += 1
                deudas += 1

            pagas -= 1
                
        msql.guardar_valor_n("cuotas", "adeudas", index, deudas)
        msql.guardar_valor_n("cuotas", "revisiones", index, semanas_a_revisar)

        msql.guardar_valor_t(
            "cuotas", 
            "multas", 
            index, 
            comprimir_of_array(multas)
        )
```

