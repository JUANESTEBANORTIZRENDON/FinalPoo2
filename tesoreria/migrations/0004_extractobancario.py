
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('tesoreria', '0003_pagodetalle'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtractoBancario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('descripcion', models.CharField(max_length=255)),
                ('referencia', models.CharField(blank=True, max_length=128)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=15)),
                ('conciliado', models.BooleanField(default=False)),
                ('cuenta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='extractos', to='tesoreria.cuentabancaria')),
                ('pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conciliaciones', to='tesoreria.pago')),
            ],
        ),
    ]
