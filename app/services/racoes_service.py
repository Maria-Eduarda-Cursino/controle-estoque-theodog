"""CRUD de rações e leitura para o caixa (racoes.json)."""

from __future__ import annotations

import uuid
from typing import Any

from app.services.json_store import read_json, write_json_atomic

_FILE = "racoes.json"


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
        rid = item.get("id")
        nome = str(item.get("nome", "") or "").strip()
        marca = str(item.get("marca", "") or "").strip()
        pet_tid = item.get("pet_tipo_id")
        if not rid or not nome or not marca or not pet_tid:
            descartado = True
            continue
        try:
            preco = float(item.get("preco", 0))
            qtd = int(item.get("quantidade", 0))
        except (TypeError, ValueError):
            descartado = True
            continue
        if preco < 0 or qtd < 0:
            descartado = True
            continue
        limpos.append(
            {
                "id": str(rid),
                "nome": nome,
                "marca": marca,
                "preco": preco,
                "quantidade": qtd,
                "pet_tipo_id": str(pet_tid),
            }
        )

    if descartado or len(limpos) != len(raw):
        write_json_atomic(_FILE, limpos)

    return limpos


def listar_por_pet(pet_tipo_id: str) -> list[dict[str, Any]]:
    return [r for r in listar() if r.get("pet_tipo_id") == pet_tipo_id]


def obter(racao_id: str) -> dict[str, Any] | None:
    for r in listar():
        if r.get("id") == racao_id:
            return r
    return None


def adicionar(
    nome: str,
    marca: str,
    preco: float,
    quantidade: int,
    pet_tipo_id: str,
) -> dict[str, Any] | None:
    nome = (nome or "").strip()
    marca = (marca or "").strip()
    if not nome or not marca or not pet_tipo_id:
        return None
    if preco < 0 or quantidade < 0:
        return None
    racoes = listar()
    item = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "marca": marca,
        "preco": float(preco),
        "quantidade": int(quantidade),
        "pet_tipo_id": pet_tipo_id,
    }
    racoes.append(item)
    write_json_atomic(_FILE, racoes)
    return item


def atualizar(
    racao_id: str,
    nome: str,
    marca: str,
    preco: float,
    quantidade: int,
    pet_tipo_id: str,
) -> bool:
    nome = (nome or "").strip()
    marca = (marca or "").strip()
    if not nome or not marca or not pet_tipo_id:
        return False
    if preco < 0 or quantidade < 0:
        return False
    racoes = listar()
    for r in racoes:
        if r.get("id") == racao_id:
            r["nome"] = nome
            r["marca"] = marca
            r["preco"] = float(preco)
            r["quantidade"] = int(quantidade)
            r["pet_tipo_id"] = pet_tipo_id
            write_json_atomic(_FILE, racoes)
            return True
    return False


def atualizar_estoque(racao_id: str, quantidade: int) -> bool:
    racoes = listar()
    for r in racoes:
        if r.get("id") == racao_id:
            r["quantidade"] = int(quantidade)
            write_json_atomic(_FILE, racoes)
            return True
    return False


def remover(racao_id: str) -> bool:
    racoes = listar()
    nova = [r for r in racoes if r.get("id") != racao_id]
    if len(nova) == len(racoes):
        return False
    write_json_atomic(_FILE, nova)
    return True


def substituir_todas(racoes: list[dict[str, Any]]) -> None:
    write_json_atomic(_FILE, racoes)
