#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manejo de autenticación y sesiones"""

import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, redirect

# Almacenamiento de sesiones activas
active_sessions = {}

# Tiempo de expiración de sesión (5 minutos)
SESSION_TIMEOUT = 5 * 60  # segundos


def generate_token():
    """Genera un nuevo token único"""
    return str(uuid.uuid4())


def create_session():
    """Crea una nueva sesión con tiempo de expiración"""
    token = generate_token()
    now = datetime.now()
    active_sessions[token] = {"created_at": now, "expires_at": now + timedelta(seconds=SESSION_TIMEOUT)}
    return token


def validate_token(token):
    """Valida si un token existe y no ha expirado"""
    if not token or token not in active_sessions:
        return False

    session = active_sessions[token]
    if datetime.now() > session["expires_at"]:
        del active_sessions[token]
        return False

    # Actualizar tiempo de expiración
    session["expires_at"] = datetime.now() + timedelta(seconds=SESSION_TIMEOUT)
    return True


def cleanup_sessions():
    """Limpia las sesiones expiradas"""
    now = datetime.now()
    expired = [token for token, session in active_sessions.items() if now > session["expires_at"]]

    for token in expired:
        del active_sessions[token]


def require_auth(f):
    """Decorador para proteger rutas que requieren autenticación"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("auth_token")

        if not validate_token(token):
            return redirect("/")

        return f(*args, **kwargs)

    return decorated
