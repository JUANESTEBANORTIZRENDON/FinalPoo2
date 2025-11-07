#!/usr/bin/env bash
# Build script para Render - S_CONTABLE
set -o errexit

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗂️  Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --clear

echo "🔍 Verificando assets del admin..."
python manage.py check_admin_assets || echo "⚠️  Advertencia: Verificación de assets falló (continuando...)"

echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

echo "✅ Build completado exitosamente!"