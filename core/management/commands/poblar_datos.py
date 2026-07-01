# Comando para poblar la base de datos con los datos históricos de Cine Chatarra
# Ejecutar: python manage.py poblar_datos
from django.core.management.base import BaseCommand
from core.models import Ciclo, Funcion, Locacion, EventoEspecial
from datetime import date


class Command(BaseCommand):
    help = 'Pobla la base de datos con los datos históricos de Cine Chatarra'

    def add_arguments(self, parser):
        parser.add_argument('--if-empty', action='store_true', help='Solo poblar si la base de datos está vacía')

    def handle(self, *args, **options):
        if options.get('if_empty') and Ciclo.objects.exists():
            self.stdout.write(self.style.SUCCESS('Base de datos ya tiene datos — saltando población.'))
            return
        self.stdout.write('Poblando base de datos de Cine Chatarra...')

        # ─── Crear locaciones ───
        self.stdout.write('  Creando locaciones...')
        locaciones_data = [
            {'nombre': 'Casa particular', 'direccion': 'Isabel Riquelme #250, Villarrica',
             'periodo_inicio': 'Ago 2023', 'periodo_fin': 'Sep 2023', 'orden': 1},
            {'nombre': 'Skol Restobar / Espacio Patio', 'direccion': 'Av. Presidente Ríos 1180, Villarrica',
             'periodo_inicio': '2023', 'periodo_fin': 'Jun 2025', 'orden': 2},
            {'nombre': 'Sede vecinal (Cesfam Los Volcanes)', 'direccion': 'Pino Hachado #950, Villarrica',
             'periodo_inicio': 'Jul 2025', 'periodo_fin': 'Sep 2025', 'orden': 3},
            {'nombre': 'Sede Vecinal 21 de Mayo', 'direccion': 'Julio Zegers #1001, Villarrica',
             'periodo_inicio': 'Oct 2025', 'periodo_fin': 'presente', 'orden': 4},
            {'nombre': 'Txafkintuwe', 'direccion': 'Korner 933, Villarrica',
             'periodo_inicio': 'Nov 2025', 'periodo_fin': '', 'orden': 5},
            {'nombre': 'Itinerante (sedes vecinales)', 'direccion': 'Varias sedes, Villarrica',
             'periodo_inicio': 'Abr 2025', 'periodo_fin': '', 'orden': 6},
        ]
        for data in locaciones_data:
            Locacion.objects.get_or_create(nombre=data['nombre'], defaults=data)
        self.stdout.write(self.style.SUCCESS(f'    {len(locaciones_data)} locaciones creadas.'))

        # ─── Crear ciclos ───
        self.stdout.write('  Creando ciclos...')
        ciclos_data = [
            {'nombre': 'Pre-ciclo', 'slug': 'pre-ciclo', 'descripcion': 'Primeras proyecciones antes de los ciclos temáticos.',
             'fecha_inicio': date(2023, 8, 1), 'fecha_fin': date(2023, 10, 31), 'orden': 1},
            {'nombre': 'Febrero Extraterrestre', 'slug': 'febrero-extraterrestre',
             'descripcion': 'Ciclo de ciencia ficción y lo extraterrestre.',
             'fecha_inicio': date(2024, 2, 1), 'fecha_fin': date(2024, 2, 29), 'orden': 2},
            {'nombre': 'Terry Gilliam', 'slug': 'terry-gilliam',
             'descripcion': 'Ciclo dedicado al director Terry Gilliam.',
             'fecha_inicio': date(2024, 3, 1), 'fecha_fin': date(2024, 3, 31), 'orden': 3},
            {'nombre': 'El Futuro Será Peor', 'slug': 'el-futuro-sera-peor',
             'descripcion': 'Ciclo desesperanzado sobre futuros distópicos.',
             'fecha_inicio': date(2024, 4, 1), 'fecha_fin': date(2024, 4, 30), 'orden': 4},
            {'nombre': 'Gitano / Kusturica', 'slug': 'gitano-kusturica',
             'descripcion': 'Ciclo dedicado al cine gitano y Emir Kusturica.',
             'fecha_inicio': date(2024, 5, 1), 'fecha_fin': date(2024, 5, 31), 'orden': 5},
            {'nombre': 'En tiempos de guerra', 'slug': 'en-tiempos-de-guerra',
             'descripcion': 'Ciclo bélico sobre conflictos y violencia.',
             'fecha_inicio': date(2024, 6, 1), 'fecha_fin': date(2024, 6, 30), 'orden': 6},
            {'nombre': 'Julio del Terror', 'slug': 'julio-del-terror',
             'descripcion': 'Ciclo de terror con clásicos del género.',
             'fecha_inicio': date(2024, 7, 1), 'fecha_fin': date(2024, 7, 31), 'orden': 7},
            {'nombre': '1er Aniversario', 'slug': 'primer-aniversario',
             'descripcion': 'Ciclo "Cine dentro del cine" celebrando el primer año.',
             'fecha_inicio': date(2024, 8, 1), 'fecha_fin': date(2024, 8, 31), 'orden': 8},
            {'nombre': 'Varias (Oct 2024)', 'slug': 'varias-oct-2024',
             'descripcion': 'Proyecciones varias de octubre.',
             'fecha_inicio': date(2024, 10, 1), 'fecha_fin': date(2024, 10, 31), 'orden': 9},
            {'nombre': 'Nicolas Cage', 'slug': 'nicolas-cage',
             'descripcion': '¿Es Nicolás Cage un buen o mal actor? Cuatro películas para debatir.',
             'fecha_inicio': date(2024, 11, 1), 'fecha_fin': date(2024, 12, 6), 'orden': 10},
            {'nombre': 'Hermanos Coen', 'slug': 'hermanos-coen',
             'descripcion': 'Ciclo dedicado a los hermanos Joel y Ethan Coen.',
             'fecha_inicio': date(2024, 12, 1), 'fecha_fin': date(2024, 12, 31), 'orden': 11},
            {'nombre': 'Especiales (Ene 2025)', 'slug': 'especiales-ene-2025',
             'descripcion': 'Proyecciones especiales de enero.',
             'fecha_inicio': date(2025, 1, 1), 'fecha_fin': date(2025, 1, 31), 'orden': 12},
            {'nombre': 'Varias (Feb 2025)', 'slug': 'varias-feb-2025',
             'descripcion': 'Proyecciones varias de febrero con clásicos de culto.',
             'fecha_inicio': date(2025, 2, 1), 'fecha_fin': date(2025, 2, 28), 'orden': 13},
            {'nombre': 'Cine Comunitario', 'slug': 'cine-comunitario',
             'descripcion': 'Ciclo itinerante por sedes vecinales explorando la comunidad.',
             'fecha_inicio': date(2025, 4, 1), 'fecha_fin': date(2025, 4, 30), 'orden': 14},
            {'nombre': 'Aki Kaurismäki', 'slug': 'aki-kaurismaki',
             'descripcion': 'Proletario, desempleado y con el corazón roto — ciclo del director finlandés.',
             'fecha_inicio': date(2025, 5, 1), 'fecha_fin': date(2025, 5, 31), 'orden': 15},
            {'nombre': 'Perdiendo el Tiempo', 'slug': 'perdiendo-el-tiempo',
             'descripcion': 'Ciclo de paradojas temporales y viajes en el tiempo.',
             'fecha_inicio': date(2025, 6, 1), 'fecha_fin': date(2025, 6, 30), 'orden': 16},
            {'nombre': 'Satoshi Kon', 'slug': 'satoshi-kon',
             'descripcion': 'Ciclo dedicado al maestro de la animación japonesa Satoshi Kon.',
             'fecha_inicio': date(2025, 7, 1), 'fecha_fin': date(2025, 7, 31), 'orden': 17},
            {'nombre': 'Vejez (1) + CESFAM', 'slug': 'vejez-1-cesfam',
             'descripcion': 'Una caja de fotos desteñidas — ciclo para hablar de la vejez, en alianza con CESFAM Los Volcanes.',
             'fecha_inicio': date(2025, 8, 1), 'fecha_fin': date(2025, 8, 31), 'orden': 18},
            {'nombre': 'Adicciones', 'slug': 'adicciones',
             'descripcion': 'Ciclo sobre adicciones con conversatorio y cortometrajes chilenos.',
             'fecha_inicio': date(2025, 9, 1), 'fecha_fin': date(2025, 9, 30), 'orden': 19},
            {'nombre': 'Vejez (2)', 'slug': 'vejez-2',
             'descripcion': 'Segunda parte del ciclo para hablar de la tercera edad.',
             'fecha_inicio': date(2025, 10, 1), 'fecha_fin': date(2025, 10, 31), 'orden': 20},
            {'nombre': 'Depresión', 'slug': 'depresion',
             'descripcion': 'Mi eterna tarde gris y lluviosa — ciclo para hablar de la depresión.',
             'fecha_inicio': date(2025, 11, 1), 'fecha_fin': date(2025, 11, 30), 'orden': 21},
            {'nombre': 'El trabajo dignifica', 'slug': 'el-trabajo-dignifica',
             'descripcion': 'Miniciclo sobre las condiciones laborales y la explotación.',
             'fecha_inicio': date(2025, 11, 29), 'fecha_fin': date(2025, 12, 6), 'orden': 22},
            {'nombre': 'Miniciclo VIH', 'slug': 'miniciclo-vih',
             'descripcion': 'Miniciclo para hablar del VIH.',
             'fecha_inicio': date(2025, 12, 13), 'fecha_fin': date(2025, 12, 13), 'orden': 23},
            {'nombre': 'Lanzamiento Las Moscas', 'slug': 'lanzamiento-las-moscas',
             'descripcion': 'Lanzamiento del libro "Las Moscas" y cierre de temporada de verano.',
             'fecha_inicio': date(2026, 1, 1), 'fecha_fin': date(2026, 1, 31), 'orden': 24},
            {'nombre': 'Herramientas nuevo fin del mundo', 'slug': 'herramientas-nuevo-fin-del-mundo',
             'descripcion': 'Ciclo sobre revoluciones, resistencia y nuevos mundos posibles.',
             'fecha_inicio': date(2026, 3, 1), 'fecha_fin': date(2026, 4, 15), 'orden': 25},
            {'nombre': 'SATÍRICO', 'slug': 'satirico',
             'descripcion': 'Ciclo de comedia satírica y humor negro.',
             'fecha_inicio': date(2026, 4, 1), 'fecha_fin': date(2026, 4, 30), 'orden': 26},
            {'nombre': 'Cine iraní', 'slug': 'cine-irani',
             'descripcion': 'El país que vuelve a la edad de piedra — ciclo de cine iraní contemporáneo.',
             'fecha_inicio': date(2026, 5, 1), 'fecha_fin': date(2026, 5, 31), 'orden': 27},
            {'nombre': 'Revelando Territorios', 'slug': 'revelando-territorios',
             'descripcion': 'Ciclo con realizadores chilenos y conversatorios en vivo.',
             'fecha_inicio': date(2026, 6, 1), 'fecha_fin': date(2026, 6, 30), 'orden': 28},
        ]
        for data in ciclos_data:
            Ciclo.objects.get_or_create(slug=data['slug'], defaults=data)
        self.stdout.write(self.style.SUCCESS(f'    {len(ciclos_data)} ciclos creados.'))

        # ─── Crear funciones ───
        self.stdout.write('  Creando funciones...')

        funciones_data = [
            # Pre-ciclo
            {'titulo': 'TOKYO!', 'director': '—', 'año': '2008', 'pais': '—',
             'fecha_funcion': '09/08/2023', 'hora': '19:00', 'locacion': 'Isabel Riquelme #250', 'ciclo_slug': 'pre-ciclo', 'orden': 1},
            {'titulo': '(proyección)', 'director': '—', 'año': '', 'pais': '',
             'fecha_funcion': '16/08/2023', 'hora': '19:00', 'locacion': 'Isabel Riquelme #250', 'ciclo_slug': 'pre-ciclo', 'orden': 2},
            {'titulo': 'Cien niños esperando un tren', 'director': 'Ignacio Agüero', 'año': '1988', 'pais': 'Chile',
             'fecha_funcion': '~20/09/2023', 'tipo': 'Documental', 'ciclo_slug': 'pre-ciclo', 'orden': 3},
            {'titulo': 'La noche de los lápices', 'director': 'Héctor Olivera', 'año': '1986', 'pais': 'Argentina',
             'fecha_funcion': '20/09/2023', 'ciclo_slug': 'pre-ciclo', 'orden': 4},
            {'titulo': 'Naked Lunch', 'director': 'David Cronenberg', 'año': '1991', 'pais': 'Canadá',
             'fecha_funcion': '~17/10/2023', 'ciclo_slug': 'pre-ciclo', 'orden': 5},
            # El Futuro Será Peor
            {'titulo': 'Mad Max 2', 'director': 'George Miller', 'año': '1981', 'pais': 'Australia',
             'fecha_funcion': 'Abr 2024', 'ciclo_slug': 'el-futuro-sera-peor', 'orden': 1},
            {'titulo': 'Tank Girl', 'director': 'Rachel Talalay', 'año': '1995', 'pais': 'EE.UU.',
             'fecha_funcion': 'Abr 2024', 'ciclo_slug': 'el-futuro-sera-peor', 'orden': 2},
            {'titulo': 'Poor Things', 'director': 'Yorgos Lanthimos', 'año': '2023', 'pais': 'Irlanda/R.U.',
             'fecha_funcion': 'Abr 2024', 'ciclo_slug': 'el-futuro-sera-peor', 'orden': 3},
            {'titulo': 'Akira', 'director': 'Katsuhiro Otomo', 'año': '1988', 'pais': 'Japón',
             'fecha_funcion': 'Abr 2024', 'tipo': 'Animación', 'ciclo_slug': 'el-futuro-sera-peor', 'orden': 4},
            {'titulo': 'Metropolis', 'director': 'Fritz Lang', 'año': '1927', 'pais': 'Alemania',
             'fecha_funcion': 'Abr 2024', 'ciclo_slug': 'el-futuro-sera-peor', 'orden': 5},
            # Gitano
            {'titulo': 'Tiempo de gitanos', 'director': 'Emir Kusturica', 'año': '1988', 'pais': 'Yugoslavia',
             'fecha_funcion': '10/05/2024', 'ciclo_slug': 'gitano-kusturica', 'orden': 1},
            {'titulo': 'Gato negro, gato blanco', 'director': 'Emir Kusturica', 'año': '1998', 'pais': 'Yugoslavia',
             'fecha_funcion': 'May 2024', 'ciclo_slug': 'gitano-kusturica', 'orden': 2},
            {'titulo': 'Latcho Drom', 'director': 'Tony Gatlif', 'año': '1993', 'pais': 'Francia',
             'fecha_funcion': 'May 2024', 'ciclo_slug': 'gitano-kusturica', 'orden': 3},
            {'titulo': 'Yo, el Vaquilla', 'director': 'José Antonio de la Loma', 'año': '1985', 'pais': 'España',
             'fecha_funcion': 'May 2024', 'ciclo_slug': 'gitano-kusturica', 'orden': 4},
            {'titulo': 'Underground', 'director': 'Emir Kusturica', 'año': '1995', 'pais': 'Yugoslavia',
             'fecha_funcion': 'May 2024', 'ciclo_slug': 'gitano-kusturica', 'orden': 5},
            # Guerra
            {'titulo': 'Starship Troopers', 'director': 'Paul Verhoeven', 'año': '1997', 'pais': 'EE.UU.',
             'fecha_funcion': 'Jun 2024', 'locacion': 'Espacio Patio', 'ciclo_slug': 'en-tiempos-de-guerra', 'orden': 1},
            {'titulo': 'En tierra de nadie', 'director': 'Danis Tanović', 'año': '2001', 'pais': 'Bosnia',
             'fecha_funcion': 'Jun 2024', 'locacion': 'Espacio Patio', 'ciclo_slug': 'en-tiempos-de-guerra', 'orden': 2},
            {'titulo': "Jacob's Ladder", 'director': 'Adrian Lyne', 'año': '1990', 'pais': 'EE.UU.',
             'fecha_funcion': 'Jun 2024', 'locacion': 'Espacio Patio', 'ciclo_slug': 'en-tiempos-de-guerra', 'orden': 3},
            # Terror
            {'titulo': 'El Exorcista', 'director': 'William Friedkin', 'año': '1973', 'pais': 'EE.UU.',
             'fecha_funcion': 'Jul 2024', 'ciclo_slug': 'julio-del-terror', 'orden': 1},
            {'titulo': 'Anticristo', 'director': 'Lars von Trier', 'año': '2009', 'pais': 'Dinamarca',
             'fecha_funcion': 'Jul 2024', 'ciclo_slug': 'julio-del-terror', 'orden': 2},
            # 1er Aniversario
            {'titulo': 'Camera Buff (Amator)', 'director': 'Krzysztof Kieślowski', 'año': '1979', 'pais': 'Polonia',
             'fecha_funcion': 'Ago 2024', 'ciclo_slug': 'primer-aniversario', 'orden': 1},
            {'titulo': 'Be Kind Rewind', 'director': 'Michel Gondry', 'año': '2008', 'pais': 'EE.UU.',
             'fecha_funcion': 'Ago 2024', 'ciclo_slug': 'primer-aniversario', 'orden': 2},
            {'titulo': 'Lost in La Mancha', 'director': 'Keith Fulton / Louis Pepe', 'año': '2002', 'pais': 'EE.UU.',
             'fecha_funcion': 'Ago 2024', 'tipo': 'Documental', 'ciclo_slug': 'primer-aniversario', 'orden': 3},
            # Varias Oct 2024
            {'titulo': 'Fritz the Cat', 'director': 'Ralph Bakshi', 'año': '1972', 'pais': 'EE.UU.',
             'fecha_funcion': 'Oct 2024', 'tipo': 'Animación', 'ciclo_slug': 'varias-oct-2024', 'orden': 1},
            {'titulo': 'Técnico Servicio', 'director': 'Juan Pablo Aguirre Ramírez', 'año': '2024', 'pais': 'Chile',
             'fecha_funcion': 'Oct 2024', 'ciclo_slug': 'varias-oct-2024', 'orden': 2},
            {'titulo': 'Los perros de la plaga', 'director': 'Martin Rosen', 'año': '1982', 'pais': 'R.U.',
             'fecha_funcion': 'Oct 2024', 'tipo': 'Animación', 'ciclo_slug': 'varias-oct-2024', 'orden': 3},
            # Nicolas Cage
            {'titulo': 'El beso del vampiro', 'director': 'Robert Bierman', 'año': '1989', 'pais': 'EE.UU.',
             'fecha_funcion': 'Nov 2024', 'ciclo_slug': 'nicolas-cage', 'orden': 1},
            {'titulo': 'Corazón salvaje', 'director': 'David Lynch', 'año': '1990', 'pais': 'EE.UU.',
             'fecha_funcion': 'Nov 2024', 'ciclo_slug': 'nicolas-cage', 'orden': 2},
            {'titulo': 'Mandy', 'director': 'Panos Cosmatos', 'año': '2018', 'pais': 'EE.UU.',
             'fecha_funcion': 'Nov 2024', 'ciclo_slug': 'nicolas-cage', 'orden': 3},
            {'titulo': 'Color Out of Space', 'director': 'Richard Stanley', 'año': '2019', 'pais': 'EE.UU.',
             'fecha_funcion': '06/12/2024', 'ciclo_slug': 'nicolas-cage', 'orden': 4},
            # Coen
            {'titulo': 'Raising Arizona', 'director': 'Joel Coen', 'año': '1987', 'pais': 'EE.UU.',
             'fecha_funcion': '06/12/2024', 'ciclo_slug': 'hermanos-coen', 'orden': 1},
            {'titulo': 'Fargo', 'director': 'Joel Coen', 'año': '1996', 'pais': 'EE.UU.',
             'fecha_funcion': 'Dic 2024', 'ciclo_slug': 'hermanos-coen', 'orden': 2},
            {'titulo': 'El hombre que nunca estuvo allí', 'director': 'Joel Coen', 'año': '2001', 'pais': 'EE.UU.',
             'fecha_funcion': 'Dic 2024', 'ciclo_slug': 'hermanos-coen', 'orden': 3},
            {'titulo': 'Quemese después de leer', 'director': 'Joel Coen', 'año': '2008', 'pais': 'EE.UU.',
             'fecha_funcion': 'Dic 2024', 'ciclo_slug': 'hermanos-coen', 'orden': 4},
            # Especiales Ene 2025
            {'titulo': 'Pink Flamingos', 'director': 'John Waters', 'año': '1972', 'pais': 'EE.UU.',
             'fecha_funcion': 'Ene 2025', 'ciclo_slug': 'especiales-ene-2025', 'orden': 1},
            {'titulo': 'La virgen de los sicarios', 'director': 'Barbet Schroeder', 'año': '2000', 'pais': 'Colombia',
             'fecha_funcion': 'Ene 2025', 'ciclo_slug': 'especiales-ene-2025', 'orden': 2},
            {'titulo': 'High Art', 'director': 'Lisa Cholodenko', 'año': '1998', 'pais': 'EE.UU.',
             'fecha_funcion': 'Ene 2025', 'ciclo_slug': 'especiales-ene-2025', 'orden': 3},
            {'titulo': 'El beso de la mujer araña', 'director': 'Héctor Babenco', 'año': '1985', 'pais': 'Argentina',
             'fecha_funcion': 'Ene 2025', 'ciclo_slug': 'especiales-ene-2025', 'orden': 4},
            # Feb 2025
            {'titulo': 'The Rocky Horror Picture Show', 'director': 'Jim Sharman', 'año': '1975', 'pais': 'EE.UU.',
             'fecha_funcion': 'Feb 2025', 'ciclo_slug': 'varias-feb-2025', 'orden': 1},
            {'titulo': 'Sound of Noise', 'director': 'Ola Simonsson / Johannes Stjärne Nilsson', 'año': '2010', 'pais': 'Suecia',
             'fecha_funcion': 'Feb 2025', 'ciclo_slug': 'varias-feb-2025', 'orden': 2},
            {'titulo': 'Hijas de las cenizas', 'director': 'Ismael Leiva', 'año': '', 'pais': 'Chile',
             'fecha_funcion': '14/02/2025', 'ciclo_slug': 'varias-feb-2025', 'orden': 3},
            # Cine Comunitario
            {'titulo': 'Pompoko', 'director': 'Isao Takahata', 'año': '1994', 'pais': 'Japón',
             'fecha_funcion': '11/04/2025', 'locacion': 'Pino Hachado 905', 'tipo': 'Animación', 'ciclo_slug': 'cine-comunitario', 'orden': 1},
            {'titulo': 'La estrategia del caracol', 'director': 'Sergio Cabrera', 'año': '1993', 'pais': 'Colombia',
             'fecha_funcion': '18/04/2025', 'ciclo_slug': 'cine-comunitario', 'orden': 2},
            {'titulo': 'Los olvidados', 'director': 'Luis Buñuel', 'año': '1950', 'pais': 'México',
             'fecha_funcion': '25/04/2025', 'locacion': 'Pino Hachado 905', 'ciclo_slug': 'cine-comunitario', 'orden': 3},
            # Kaurismäki
            {'titulo': 'Hojas del Otoño (Kuolleet lehdet)', 'director': 'Aki Kaurismäki', 'año': '2023', 'pais': 'Finlandia',
             'fecha_funcion': '30/05/2025', 'locacion': 'Presidente Ríos 1180', 'ciclo_slug': 'aki-kaurismaki', 'orden': 1},
            # Perdiendo el Tiempo
            {'titulo': 'Más allá de los dos minutos infinitos', 'director': 'Junta Yamaguchi', 'año': '2020', 'pais': 'Japón',
             'fecha_funcion': '06/06/2025', 'locacion': 'Presidente Ríos 1180', 'ciclo_slug': 'perdiendo-el-tiempo', 'orden': 1},
            {'titulo': 'Predestinación (Predestination)', 'director': 'Michael Spierig / Peter Spierig', 'año': '2014', 'pais': 'Australia',
             'fecha_funcion': '13/06/2025', 'ciclo_slug': 'perdiendo-el-tiempo', 'orden': 2},
            {'titulo': 'La chica que saltaba a través del tiempo', 'director': 'Mamoru Hosoda', 'año': '2006', 'pais': 'Japón',
             'fecha_funcion': '20/06/2025', 'tipo': 'Animación', 'ciclo_slug': 'perdiendo-el-tiempo', 'orden': 3},
            {'titulo': 'Querida, voy a comprar cigarrillos y vuelvo', 'director': 'Mariano Cohn / Gastón Duprat', 'año': '2011', 'pais': 'Argentina',
             'fecha_funcion': 'Jun 2025', 'ciclo_slug': 'perdiendo-el-tiempo', 'orden': 4},
            # Satoshi Kon
            {'titulo': 'Perfect Blue', 'director': 'Satoshi Kon', 'año': '1997', 'pais': 'Japón',
             'fecha_funcion': '05/07/2025', 'locacion': 'Pino Hachado #950', 'tipo': 'Animación', 'ciclo_slug': 'satoshi-kon', 'orden': 1},
            {'titulo': 'Tokyo Godfathers', 'director': 'Satoshi Kon', 'año': '2003', 'pais': 'Japón',
             'fecha_funcion': '12/07/2025', 'locacion': 'Pino Hachado #950', 'tipo': 'Animación', 'ciclo_slug': 'satoshi-kon', 'orden': 2},
            {'titulo': 'Millennium Actress', 'director': 'Satoshi Kon', 'año': '2001', 'pais': 'Japón',
             'fecha_funcion': '19/07/2025', 'locacion': 'Pino Hachado #950', 'tipo': 'Animación', 'ciclo_slug': 'satoshi-kon', 'orden': 3},
            # Vejez 1
            {'titulo': 'Coronación', 'director': 'Silvio Caiozzi', 'año': '2000', 'pais': 'Chile',
             'fecha_funcion': 'Ago 2025', 'locacion': 'Pino Hachado #950', 'ciclo_slug': 'vejez-1-cesfam', 'orden': 1},
            {'titulo': 'Varda par Agnès', 'director': 'Agnès Varda', 'año': '2019', 'pais': 'Francia',
             'fecha_funcion': '27/08/2025', 'locacion': 'Pino Hachado #950', 'tipo': 'Documental', 'ciclo_slug': 'vejez-1-cesfam', 'orden': 2},
            # Adicciones
            {'titulo': 'Another Round (Druk)', 'director': 'Thomas Vinterberg', 'año': '2020', 'pais': 'Dinamarca',
             'fecha_funcion': '04/09/2025', 'locacion': 'Julio Zegers #1001', 'ciclo_slug': 'adicciones', 'orden': 1},
            {'titulo': 'Requiem por un sueño', 'director': 'Darren Aronofsky', 'año': '2000', 'pais': 'EE.UU.',
             'fecha_funcion': '11/09/2025', 'ciclo_slug': 'adicciones', 'orden': 2},
            {'titulo': 'Entre ponerle y no ponerle', 'director': 'Héctor Ríos', 'año': '1971', 'pais': 'Chile',
             'fecha_funcion': '20/09/2025', 'locacion': 'Julio Zegers #1001', 'tipo': 'Cortometraje', 'ciclo_slug': 'adicciones', 'orden': 3},
            {'titulo': 'Juanito', 'director': 'Renato Dennis', 'año': '2021', 'pais': 'Chile',
             'fecha_funcion': '20/09/2025', 'locacion': 'Julio Zegers #1001', 'tipo': 'Cortometraje', 'ciclo_slug': 'adicciones', 'orden': 4},
            {'titulo': 'Kids', 'director': 'Larry Clark', 'año': '1995', 'pais': 'EE.UU.',
             'fecha_funcion': '23/09/2025', 'locacion': 'Julio Zegers #1001', 'ciclo_slug': 'adicciones', 'orden': 5},
            # Vejez 2
            {'titulo': 'Harold and Maude', 'director': 'Hal Ashby', 'año': '1971', 'pais': 'EE.UU.',
             'fecha_funcion': '07/10/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'vejez-2', 'orden': 1},
            {'titulo': 'Amour', 'director': 'Michael Haneke', 'año': '2012', 'pais': 'Francia',
             'fecha_funcion': '16/10/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'vejez-2', 'orden': 2},
            {'titulo': 'The Father (El Padre)', 'director': 'Florian Zeller', 'año': '2020', 'pais': 'R.U.',
             'fecha_funcion': '20/10/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'vejez-2', 'orden': 3},
            # Depresión
            {'titulo': 'The Whale (La Ballena)', 'director': 'Darren Aronofsky', 'año': '2022', 'pais': 'EE.UU.',
             'fecha_funcion': '01/11/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'depresion', 'orden': 1},
            {'titulo': 'Love Liza', 'director': 'Todd Louiso', 'año': '2002', 'pais': 'EE.UU.',
             'fecha_funcion': '08/11/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'depresion', 'orden': 2},
            {'titulo': 'Her', 'director': 'Spike Jonze', 'año': '2013', 'pais': 'EE.UU.',
             'fecha_funcion': '15/11/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'depresion', 'orden': 3},
            {'titulo': 'Winter Light (Los comulgantes)', 'director': 'Ingmar Bergman', 'año': '1963', 'pais': 'Suecia',
             'fecha_funcion': '22/11/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'depresion', 'orden': 4},
            # El trabajo dignifica
            {'titulo': 'Life and Death in the Warehouse', 'director': 'Aysha Rafaele / Joseph Bullman', 'año': '2022', 'pais': 'R.U.',
             'fecha_funcion': '29/11/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'el-trabajo-dignifica', 'orden': 1},
            {'titulo': 'El patrón: radiografía de un crimen', 'director': 'Sebastián Schindel', 'año': '2014', 'pais': 'Argentina',
             'fecha_funcion': '06/12/2025', 'locacion': 'Julio Zegers #1001', 'hora': '19:30', 'ciclo_slug': 'el-trabajo-dignifica', 'orden': 2},
            # VIH
            {'titulo': 'Dallas Buyers Club', 'director': 'Jean-Marc Vallée', 'año': '2013', 'pais': 'EE.UU.',
             'fecha_funcion': '13/12/2025', 'locacion': 'Txafkintuwe, Korner 933', 'ciclo_slug': 'miniciclo-vih', 'orden': 1},
            # Herramientas nuevo fin del mundo
            {'titulo': 'La batalla de Argelia', 'director': 'Gillo Pontecorvo', 'año': '1966', 'pais': 'Italia/Argelia',
             'fecha_funcion': '02/04/2026', 'locacion': 'Julio Zegers #1001', 'hora': '19:00', 'ciclo_slug': 'herramientas-nuevo-fin-del-mundo', 'orden': 1},
            {'titulo': 'Videograma de una revolución', 'director': 'Harun Farocki / Andrei Ujică', 'año': '1992', 'pais': 'Alemania',
             'fecha_funcion': 'Abr 2026', 'tipo': 'Documental', 'ciclo_slug': 'herramientas-nuevo-fin-del-mundo', 'orden': 2},
            {'titulo': 'El Rati Horror Show', 'director': 'Enrique Piñeyro', 'año': '2010', 'pais': 'Argentina',
             'fecha_funcion': 'Abr 2026', 'tipo': 'Documental', 'ciclo_slug': 'herramientas-nuevo-fin-del-mundo', 'orden': 3},
            # SATÍRICO
            {'titulo': 'Tiempo de valientes', 'director': 'Damián Szifron', 'año': '2005', 'pais': 'Argentina',
             'fecha_funcion': '16/04/2026', 'ciclo_slug': 'satirico', 'orden': 1},
            {'titulo': 'La vida de Brian', 'director': 'Terry Jones', 'año': '1979', 'pais': 'R.U.',
             'fecha_funcion': '23/04/2026', 'ciclo_slug': 'satirico', 'orden': 2},
            {'titulo': 'Rubber', 'director': 'Quentin Dupieux', 'año': '2010', 'pais': 'Francia',
             'fecha_funcion': '30/04/2026', 'ciclo_slug': 'satirico', 'orden': 3},
            # Cine iraní
            {'titulo': 'Persepolis', 'director': 'Marjane Satrapi / Vincent Paronnaud', 'año': '2007', 'pais': 'Francia/Irán',
             'fecha_funcion': '07/05/2026', 'locacion': 'Julio Zegers #1001', 'tipo': 'Animación', 'ciclo_slug': 'cine-irani', 'orden': 1},
            {'titulo': 'Los niños del fin del mundo', 'director': 'Marzieh Meshkini', 'año': '2008', 'pais': 'Irán',
             'fecha_funcion': '14/05/2026', 'locacion': 'Julio Zegers #1001', 'ciclo_slug': 'cine-irani', 'orden': 2},
            {'titulo': 'La semilla del árbol sagrado', 'director': 'Mohammad Rasoulof', 'año': '2024', 'pais': 'Irán',
             'fecha_funcion': '21/05/2026', 'locacion': 'Julio Zegers #1001', 'ciclo_slug': 'cine-irani', 'orden': 3},
            # Revelando Territorios
            {'titulo': 'Código rojo', 'director': 'Fabiola Albornoz', 'año': '', 'pais': 'Chile',
             'fecha_funcion': '11/06/2026', 'locacion': 'Julio Zegers #1001', 'hora': '19:00', 'ciclo_slug': 'revelando-territorios', 'orden': 1},
            {'titulo': 'La casa prometida', 'director': 'Renato Dennis', 'año': '', 'pais': 'Chile',
             'fecha_funcion': '18/06/2026', 'locacion': 'Julio Zegers #1001', 'hora': '19:00', 'ciclo_slug': 'revelando-territorios', 'orden': 2},
        ]

        for data in funciones_data:
            ciclo_slug = data.pop('ciclo_slug')
            titulo = data.pop('titulo')
            try:
                ciclo = Ciclo.objects.get(slug=ciclo_slug)
            except Ciclo.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'    Ciclo {ciclo_slug} no encontrado, saltando función.'))
                continue
            Funcion.objects.get_or_create(
                titulo_pelicula=titulo,
                ciclo=ciclo,
                defaults={**data, 'ciclo': ciclo}
            )

        self.stdout.write(self.style.SUCCESS(f'    {len(funciones_data)} funciones creadas.'))

        # ─── Crear eventos especiales ───
        self.stdout.write('  Creando eventos especiales...')
        eventos_data = [
            {'titulo': 'Completada a beneficio', 'fecha': '16/08/2024',
             'descripcion': 'Completada para recaudar fondos y comprar un parlante.'},
            {'titulo': 'Conversatorio con Renato Dennis', 'fecha': '20/09/2025',
             'descripcion': 'Conversatorio con el director Renato Dennis posterior a la proyección de Juanito.'},
            {'titulo': 'Estreno Chew Müley', 'fecha': '06/11/2025',
             'descripcion': 'Estreno del documental del Colectivo Cau Cau Films sobre la desaparición de Julia Chuñil Catricura. Txafkintuwe, Korner 933.'},
            {'titulo': 'EMPs gratuitos', 'fecha': '22/11/2025',
             'descripcion': 'Exámenes de Medicina Preventiva gratuitos previo a la función (alianza CESFAM).'},
            {'titulo': 'Lanzamiento libro Las Moscas', 'fecha': 'Ene 2026',
             'descripcion': 'Lanzamiento del libro "Las Moscas" y cierre de temporada de verano.'},
            {'titulo': 'Videollamada con Fabiola Albornoz', 'fecha': '11/06/2026',
             'descripcion': 'Conversatorio vía videollamada con la directora Fabiola Albornoz (Código rojo).'},
            {'titulo': 'Proyección online simultánea', 'fecha': '18/06/2026',
             'descripcion': 'La casa prometida disponible online durante la proyección presencial.'},
        ]
        for data in eventos_data:
            EventoEspecial.objects.get_or_create(titulo=data['titulo'], defaults=data)
        self.stdout.write(self.style.SUCCESS(f'    {len(eventos_data)} eventos creados.'))

        self.stdout.write(self.style.SUCCESS('[OK] Base de datos poblada exitosamente.'))
