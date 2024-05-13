from ElUniversal import ElUniversal
from EstructuraSQL import EstructuraSql
from Excelsior import Excelsior
from ElMilenio import ElMilenio
from datetime import datetime

EstructuraSql()

ElUniversal().obtenerNoticias()
Excelsior().obtenerNoticias()
ElMilenio().obtenerNoticias()
