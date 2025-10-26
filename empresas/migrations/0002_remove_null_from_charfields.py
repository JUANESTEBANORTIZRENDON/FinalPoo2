# Generated manually for SonarCloud fixes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historialcambios',
            name='modelo_afectado',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Nombre del modelo que fue modificado',
                max_length=100,
                verbose_name='Modelo Afectado'
            ),
        ),
        migrations.AlterField(
            model_name='historialcambios',
            name='user_agent',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Información del navegador/dispositivo',
                verbose_name='User Agent'
            ),
        ),
        migrations.AlterField(
            model_name='historialcambios',
            name='url_solicitada',
            field=models.URLField(
                blank=True,
                default='',
                max_length=500,
                verbose_name='URL Solicitada'
            ),
        ),
        migrations.AlterField(
            model_name='historialcambios',
            name='metodo_http',
            field=models.CharField(
                blank=True,
                default='',
                help_text='GET, POST, PUT, DELETE, etc.',
                max_length=10,
                verbose_name='Método HTTP'
            ),
        ),
    ]
