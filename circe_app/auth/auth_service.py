from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass

from circe_app.auth.database import get_connection

_PBKDF2_ITERATIONS = 200_000
_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


class AuthError(Exception):
    """Error de autenticación: usuario inválido, ya existente o credenciales incorrectas."""


@dataclass(frozen=True)
class User:
    id: int
    username: str


def _hash_password(password: str, salt: bytes) -> str:
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return derived.hex()


class AuthService:
    """Gestiona el registro e inicio de sesión de usuarios en la base de datos local."""

    def register(self, username: str, password: str) -> User:
        username = username.strip()
        if not _USERNAME_PATTERN.match(username):
            raise AuthError(
                "El usuario debe tener entre 3 y 32 caracteres (letras, números, '.', '_' o '-')."
            )
        if len(password) < 6:
            raise AuthError("La contraseña debe tener al menos 6 caracteres.")

        salt = os.urandom(16)
        password_hash = _hash_password(password, salt)

        connection = get_connection()
        try:
            try:
                cursor = connection.execute(
                    "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                    (username, password_hash, salt.hex(), time.time()),
                )
            except Exception as exc:
                if "UNIQUE" in str(exc).upper():
                    raise AuthError(f"El usuario '{username}' ya existe.") from exc
                raise
            connection.commit()
            return User(id=cursor.lastrowid, username=username)
        finally:
            connection.close()

    def login(self, username: str, password: str) -> User:
        username = username.strip()
        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            raise AuthError("Usuario o contraseña incorrectos.")

        salt = bytes.fromhex(row["salt"])
        if _hash_password(password, salt) != row["password_hash"]:
            raise AuthError("Usuario o contraseña incorrectos.")

        return User(id=row["id"], username=row["username"])
