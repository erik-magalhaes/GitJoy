# Gera o Index.html (o arquivo que vai no Apps Script) a partir de pagina.html, embutindo as imagens de img/.
import base64, pathlib
aqui = pathlib.Path(__file__).parent
html = (aqui / 'pagina.html').read_text()
for chave, arq in [('LOGO', 'logo.webp'), ('DOIS', 'dois.webp'), ('CARAS', 'caras.webp')]:
    b64 = base64.b64encode((aqui / 'img' / arq).read_bytes()).decode()
    html = html.replace('{{' + chave + '}}', 'data:image/webp;base64,' + b64)
(aqui / 'Index.html').write_text(html)
print('Index.html', len(html) // 1024, 'KB')
