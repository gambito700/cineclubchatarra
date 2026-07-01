import json
import re
import shutil
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify


from core.models import Funcion


def normalize(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.lower().strip()


def parse_timestamp(ts):
    return datetime.fromtimestamp(ts)


def extract_caption(post):
    if 'title' in post and post.get('title', '').strip():
        return post['title']
    for item in post.get('media', []):
        if item.get('title', '').strip():
            return item['title']
    for lv in post.get('label_values', []):
        if lv.get('label') in ('Descripción', 'Título') and lv.get('value', '').strip():
            return lv['value']
    return ''


def extract_uris(post):
    uris = []
    if 'label_values' in post:
        for lv in post.get('label_values', []):
            if lv.get('label') == 'Contenido multimedia':
                for m in lv.get('media', []):
                    uri = m.get('uri', '')
                    if uri:
                        uris.append(uri)
    else:
        for m in post.get('media', []):
            uri = m.get('uri', '')
            if uri:
                uris.append(uri)
    return uris


def get_media_path(uri, media_dir):
    rel = uri.replace('media/posts/', '', 1)
    p = Path(media_dir) / rel
    if p.exists():
        return p
    alt = Path(media_dir) / Path(uri).name
    if alt.exists():
        return alt
    return None


def is_likely_poster(ext):
    return ext.lower() in ('.jpg', '.jpeg', '.png', '.webp')


def convert_heic_to_jpg(src, dst):
    try:
        from PIL import Image
        img = Image.open(src)
        rgb = img.convert('RGB')
        rgb.save(dst, 'JPEG', quality=90)
        return True
    except Exception as e:
        print(f'    ! Error converting HEIC {src.name}: {e}')
        return False


def jueves_cercano(fecha, post_date, dias_tolerancia=4):
    if not fecha:
        return False
    diff = abs((fecha - post_date).days)
    return diff <= dias_tolerancia


def es_jueves(dt):
    return dt.weekday() == 3


class Command(BaseCommand):
    help = 'Importa posters desde export de Instagram, matcheando por caption + timestamp + OCR'

    def add_arguments(self, parser):
        parser.add_argument('--posts-json', default='', help='Ruta a posts.json')
        parser.add_argument('--posts_1-json', default='', help='Ruta a posts_1.json')
        parser.add_argument('--media-dir', default='', help='Ruta a media/posts/')
        parser.add_argument('--dry-run', action='store_true', help='Solo mostrar qué se matchearía sin copiar')
        parser.add_argument('--report', action='store_true', help='Generar reporte HTML')
        parser.add_argument('--ocr', action='store_true', help='Usar OCR en imágenes sin match (lento)')
        parser.add_argument('--dest-dir', default='', help='Directorio destino para posters')

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parent.parent.parent.parent
        export_base = base.parent

        posts_json = Path(options['posts_json']) if options['posts_json'] else export_base / 'your_instagram_activity' / 'media' / 'posts.json'
        posts_1_json = Path(options['posts_1_json']) if options['posts_1_json'] else export_base / 'your_instagram_activity' / 'media' / 'posts_1.json'
        media_dir = Path(options['media_dir']) if options['media_dir'] else export_base / 'media' / 'posts'
        dest_dir = Path(options['dest_dir']) if options['dest_dir'] else base / 'core' / 'static' / 'core' / 'posters'

        if not posts_json.exists():
            raise CommandError(f'posts.json no encontrado: {posts_json}')
        if not posts_1_json.exists():
            raise CommandError(f'posts_1.json no encontrado: {posts_1_json}')
        if not media_dir.exists():
            raise CommandError(f'media dir no encontrado: {media_dir}')

        dry_run = options['dry_run']
        use_ocr = options['ocr']
        make_report = options['report']

        self.stdout.write(f'posts.json: {posts_json}')
        self.stdout.write(f'posts_1.json: {posts_1_json}')
        self.stdout.write(f'media dir: {media_dir}')
        self.stdout.write(f'dest dir: {dest_dir}')
        self.stdout.write(f'dry-run: {dry_run}')
        self.stdout.write(f'ocr: {use_ocr}')
        self.stdout.write('')

        with open(posts_json, encoding='utf-8') as f:
            data_old = json.load(f)
        with open(posts_1_json, encoding='utf-8') as f:
            data_new = json.load(f)

        posts = []
        for p in data_old:
            caption = extract_caption(p)
            uris = extract_uris(p)
            ts = p.get('timestamp', 0)
            posts.append({'caption': caption, 'uris': uris, 'timestamp': ts, 'source': 'posts.json'})
        for p in data_new:
            caption = extract_caption(p)
            uris = extract_uris(p)
            ts = p.get('creation_timestamp', 0)
            if not ts and uris:
                for m in p.get('media', []):
                    if m.get('creation_timestamp'):
                        ts = m['creation_timestamp']
                        break
            posts.append({'caption': caption, 'uris': uris, 'timestamp': ts, 'source': 'posts_1.json'})

        self.stdout.write(f'Total posts cargados: {len(posts)}')
        self.stdout.write(f'Total funciones en DB: {Funcion.objects.count()}')
        self.stdout.write('')

        funciones = list(Funcion.objects.all())
        asignados = set()
        resultados = []

        # ─── FASE 1: Caption matching ───
        self.stdout.write(self.style.NOTICE('=== FASE 1: Caption matching ==='))
        for idx, post in enumerate(posts):
            caption = post['caption']
            if not caption.strip():
                continue
            caption_norm = normalize(caption)
            for func in funciones:
                if func.pk in asignados:
                    continue
                titulo = func.titulo_pelicula
                titulo_norm = normalize(titulo)
                if titulo_norm in caption_norm:
                    asignados.add(func.pk)
                    resultados.append((func, post, 'caption'))
                    self.stdout.write(f'  [OK] {func.titulo_pelicula} -> caption match (post {idx})')
                    break
        self.stdout.write(f'  Matches Fase 1: {len([r for r in resultados if r[2] == "caption"])}')
        self.stdout.write('')

        # ─── FASE 2: Timestamp + jueves + keyword ───
        self.stdout.write(self.style.NOTICE('=== FASE 2: Timestamp + keyword matching ==='))
        nuevos_fase2 = 0
        for idx, post in enumerate(posts):
            if idx >= len(resultados) and any(r[1] == post for r in resultados):
                continue
            if any(r[1] == post for r in resultados):
                continue
            ts = post['timestamp']
            if not ts:
                continue
            post_date = parse_timestamp(ts)
            caption = post['caption']
            caption_norm = normalize(caption) if caption else ''

            candidatas = []
            for func in funciones:
                if func.pk in asignados:
                    continue
                if jueves_cercano(func.fecha_precisa, post_date):
                    puntaje = 1
                    if caption_norm:
                        palabras_titulo = normalize(func.titulo_pelicula).split()
                        coincidencias = sum(1 for p in palabras_titulo if len(p) > 3 and p in caption_norm)
                        if coincidencias > 0:
                            puntaje += coincidencias
                    candidatas.append((func, puntaje))

            if not candidatas:
                candidatas = []
                for func in funciones:
                    if func.pk in asignados:
                        continue
                    palabras_titulo = normalize(func.titulo_pelicula).split()
                    if caption_norm:
                        coincidencias = sum(1 for p in palabras_titulo if len(p) > 3 and p in caption_norm)
                        if coincidencias >= 2 and len([p for p in palabras_titulo if len(p) > 3]) >= 2:
                            candidatas.append((func, coincidencias))

            if len(candidatas) == 1:
                func, _ = candidatas[0]
                asignados.add(func.pk)
                resultados.append((func, post, 'timestamp'))
                nuevos_fase2 += 1
                self.stdout.write(f'  [OK] {func.titulo_pelicula} -> timestamp+keyword match (post {idx})')
            elif len(candidatas) > 1:
                candidatas.sort(key=lambda x: -x[1])
                best = candidatas[0]
                if best[1] > 1:
                    func, _ = best
                    asignados.add(func.pk)
                    resultados.append((func, post, 'timestamp'))
                    nuevos_fase2 += 1
                    self.stdout.write(f'  [OK] {func.titulo_pelicula} -> best of {len(candidatas)} candidatos (post {idx})')
        self.stdout.write(f'  Matches Fase 2: {nuevos_fase2}')
        self.stdout.write('')

        # ─── FASE 3: OCR ───
        if use_ocr:
            self.stdout.write(self.style.NOTICE('=== FASE 3: OCR matching ==='))
            try:
                import easyocr
                reader = easyocr.Reader(['es', 'en'], gpu=False)
            except ImportError:
                self.stdout.write(self.style.WARNING('  easyocr no disponible - saltando OCR'))
                use_ocr = False

            if use_ocr:
                nuevos_ocr = 0
                for idx, post in enumerate(posts):
                    if any(r[1] == post for r in resultados):
                        continue
                    caption = post['caption']
                    uris = post['uris']
                    if not uris:
                        continue
                    uri = uris[0]
                    media_path = get_media_path(uri, media_dir)
                    if not media_path or not is_likely_poster(media_path.suffix):
                        continue
                    try:
                        self.stdout.write(f'  OCR en post {idx}...')
                        text_blocks = reader.readtext(str(media_path), detail=0)
                        ocr_text = ' '.join(text_blocks)
                        ocr_norm = normalize(ocr_text)
                        for func in funciones:
                            if func.pk in asignados:
                                continue
                            titulo_norm = normalize(func.titulo_pelicula)
                            if titulo_norm in ocr_norm:
                                asignados.add(func.pk)
                                resultados.append((func, post, 'ocr'))
                                nuevos_ocr += 1
                                self.stdout.write(f'  [OK] {func.titulo_pelicula} -> OCR match')
                                break
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  Error OCR post {idx}: {e}'))
                self.stdout.write(f'  Matches Fase 3: {nuevos_ocr}')
                self.stdout.write('')

        # ─── Copiar imágenes ───
        self.stdout.write(self.style.NOTICE('=== Copiando imágenes ==='))
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)

        copiados = 0
        for func, post, metodo in resultados:
            uris = post['uris']
            if not uris:
                continue
            uri = uris[0]
            media_path = get_media_path(uri, media_dir)
            if not media_path:
                self.stdout.write(self.style.WARNING(f'  ! Archivo no encontrado: {uri}'))
                continue

            slug = slugify(func.titulo_pelicula)[:50]
            ext = media_path.suffix.lower()
            convertir_heic = ext == '.heic'
            nombre_dest = f'{slug}.jpg' if convertir_heic else f'{slug}{ext}'
            dest_path = dest_dir / nombre_dest

            if dry_run:
                self.stdout.write(f'  [DRY-RUN] {func.titulo_pelicula} -> {nombre_dest} ({metodo})')
                copiados += 1
                continue

            if dest_path.exists():
                self.stdout.write(f'  = {func.titulo_pelicula} -> ya existe ({nombre_dest})')
                func.poster_path = f'/static/core/posters/{nombre_dest}'
                func.save()
                copiados += 1
                continue

            try:
                if convertir_heic:
                    ok = convert_heic_to_jpg(media_path, dest_path)
                    if not ok:
                        self.stdout.write(self.style.WARNING(f'    ! Skip HEIC {media_path.name}'))
                        continue
                else:
                    shutil.copy2(media_path, dest_path)
                func.poster_path = f'/static/core/posters/{nombre_dest}'
                func.save()
                copiados += 1
                self.stdout.write(f'  [OK] {func.titulo_pelicula} -> {nombre_dest} ({metodo})')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERR] Error copiando {media_path.name}: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Posters asignados: {copiados}/{len(resultados)}'))

        # ─── Sin match ───
        sin_match = []
        for func in funciones:
            if func.pk not in asignados:
                sin_match.append(func)
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE(f'Funciones sin poster: {len(sin_match)}'))
        for func in sin_match:
            self.stdout.write(f'  - {func.titulo_pelicula} ({func.fecha_funcion})')

        # ─── Reporte ───
        if make_report:
            self.generar_reporte(resultados, sin_match, posts, dest_dir)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('¡Importación completada!'))

    def generar_reporte(self, resultados, sin_match, posts, dest_dir):
        report_path = dest_dir.parent / 'reporte_importacion.html'
        html = '<html><head><meta charset="utf-8"><title>Reporte Importación Posters</title>'
        html += '<style>body{font-family:sans-serif;max-width:800px;margin:auto;padding:20px}'
        html += 'h2{color:#333}.ok{color:green}.nope{color:orange}.sin{color:red}'
        html += 'li{margin:8px 0}img{max-width:200px;max-height:200px;border-radius:4px}</style></head><body>'
        html += '<h1>Reporte de Importación de Posters</h1>'

        html += f'<h2>Matcheados ({len(resultados)})</h2><ol>'
        for func, post, metodo in resultados:
            color = {'caption': 'green', 'timestamp': 'orange', 'ocr': 'blue'}.get(metodo, 'gray')
            html += f'<li><span class="ok">✓</span> <strong>{func.titulo_pelicula}</strong> '
            html += f'<span style="color:{color}">({metodo})</span>'
            if func.poster_path:
                html += f'<br><img src="{func.poster_path}" alt="{func.titulo_pelicula}">'
            html += '</li>'
        html += '</ol>'

        html += f'<h2>Sin match ({len(sin_match)})</h2><ul>'
        for func in sin_match:
            html += f'<li class="sin">✗ <strong>{func.titulo_pelicula}</strong> ({func.fecha_funcion})</li>'
        html += '</ul>'

        html += '<h2>Posts sin match de función</h2><ol>'
        for idx, post in enumerate(posts):
            if any(r[1] == post for r in resultados):
                continue
            caption = post['caption'][:200] if post['caption'] else '(sin caption)'
            uris = post['uris']
            ts = post.get('timestamp', 0)
            if ts:
                fecha = parse_timestamp(ts).strftime('%d/%m/%Y')
            else:
                fecha = '?'
            html += f'<li value="{idx}"><strong>[{fecha}]</strong> {caption}'
            if uris:
                uri = uris[0]
                rel = uri.replace('media/posts/', '', 1)
                src = dest_dir.parent.parent.parent.parent.parent / 'media' / 'posts' / rel
                if not src.exists():
                    src = dest_dir.parent.parent.parent.parent.parent / 'media' / 'posts' / Path(uri).name
                if src.exists():
                    html += f'<br><img src="file:///{src}" style="max-width:300px">'
            html += '</li>'
        html += '</ol>'

        html += '</body></html>'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        self.stdout.write(self.style.SUCCESS(f'Reporte generado: {report_path}'))
