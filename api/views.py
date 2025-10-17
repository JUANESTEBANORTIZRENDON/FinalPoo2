"""
Views para API REST con JWT
Convivencia con autenticación por sesiones (MVT)

IMPORTANTE: 
- Las vistas MVT (HTML) siguen usando sesiones Django normalmente
- Estas vistas API usan JWT para móviles/SPA
- request.user funciona igual en ambos casos
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .serializers import (
    RegistroSerializer,
    RegistroCompletoSerializer,
    MeSerializer, 
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ActivarCuentaSerializer
)


# ===== AUTENTICACIÓN JWT =====

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT
    Extiende la vista base de SimpleJWT
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Agregar información adicional en la respuesta
            user = User.objects.get(username=request.data.get('username'))
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/me/
    Retorna información del usuario autenticado
    Requiere: Authorization: Bearer <access_token>
    """
    serializer = MeSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    })


# ===== REGISTRO Y ACTIVACIÓN =====

@api_view(['POST'])
@permission_classes([AllowAny])
def registro_view(request):
    """
    POST /api/registro/
    Crea usuario y envía email de activación
    Body: {"username": "...", "email": "...", "password1": "...", "password2": "..."}
    """
    serializer = RegistroSerializer(data=request.data)
    
    if serializer.is_valid():
        # Crear usuario inactivo
        user = serializer.save()
        
        # Generar token de activación seguro
        signer = Signer()
        token = signer.sign(f"{user.id}:{user.email}")
        
        # Enviar email de activación
        try:
            subject = '🎉 ¡Bienvenido a S_CONTABLE! Activa tu cuenta'
            message = f"""
¡Hola {user.first_name or user.username}!

¡Bienvenido/a a S_CONTABLE - Tu Sistema Contable Colombiano! 🇨🇴

Gracias por registrarte. Para completar tu registro y activar tu cuenta, necesitas verificar tu email.

📱 PARA APLICACIONES MÓVILES:
Usa este token de activación: {token}

🌐 PARA NAVEGADOR WEB:
Haz clic en este enlace: http://127.0.0.1:8000/api/activar/?token={token}

⏰ IMPORTANTE:
- Este token expira en 24 horas por tu seguridad
- Solo puedes usar este token una vez
- Si no te registraste, ignora este email

¿Necesitas ayuda? Responde a este email.

¡Esperamos que disfrutes usando S_CONTABLE!

Cordialmente,
El equipo de S_CONTABLE 🚀
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'Usuario creado exitosamente. Revisa tu email para activar la cuenta.',
                'user_id': user.id,
                'email': user.email,
                'documento': getattr(user.perfil, 'documento_completo', 'No especificado')
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Si falla el email, eliminar usuario para evitar cuentas huérfanas
            user.delete()
            return Response({
                'success': False,
                'error': 'Error al enviar email de activación. Intenta nuevamente.',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_completo_view(request):
    """
    POST /api/registro-completo/
    Crea usuario con información completa colombiana y envía email de activación
    Body: Todos los campos del RegistroCompletoSerializer
    """
    serializer = RegistroCompletoSerializer(data=request.data)
    
    if serializer.is_valid():
        # Crear usuario completo con perfil
        user = serializer.save()
        
        # Generar token de activación seguro
        signer = Signer()
        token = signer.sign(f"{user.id}:{user.email}")
        
        # Enviar email de activación personalizado
        try:
            subject = '🎉 ¡Bienvenido a S_CONTABLE! Activa tu cuenta'
            
            # Información del perfil para personalizar el email
            perfil = user.perfil
            nombre_completo = f"{user.first_name} {user.last_name}".strip()
            documento = perfil.documento_completo if perfil.numero_documento else "No especificado"
            ciudad = f"{perfil.ciudad}, {perfil.departamento}" if perfil.ciudad else "Colombia"
            
            message = f"""
¡Hola {nombre_completo}!

¡Bienvenido/a a S_CONTABLE - Tu Sistema Contable Colombiano! 🇨🇴

Gracias por completar tu registro con nosotros. Hemos recibido tu información:

👤 INFORMACIÓN REGISTRADA:
• Nombre: {nombre_completo}
• Documento: {documento}
• Email: {user.email}
• Teléfono: {perfil.telefono or 'No especificado'}
• Ubicación: {ciudad}
• Profesión: {perfil.profesion or 'No especificada'}

📧 ACTIVACIÓN REQUERIDA:
Para completar tu registro y activar tu cuenta, necesitas verificar tu email.

📱 PARA APLICACIONES MÓVILES:
Usa este token de activación: {token}

🌐 PARA NAVEGADOR WEB:
Haz clic en este enlace: http://127.0.0.1:8000/api/activar/?token={token}

⏰ IMPORTANTE:
- Este token expira en 24 horas por tu seguridad
- Solo puedes usar este token una vez
- Si no completaste este registro, ignora este email

🔒 PRIVACIDAD:
Tu información está protegida según nuestra política de privacidad.
Solo será usada para brindarte el mejor servicio contable.

¿Necesitas ayuda? Responde a este email.

¡Esperamos que disfrutes usando S_CONTABLE para gestionar tu contabilidad!

Cordialmente,
El equipo de S_CONTABLE 🚀

---
S_CONTABLE - Sistema Contable Colombiano
Tu aliado en gestión financiera y contable
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'Registro completo exitoso. Revisa tu email para activar la cuenta.',
                'user_id': user.id,
                'email': user.email,
                'nombre_completo': nombre_completo,
                'documento': documento,
                'telefono': perfil.telefono,
                'ciudad': ciudad,
                'profesion': perfil.profesion or 'No especificada'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Si falla el email, eliminar usuario para evitar cuentas huérfanas
            user.delete()
            return Response({
                'success': False,
                'error': 'Error al enviar email de activación. Intenta nuevamente.',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def activar_cuenta_view(request):
    """
    POST /api/activar/
    Activa cuenta con token del email
    Body: {"token": "..."}
    """
    serializer = ActivarCuentaSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            # Verificar y decodificar token
            signer = Signer()
            unsigned_token = signer.unsign(token)
            user_id, email = unsigned_token.split(':', 1)
            
            # Buscar y activar usuario
            user = User.objects.get(id=user_id, email=email, is_active=False)
            user.is_active = True
            user.save()
            
            # Generar tokens JWT para login automático
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '¡Cuenta activada exitosamente!',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
            
        except (BadSignature, User.DoesNotExist, ValueError):
            return Response({
                'success': False,
                'error': 'Token inválido o expirado.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ===== RECUPERACIÓN DE CLAVE DE ACCESO =====

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_view(request):
    """
    POST /api/password/reset/
    Inicia recuperación de clave de acceso por email
    Body: {"email": "..."}
    """
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generar token de reset usando el sistema de Django
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Enviar email
            subject = 'Recuperar clave de acceso - S_CONTABLE'
            message = f"""
¡Hola {user.username}!

Recibimos una solicitud para restablecer tu clave de acceso en S_CONTABLE.

Token de recuperación: {token}
ID de usuario: {uid}

Para restablecer tu clave de acceso, usa estos datos en la aplicación.

Si no solicitaste este cambio, ignora este email.

Este enlace expira en 24 horas por seguridad.

Saludos,
El equipo de S_CONTABLE
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe
            pass
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error al enviar email. Intenta nuevamente.',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Siempre retornamos éxito por seguridad
        return Response({
            'success': True,
            'message': 'Si el email existe, recibirás instrucciones para restablecer tu clave de acceso.'
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    POST /api/password/reset/confirm/
    Confirma cambio de clave de acceso con token
    Body: {"token": "...", "uid": "...", "password1": "...", "password2": "..."}
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        uid = request.data.get('uid')
        new_password = serializer.validated_data['password1']
        
        try:
            # Decodificar UID y obtener usuario
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
            
            # Verificar token
            if default_token_generator.check_token(user, token):
                # Cambiar clave de acceso
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Clave de acceso restablecida exitosamente.'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Token inválido o expirado.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Token o ID de usuario inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ===== LOGOUT JWT (Opcional - con blacklist) =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/logout/
    Invalida refresh token (blacklist)
    Body: {"refresh": "..."}
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logout exitoso.'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Error al hacer logout.',
            'details': str(e) if settings.DEBUG else None
        }, status=status.HTTP_400_BAD_REQUEST)
