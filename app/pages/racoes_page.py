"""Cadastro de rações."""

from __future__ import annotations

import flet as ft

from app.components.dialogs import confirmar, informar, snack
from app.services import pets_service, racoes_service


def _fmt_preco(v: float) -> str:
    return f"R$ {v:.2f}"


def build_view(page: ft.Page) -> ft.Control:
    lista = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)

    nome = ft.TextField(label="Nome da ração", expand=True)
    marca = ft.TextField(label="Marca", expand=True)
    preco = ft.TextField(label="Preço", hint_text="Ex.: 49.90", expand=True)
    qtd = ft.TextField(label="Quantidade em estoque", hint_text="0", expand=True)
    pet_dd = ft.Dropdown(
        label="Tipo de pet",
        expand=True,
        options=[],
    )

    def opcoes_pets():
        pet_dd.options = [
            ft.dropdown.Option(key=pid, text=p.get("nome", ""))
            for p in pets_service.listar()
            if (pid := p.get("id"))
        ]
        if not pet_dd.options:
            pet_dd.value = None
        elif not pet_dd.value or not any(
            o.key == pet_dd.value for o in pet_dd.options
        ):
            pet_dd.value = pet_dd.options[0].key

    def parse_int(s: str) -> int | None:
        try:
            v = int((s or "").strip())
            if v < 0:
                return None
            return v
        except ValueError:
            return None

    def parse_float(s: str) -> float | None:
        try:
            t = (s or "").strip().replace(",", ".")
            v = float(t)
            if v < 0:
                return None
            return v
        except ValueError:
            return None

    def atualizar_lista():
        lista.controls.clear()
        pets = {
            pid: p.get("nome", "?")
            for p in pets_service.listar()
            if (pid := p.get("id"))
        }
        for r in racoes_service.listar():
            rid = r.get("id")
            if not rid:
                continue
            pet_nome = pets.get(r.get("pet_tipo_id", ""), "—")
            lista.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{r.get('nome', '')} — {r.get('marca', '')}",
                                        weight=ft.FontWeight.W_600,
                                        expand=True,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        tooltip="Editar",
                                        on_click=lambda e, item=r: abrir_edicao(item),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="Excluir",
                                        on_click=lambda e, i=rid: solicitar_exclusao(i),
                                    ),
                                ]
                            ),
                            ft.Text(
                                f"Preço: {_fmt_preco(float(r.get('preco', 0)))}  |  "
                                f"Estoque: {r.get('quantidade', 0)}  |  Pet: {pet_nome}",
                                size=13,
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

    def limpar_form():
        nome.value = ""
        marca.value = ""
        preco.value = ""
        qtd.value = ""
        opcoes_pets()
        page.update()

    def coletar_form(racao_id: str | None = None) -> dict | None:
        opcoes_pets()
        pn = nome.value.strip()
        mar = marca.value.strip()
        pr = parse_float(preco.value)
        qt = parse_int(qtd.value)
        pid = pet_dd.value
        if not pn or not mar or pid is None or pr is None or qt is None:
            informar(
                page,
                titulo="Formulário incompleto",
                mensagem=(
                    "Preencha nome, marca, preço e quantidade em estoque com valores válidos "
                    "(preço e estoque não podem ser negativos) e selecione o tipo de pet."
                ),
            )
            return None
        return {
            "id": racao_id,
            "nome": pn,
            "marca": mar,
            "preco": pr,
            "quantidade": qt,
            "pet_tipo_id": pid,
        }

    modo_edicao: dict[str, str | None] = {"id": None}

    def abrir_edicao(item: dict):
        modo_edicao["id"] = item.get("id")
        nome.value = item.get("nome", "")
        marca.value = item.get("marca", "")
        preco.value = str(item.get("preco", ""))
        qtd.value = str(item.get("quantidade", ""))
        opcoes_pets()
        pet_dd.value = item.get("pet_tipo_id")
        btn_salvar.text = "Atualizar ração"
        btn_cancel.text = "Cancelar edição"
        page.update()

    def salvar(_):
        rid = modo_edicao["id"]
        data = coletar_form(rid)
        if not data:
            return
        if rid:
            ok = racoes_service.atualizar(
                rid,
                data["nome"],
                data["marca"],
                data["preco"],
                data["quantidade"],
                data["pet_tipo_id"],
            )
            if ok:
                modo_edicao["id"] = None
                btn_salvar.text = "Cadastrar ração"
                btn_cancel.text = "Cancelar cadastro"
                limpar_form()
                atualizar_lista()
                snack(page, "Ração atualizada.")
            else:
                informar(
                    page,
                    titulo="Não foi possível atualizar",
                    mensagem="Verifique os dados e se a ração ainda existe na lista.",
                )
        else:
            c = racoes_service.adicionar(
                data["nome"],
                data["marca"],
                data["preco"],
                data["quantidade"],
                data["pet_tipo_id"],
            )
            if c:
                limpar_form()
                atualizar_lista()
                snack(page, "Ração cadastrada.")
            else:
                informar(
                    page,
                    titulo="Cadastro não realizado",
                    mensagem="Os dados não puderam ser salvos. Confira nome, marca, preço, estoque e tipo de pet.",
                )

    def cancelar_edicao(_):
        modo_edicao["id"] = None
        btn_salvar.text = "Cadastrar ração"
        btn_cancel.text = "Cancelar cadastro"
        limpar_form()
        atualizar_lista()

    def solicitar_exclusao(racao_id: str):
        def excluir():
            if racoes_service.remover(racao_id):
                atualizar_lista()
                snack(page, "Ração removida.")
            else:
                informar(
                    page,
                    titulo="Não foi possível excluir",
                    mensagem="A ração não pôde ser removida. Tente novamente.",
                )

        confirmar(
            page,
            titulo="Excluir ração",
            mensagem="Deseja realmente excluir esta ração?",
            rotulo_confirmar="Excluir",
            ao_confirmar=excluir,
        )

    btn_salvar = ft.FilledButton("Cadastrar ração", on_click=salvar)
    btn_cancel = ft.OutlinedButton("Cancelar cadastro", on_click=cancelar_edicao)

    opcoes_pets()
    atualizar_lista()

    return ft.Column(
        [
            ft.Text("Rações", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.ResponsiveRow(
                [
                    ft.Container(nome, col={"sm": 12, "md": 6}),
                    ft.Container(marca, col={"sm": 12, "md": 6}),
                    ft.Container(preco, col={"sm": 12, "md": 4}),
                    ft.Container(qtd, col={"sm": 12, "md": 4}),
                    ft.Container(pet_dd, col={"sm": 12, "md": 4}),
                ],
                run_spacing=8,
            ),
            ft.Row([btn_salvar, btn_cancel], spacing=8),
            ft.Divider(),
            lista,
        ],
        expand=True,
        spacing=12,
    )
