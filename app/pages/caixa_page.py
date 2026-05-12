"""Caixa: filtro por pet, carrinho e finalização de venda."""

from __future__ import annotations

from datetime import datetime, timezone

import flet as ft

from app.components.dialogs import informar, snack
from app.services import pets_service, racoes_service, vendas_service


def _fmt_preco(v: float) -> str:
    return f"R$ {v:.2f}"


def _fmt_data_hora(iso: str) -> str:
    try:
        s = (iso or "").replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError, OSError):
        return iso or "—"


def build_view(page: ft.Page) -> ft.Control:
    pet_dd = ft.Dropdown(label="Tipo de pet", width=400, options=[])
    racao_dd = ft.Dropdown(label="Ração", width=400, options=[], disabled=True)
    qtd_field = ft.TextField(label="Quantidade", width=160, hint_text="1")
    carrinho_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    historico_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: R$ 0.00", style=ft.TextThemeStyle.TITLE_MEDIUM)

    # carrinho: racao_id -> {nome, preco_unit, quantidade}
    carrinho: dict[str, dict] = {}

    def opcoes_pets():
        pets = pets_service.listar()
        pet_dd.options = [
            ft.dropdown.Option(key=pid, text=p.get("nome", ""))
            for p in pets
            if (pid := p.get("id"))
        ]
        if not pets:
            pet_dd.value = None
        elif not pet_dd.value or not any(
            p.get("id") == pet_dd.value for p in pets if p.get("id")
        ):
            first_id = pets[0].get("id")
            pet_dd.value = first_id if first_id else None

    def atualizar_racoes_dropdown():
        pid = pet_dd.value
        if not pid:
            racao_dd.options = []
            racao_dd.value = None
            racao_dd.disabled = True
            return
        racoes = racoes_service.listar_por_pet(pid)
        racao_dd.options = [
            ft.dropdown.Option(
                key=rid,
                text=f"{r.get('nome', '')} — estq. {r.get('quantidade', 0)}",
            )
            for r in racoes
            if (rid := r.get("id"))
        ]
        racao_dd.disabled = len(racao_dd.options) == 0
        if racao_dd.options:
            racao_dd.value = racao_dd.options[0].key
        else:
            racao_dd.value = None

    def render_carrinho():
        carrinho_col.controls.clear()
        total = 0.0
        for rid, it in carrinho.items():
            sub = round(it["preco_unit"] * it["quantidade"], 2)
            total += sub
            carrinho_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(it["nome"], weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        f"{it['quantidade']} x {_fmt_preco(it['preco_unit'])} = {_fmt_preco(sub)}",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                tooltip="Remover",
                                on_click=lambda e, i=rid: remover_item(i),
                            ),
                        ]
                    ),
                    padding=8,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=4,
                )
            )
        total_text.value = f"Total: {_fmt_preco(round(total, 2))}"
        page.update()

    def remover_item(rid: str):
        carrinho.pop(rid, None)
        render_carrinho()

    def limpar_carrinho():
        carrinho.clear()
        render_carrinho()

    def render_historico():
        historico_col.controls.clear()
        vendas = sorted(
            vendas_service.listar(),
            key=lambda v: str(v.get("data_hora", "")),
            reverse=True,
        )
        if not vendas:
            historico_col.controls.append(
                ft.Text(
                    "Nenhuma venda registrada ainda.",
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    size=13,
                )
            )
        else:
            for v in vendas:
                dh = _fmt_data_hora(str(v.get("data_hora", "")))
                total_v = float(v.get("total", 0))
                linhas_itens = []
                for it in v.get("itens") or []:
                    nome = str(it.get("nome", ""))
                    q = int(it.get("quantidade", 0))
                    sub = float(it.get("subtotal", 0))
                    linhas_itens.append(f"{nome} ×{q} — {_fmt_preco(sub)}")
                detalhe = "  ·  ".join(linhas_itens) if linhas_itens else "—"
                historico_col.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            dh,
                                            weight=ft.FontWeight.W_500,
                                            expand=True,
                                        ),
                                        ft.Text(
                                            _fmt_preco(total_v),
                                            weight=ft.FontWeight.W_600,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                ft.Text(
                                    detalhe,
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=4,
                    )
                )

    def adicionar_item(_):
        rid = racao_dd.value
        if not rid:
            snack(page, "Selecione uma ração.", erro=True)
            return
        r = racoes_service.obter(rid)
        if not r:
            snack(page, "Ração não encontrada.", erro=True)
            return
        try:
            q = int((qtd_field.value or "1").strip())
        except ValueError:
            snack(page, "Quantidade inválida.", erro=True)
            return
        if q <= 0:
            snack(page, "Quantidade deve ser maior que zero.", erro=True)
            return
        preco = float(r.get("preco", 0))
        nome = str(r.get("nome", ""))
        if rid in carrinho:
            carrinho[rid]["quantidade"] += q
        else:
            carrinho[rid] = {"nome": nome, "preco_unit": preco, "quantidade": q}
        render_carrinho()
        snack(page, "Item adicionado ao carrinho.")

    def finalizar(_):
        if not carrinho:
            informar(
                page,
                titulo="Carrinho vazio",
                mensagem="Adicione ao menos um item à venda antes de finalizar.",
            )
            return
        itens = [
            {"racao_id": rid, "quantidade": it["quantidade"]}
            for rid, it in carrinho.items()
        ]
        ok, msg = vendas_service.registrar_venda(itens)
        if ok:
            limpar_carrinho()
            opcoes_pets()
            atualizar_racoes_dropdown()
            render_historico()
            snack(page, msg)
        else:
            informar(
                page,
                titulo="Venda não realizada",
                mensagem=msg,
            )

    def on_pet_change(_):
        atualizar_racoes_dropdown()
        page.update()

    opcoes_pets()
    atualizar_racoes_dropdown()
    pet_dd.on_change = on_pet_change
    render_historico()

    return ft.Column(
        [
            ft.Text("Caixa / Vendas", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Text(
                "Selecione o tipo de pet para ver rações compatíveis, monte o carrinho e finalize.",
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            ft.Row([pet_dd], wrap=True),
            ft.Row(
                [
                    racao_dd,
                    qtd_field,
                    ft.FilledButton("Adicionar à venda", on_click=adicionar_item),
                ],
                spacing=12,
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Divider(),
            ft.Text("Carrinho", style=ft.TextThemeStyle.TITLE_SMALL),
            carrinho_col,
            ft.Row(
                [
                    total_text,
                    ft.FilledButton(
                        "Finalizar venda",
                        icon=ft.Icons.POINT_OF_SALE,
                        on_click=finalizar,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(),
            ft.Text("Histórico de vendas", style=ft.TextThemeStyle.TITLE_SMALL),
            ft.Container(
                content=historico_col,
                height=280,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=4,
                padding=8,
            ),
        ],
        expand=True,
        spacing=12,
    )
