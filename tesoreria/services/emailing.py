
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_invoice_email(factura, pdf_bytes: bytes, destinatario: str = None) -> None:
    to = [destinatario or getattr(factura.cliente, 'email', None)]
    to = [x for x in to if x]
    if not to:
        return
    subject = f"Factura {factura.numero_factura} - {factura.empresa.nombre}"
    body_html = render_to_string('tesoreria/emails/factura_email.html', {'factura': factura})
    email = EmailMessage(
        subject=subject,
        body=body_html,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None),
        to=to,
    )
    email.content_subtype = 'html'
    nombre_pdf = f"{factura.numero_factura}_{factura.cliente.razon_social.replace(' ', '_')}.pdf"
    email.attach(nombre_pdf, pdf_bytes, 'application/pdf')
    email.send(fail_silently=False)
