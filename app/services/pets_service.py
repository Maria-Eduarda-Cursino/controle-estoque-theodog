"""CRUD de tipos de pet (pets.json)."""

from __future__ import annotations

import uuid
from typing import Any

from app.services.json_store import read_json, write_json_atomic

_FILE = "pets.json"


def listar() -> list[dict[str, Any]]:
    raw = read_json(_FILE, [])
    if not isinstance(raw, list):
        write_json_atomic(_FILE, [])
        return []

    limpos: list[dict[str, Any]] = []
    descartado = False
    for item in raw:
        if not isinstance(item, dict):
            descartado = True
            continue
        pid = item.get("id")
        nome_str = str(item.get("nome", "") or "").strip()
        if not pid or not nome_str:
            descartado = True
            continue
        limpos.append({"id": str(pid), "nome": nome_str})

    if descartado or len(limpos) != len(raw):
        write_json_atomic(_FILE, limpos)

    return limpos


def adicionar(nome: str) -> dict[str, Any] | None:
    nome = (nome or "").strip()
    if not nome:
        return None
    pets = listar()
    pet = {"id": str(uuid.uuid4()), "nome": nome}
    pets.append(pet)
    write_json_atomic(_FILE, pets)
    return pet


def atualizar(pet_id: str, nome: str) -> bool:
    nome = (nome or "").strip()
    if not nome:
        return False
    pets = listar()
    for p in pets:
        if p.get("id") == pet_id:
            p["nome"] = nome
            write_json_atomic(_FILE, pets)
            return True
    return False


def remover(pet_id: str) -> bool:
    pets = listar()
    nova = [p for p in pets if p.get("id") != pet_id]
    if len(nova) == len(pets):
        return False
    write_json_atomic(_FILE, nova)
    return True


def obter(pet_id: str) -> dict[str, Any] | None:
    for p in listar():
        if p.get("id") == pet_id:
            return p
    return None
