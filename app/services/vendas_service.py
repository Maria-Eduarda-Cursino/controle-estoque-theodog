"""Registro de vendas e atualização de estoque (vendas.json + racoes.json).

Não há transação atômica entre os dois arquivos: em uso local o risco é aceitável
para este MVP. Ordem: valida tudo, grava rações, depois vendas.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from app.services import racoes_service
from app.services.json_store import read_json, write_json_atomic

_FILE = "vendas.json"


def listar() -> list[dict[str, Any]]:
    return read_json(_FILE, [])


def _agregar_itens(
    itens: list[dict[str, Any]],
) -> dict[str, int]:
    totais: dict[str, int] = defaultdict(int)
    for it in itens:
        rid = it.get("racao_id")
        q = int(it.get("quantidade", 0))
        if not rid or q <= 0:
            raise ValueError("Cada item precisa de racao_id e quantidade maior que zero.")
        totais[rid] += q
    return dict(totais)


def registrar_venda(itens: list[dict[str, Any]]) -> tuple[bool, str]:
    """
    itens: [{"racao_id": str, "quantidade": int}, ...]
    """
    if not itens:
        return False, "Adicione ao menos um item à venda."

    try:
        needed = _agregar_itens(itens)
    except ValueError as e:
        return False, str(e)

    racoes = racoes_service.listar()
    by_id = {r["id"]: r for r in racoes if "id" in r}

    linhas: list[dict[str, Any]] = []
    for rid, qtd_pedido in needed.items():
        r = by_id.get(rid)
        if not r:
            return False, f"Ração não encontrada: {rid}"
        est = int(r.get("quantidade", 0))
        if est < qtd_pedido:
            return False, (
                f"Estoque insuficiente para '{r.get('nome', rid)}'. "
                f"Disponível: {est}, pedido: {qtd_pedido}."
            )
        preco = float(r.get("preco", 0))
        subtotal = round(preco * qtd_pedido, 2)
        linhas.append(
            {
                "racao_id": rid,
                "nome": r.get("nome", ""),
                "quantidade": qtd_pedido,
                "preco_unitario": preco,
                "subtotal": subtotal,
            }
        )

    total = round(sum(L["subtotal"] for L in linhas), 2)

    for rid, qtd_pedido in needed.items():
        r = by_id[rid]
        r["quantidade"] = int(r["quantidade"]) - qtd_pedido

    racoes_service.substituir_todas(racoes)

    venda = {
        "id": str(uuid.uuid4()),
        "data_hora": datetime.now(timezone.utc).isoformat(),
        "itens": linhas,
        "total": total,
    }
    vendas = listar()
    vendas.append(venda)
    write_json_atomic(_FILE, vendas)
    return True, "Venda registrada."
