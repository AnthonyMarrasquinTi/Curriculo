from django.shortcuts import render, get_object_or_404
from apps.perfil.models import DatosPersonales
from apps.trayectoria.models import (
    ExperienciaLaboral,
    CursoRealizado,
    Reconocimiento,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage,
)

from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
import os
import base64
import mimetypes
from django.urls import reverse
from weasyprint import HTML, CSS


def _render_html_to_pdf(html: str, request) -> bytes:
    """Render HTML to PDF using WeasyPrint only.

    Returns raw PDF bytes. Raises RuntimeError with a helpful message on failure.
    """
    base_url = request.build_absolute_uri('/')
    try:
        # Force A4 and set reasonable margins (can be overridden by the template CSS)
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf(
            stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
        )
        return pdf_bytes
    except Exception as exc:
        # Provide a clear error so the developer can install WeasyPrint system deps if needed
        raise RuntimeError(f'WeasyPrint PDF generation failed: {exc}')


def _prepare_html_for_pdf(html: str, request=None) -> str:
    """Ensure relative asset URLs become absolute so WeasyPrint can fetch them.

    This function intentionally does NOT modify CSS variables or strip fonts so the original
    template CSS and design are preserved exactly.
    """
    if request is not None:
        try:
            from django.urls import reverse

            # Convert profile photo proxy relative URL to absolute
            photo_url = request.build_absolute_uri(reverse('ver_foto_perfil'))
            html = html.replace('src="/foto-perfil/"', f'src="{photo_url}"')

            # Convert static references to absolute URLs
            static_base = request.build_absolute_uri('/static/')
            html = html.replace('src="/static/', f'src="{static_base}')
            html = html.replace('href="/static/', f'href="{static_base}')
        except Exception:
            pass

    return html


def get_pdf_css():
    """Return the PDF CSS contents for tests and debugging.

    Prefer the PDF-specific stylesheet under `static/perfil/css/pdf/cv_pdf.css`.
    """
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_template_web.css')),
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'pdf', 'cv_pdf.css')),
        os.path.normpath(os.path.join(base_dir, 'static', 'perfil', 'css', 'cv_clean.css')),
    ]
    for css_path in candidates:
        try:
            with open(css_path, 'r', encoding='utf-8') as fh:
                return fh.read()
        except Exception:
            continue
    return ''


def _get_foto_perfil_base64(perfil):
    """Download profile photo from Azure URL and return as base64 data URL for PDF embedding.
    
    This ensures the photo works in PDF generation in both local and production (Render) environments.
    Returns None if photo is not available or download fails.
    """
    if not getattr(perfil, 'foto_perfil_url', None):
        return None
    
    try:
        from apps.trayectoria.views import _download_blob_from_url
        from urllib.request import urlopen
        from urllib.parse import urlparse
        
        blob_url = perfil.foto_perfil_url
        
        # Try primary method: use existing helper
        try:
            data, filename = _download_blob_from_url(blob_url)
        except Exception:
            # Fallback: direct HTTP fetch
            try:
                resp = urlopen(blob_url, timeout=5)
                data = resp.read()
                filename = os.path.basename(urlparse(blob_url).path) or 'profile.png'
            except Exception:
                return None
        
        # Guess MIME type; default to PNG
        mime, _ = mimetypes.guess_type(filename)
        if not mime:
            mime = 'image/png'
        
        # Convert to base64 data URL
        b64 = base64.b64encode(data).decode('utf-8')
        return f'data:{mime};base64,{b64}'
    except Exception:
        return None





def hoja_vida_publica(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        perfil = DatosPersonales.objects.create(
            nombres="Perfil",
            apellidos="Predeterminado",
            descripcionperfil="Perfil por defecto",
            perfilactivo=1,
            nacionalidad="Colombia",
            lugarnacimiento="Bogotá",
            fechanacimiento=date.today(),
            numerocedula="1234567890",
            sexo="H",
            estadocivil="Soltero",
            licenciaconducir="B1",
            telefonoconvencional="3001234567",
            telefonofijo="6012345678",
            direcciontrabajo="Calle 123",
            direcciondomiciliaria="Carrera 456",
            sitioweb="https://example.com"
        )

    # Obtain active experiences for the profile and group them by company.
    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    # Order each company's experiences by start date desc and order companies
    # by the most recent experience date (desc).
    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio')

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento')

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto')

    # Venta Garage: visible records ordered by product name (ascending)
    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

    context = {
        'perfil': perfil,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
    }

    # Provide the same photo proxy URL used by the PDF path so browsers can fetch the image
    foto_perfil_proxy_url = None
    if getattr(perfil, 'foto_perfil_url', None):
        foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"
    context['foto_perfil_proxy_url'] = foto_perfil_proxy_url

    # Public render - use new clean template
    response = render(request, 'perfil/cv_clean.html', context)
    return response


def descargar_cv_pdf(request):
    """Generate a PDF of the public CV using the new professional template."""
    from django.http import HttpResponse

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)

    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio')

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento')

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto')

    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

    foto_perfil_proxy_url = None
    foto_perfil_base64 = None
    if getattr(perfil, 'foto_perfil_url', None):
        # Try to get base64 version for PDF (works in both local and Render)
        foto_perfil_base64 = _get_foto_perfil_base64(perfil)
        # Fallback to proxy URL if base64 fails
        if not foto_perfil_base64:
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"

    context = {
        'perfil': perfil,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'foto_perfil_base64': foto_perfil_base64,
        'certificates': [],
    }

    # Render the PDF-specific template (no interactive elements)
    html = render_to_string('perfil/pdf/cv_template_web.html', context, request=request)
    html = _prepare_html_for_pdf(html, request)
    try:
        # Use the dedicated PDF CSS (includes @page size and margins)
        css_text = get_pdf_css()
        pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(
            stylesheets=[CSS(string=css_text)]
        )
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="hoja_de_vida.pdf"'
    return response


def descargar_cv_completo_pdf(request):
    """Generate a professional PDF with CV and embedded certificates (Check All)."""
    from django.http import HttpResponse
    from django.urls import reverse
    from apps.trayectoria.views import _download_blob_from_url
    from pypdf import PdfReader, PdfWriter

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)

    experiencias_qs = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    from django.db.models import Max

    companies = (
        experiencias_qs
        .values('nombrempresa')
        .annotate(latest=Max('fechainiciogestion'))
        .order_by('-latest')
    )

    experiencias = []
    for c in companies:
        company_name = c['nombrempresa']
        company_experiences = (
            experiencias_qs.filter(nombrempresa=company_name)
            .order_by('-fechainiciogestion')
        )
        experiencias.append({'empresa': company_name, 'experiencias': company_experiences})

    cursos = CursoRealizado.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechainicio')

    reconocimientos = Reconocimiento.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechareconocimiento')

    productos_academicos = ProductoAcademico.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    )

    productos_laborales = ProductoLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('-fechaproducto')

    ventas_garage = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True,
    ).order_by('nombreproducto')

    # Collect ALL certificates from the three tables that have rutacertificado
    # and are active for frontend display (activarparaqueseveaenfront=True)
    # This includes: EXPERIENCIALABORAL, CURSOSREALIZADOS, RECONOCIMIENTOS
    certificados_meta = []

    # 1. EXPERIENCIALABORAL: All experiences with certificates
    for e in experiencias_qs:  # experiencias_qs already filtered by activarparaqueseveaenfront=True
        if getattr(e, 'rutacertificado', None) and e.rutacertificado.strip():
            certificados_meta.append({
                'model': e,
                'titulo': e.cargodesempenado or e.nombrempresa or 'Experiencia Laboral',
                'tipo': 'Experiencia Laboral',
            })

    # 2. CURSOSREALIZADOS: All courses with certificates
    for c in cursos:  # cursos already filtered by activarparaqueseveaenfront=True
        if getattr(c, 'rutacertificado', None) and c.rutacertificado.strip():
            certificados_meta.append({
                'model': c,
                'titulo': c.nombrecurso or 'Curso',
                'tipo': 'Curso',
            })

    # 3. RECONOCIMIENTOS: All recognitions with certificates
    for r in reconocimientos:  # reconocimientos already filtered by activarparaqueseveaenfront=True
        if getattr(r, 'rutacertificado', None) and r.rutacertificado.strip():
            certificados_meta.append({
                'model': r,
                'titulo': r.descripcionreconocimiento or r.tiporeconocimiento or 'Reconocimiento',
                'tipo': 'Reconocimiento',
            })

    foto_perfil_proxy_url = None
    foto_perfil_base64 = None
    if getattr(perfil, 'foto_perfil_url', None):
        # Try to get base64 version for PDF (works in both local and Render)
        foto_perfil_base64 = _get_foto_perfil_base64(perfil)
        # Fallback to proxy URL if base64 fails
        if not foto_perfil_base64:
            foto_perfil_proxy_url = f"{request.scheme}://{request.get_host()}/foto-perfil/"

    context = {
        'perfil': perfil,
        'datos_personales': perfil,
        'experiencias': experiencias,
        'experiencias_qs': experiencias_qs,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'ventas_garage': ventas_garage,
        'foto_perfil_proxy_url': foto_perfil_proxy_url,
        'foto_perfil_base64': foto_perfil_base64,
    }

    # Generate CV PDF using the PDF-only template (no interactive elements)
    html = render_to_string('perfil/pdf/cv_template_web.html', context, request=request)
    html = _prepare_html_for_pdf(html, request)
    try:
        css_text = get_pdf_css()
        cv_pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf(
            stylesheets=[CSS(string=css_text)]
        )
    except Exception:
        return HttpResponse('Error generating PDF', status=500)
    
    # Determine which certificates to include based on GET params (supports individual selection)
    requested = request.GET.getlist('certificados')
    check_all = request.GET.get('check_all') or request.GET.get('select_all')

    if check_all:
        # CHECK ALL: Include ALL certificates from all three tables (Experiencia, Cursos, Reconocimientos)
        # that have rutacertificado and are active for frontend display
        selected_meta = certificados_meta  # All certificates collected above
    elif requested:
        # requested values are like 'experiencia_5' or 'curso_3' or 'reconocimiento_2'
        selected_meta = []
        for token in requested:
            parts = token.split('_')
            if len(parts) != 2:
                continue
            tipo, pk = parts[0], parts[1]
            for cm in certificados_meta:
                model = cm['model']
                try:
                    if str(getattr(model, 'pk', '')) == pk:
                        selected_meta.append(cm)
                        break
                except Exception:
                    continue
    else:
        # No certificates requested
        selected_meta = []

    # If there are certificates selected, merge them into the PDF
    if selected_meta:
        writer = PdfWriter()
        
        # Add all CV pages
        try:
            cv_reader = PdfReader(BytesIO(cv_pdf_bytes))
            for page in cv_reader.pages:
                writer.add_page(page)
        except Exception as e:
            return HttpResponse(f'Error processing CV PDF: {str(e)}', status=500)
        
        # Add each selected certificate
        for cert_meta in selected_meta:
            try:
                model = cert_meta['model']
                titulo = cert_meta['titulo']
                
                # Get the blob URL from the model
                cert_url = getattr(model, 'rutacertificado', None)
                if cert_url:
                    # Download certificate from Azure
                    cert_bytes, filename = _download_blob_from_url(cert_url)
                    filename = filename or ''
                    lower = filename.lower()

                    # If image -> embed as preview page
                    if lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        b64 = base64.b64encode(cert_bytes).decode('ascii')
                        mime, _ = mimetypes.guess_type(filename)
                        if not mime:
                            mime = 'image/png'
                        data_uri = f"data:{mime};base64,{b64}"

                        cert_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                            'titulo': titulo,
                            'image_data_uri': data_uri,
                        })
                        cert_html = _prepare_html_for_pdf(cert_html, request)
                        try:
                            pdf_bytes = HTML(string=cert_html, base_url=request.build_absolute_uri('/')).write_pdf(
                                stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                            )
                            cert_reader = PdfReader(BytesIO(pdf_bytes))
                            for page in cert_reader.pages:
                                writer.add_page(page)
                        except Exception:
                            pass
                    else:
                        # Treat as PDF: overlay the title onto the first page of the certificate
                        title_html = render_to_string('perfil/pdf/certificado_wrapper.html', {
                            'titulo': titulo,
                            'image_data_uri': '__title_only__',
                        })
                        title_html = _prepare_html_for_pdf(title_html, request)
                        try:
                            title_pdf_bytes = HTML(string=title_html, base_url=request.build_absolute_uri('/')).write_pdf(
                                stylesheets=[CSS(string='@page { size: A4; margin: 15mm }')]
                            )
                            title_reader = PdfReader(BytesIO(title_pdf_bytes))
                        except Exception:
                            title_reader = None

                        try:
                            cert_reader = PdfReader(BytesIO(cert_bytes))
                            if len(cert_reader.pages) == 0:
                                # Nothing to append
                                continue

                            # If we have a title overlay page, merge it on top of the first certificate page
                            if title_reader and len(title_reader.pages) > 0:
                                try:
                                    cert_first = cert_reader.pages[0]
                                    overlay = title_reader.pages[0]
                                    # Merge overlay (title) into the certificate first page so title appears on same page
                                    cert_first.merge_page(overlay)
                                    # Add merged first page
                                    writer.add_page(cert_first)
                                    # Add remaining certificate pages
                                    for p in cert_reader.pages[1:]:
                                        writer.add_page(p)
                                except Exception:
                                    # Fallback: if merge fails, append title page then certificate pages
                                    for p in title_reader.pages:
                                        writer.add_page(p)
                                    for p in cert_reader.pages:
                                        writer.add_page(p)
                            else:
                                # No title overlay available — just append certificate pages
                                for p in cert_reader.pages:
                                    writer.add_page(p)
                        except Exception:
                            # Skip if certificate PDF invalid
                            pass
            except Exception:
                # Skip individual certificate errors
                pass
        
        # Write the final merged PDF
        out_buf = BytesIO()
        writer.write(out_buf)
        response = HttpResponse(out_buf.getvalue(), content_type='application/pdf')
    else:
        # No certificates, just return CV
        response = HttpResponse(cv_pdf_bytes, content_type='application/pdf')
    
    response['Content-Disposition'] = 'attachment; filename="cv_completo.pdf"'
    return response


# --- Secure photo proxy view ---
from apps.trayectoria.views import _download_blob_from_url


def ver_foto_perfil(request):
    """Proxy view to serve the profile photo from Azure without exposing the blob URL."""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        # Create default profile if none exists with all required fields
        from datetime import date
        try:
            perfil = DatosPersonales.objects.create(
                nombres="Perfil",
                apellidos="Predeterminado",
                descripcionperfil="Perfil por defecto",
                perfilactivo=1,
                nacionalidad="Colombia",
                lugarnacimiento="Bogotá",
                fechanacimiento=date.today(),
                numerocedula="1234567890",
                sexo="H",
                estadocivil="Soltero",
                licenciaconducir="B1",
                telefonoconvencional="3001234567",
                telefonofijo="6012345678",
                direcciontrabajo="Calle 123",
                direcciondomiciliaria="Carrera 456",
                sitioweb="https://example.com"
            )
        except Exception as e:
            return HttpResponse(f'Error creando perfil: {str(e)}', status=500)
    blob_url = getattr(perfil, 'foto_perfil_url', None)
    if not blob_url:
        return HttpResponse('No profile photo available.', status=404)

    # Primary attempt: use existing helper that downloads from Azure blobs.
    try:
        data, filename = _download_blob_from_url(blob_url)
    except Exception:
        # Fallback: try a direct HTTP fetch (works for public URLs or SAS URLs).
        try:
            from urllib.request import urlopen
            from urllib.parse import urlparse

            resp_fetch = urlopen(blob_url)
            data = resp_fetch.read()
            filename = os.path.basename(urlparse(blob_url).path) or 'profile.png'
        except Exception as exc:
            return HttpResponse(f'Error fetching profile photo: {exc}', status=500)

    # Guess mime type from filename; default to PNG to preserve previous behavior
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = 'image/png'

    resp = HttpResponse(data, content_type=mime)
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp

