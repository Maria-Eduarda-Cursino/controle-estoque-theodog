"""Cadastro de tipos de pet."""

from __future__ import annotations

import flet as ft

from app.components.dialogs import confirmar, editar_texto, informar, snack
from app.services import pets_service, racoes_service


def build_view(page: ft.Page) -> ft.Control:
    lista = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
    nome = ft.TextField(
        label="Nome do tipo de pet",
        hint_text="Ex.: Cachorro - Pequeno, Gato",
        expand=True,
    )

    def atualizar_lista():
        lista.controls.clear()
        for p in pets_service.listar():
            pid = p.get("id")
            if not pid:
                continue
            lista.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(p.get("nome", ""), expand=True),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar",
                                on_click=lambda e, i=pid, n=p.get("nome", ""): abrir_edicao(
                                    i, n
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Excluir",
                                on_click=lambda e, i=pid: solicitar_exclusao(i),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=4,
                )
            )

    def abrir_edicao(pet_id: str, nome_atual: str):
        def salvar(novo: str):
            if pets_service.atualizar(pet_id, novo):
                atualizar_lista()
                snack(page, "Tipo de pet atualizado.")
            else:
                informar(
                    page,
                    titulo="Não foi possível salvar",
                    mensagem="Informe um nome válido (não vazio) para o tipo de pet.",
                )

        editar_texto(
            page,
            titulo="Editar tipo de pet",
            label="Nome",
            valor_inicial=nome_atual,
            ao_salvar=salvar,
        )

    def solicitar_exclusao(pet_id: str):
        if any(
            r.get("pet_tipo_id") == pet_id for r in racoes_service.listar()
        ):
            informar(
                page,
                titulo="Exclusão não permitida",
                mensagem=(
                    "Este tipo de pet não pode ser excluído porque já existe "
                    "pelo menos uma ração cadastrada para ele. "
                    "Remova ou altere essas rações antes de excluir o tipo."
                ),
            )
            return

        def excluir():
            if pets_service.remover(pet_id):
                atualizar_lista()
                snack(page, "Tipo de pet removido.")
            else:
                informar(
                    page,
                    titulo="Não foi possível excluir",
                    mensagem="O registro não pôde ser removido. Tente novamente.",
                )

        confirmar(
            page,
            titulo="Excluir tipo de pet",
            mensagem="Deseja realmente excluir este registro?",
            rotulo_confirmar="Excluir",
            ao_confirmar=excluir,
        )

    def adicionar(_):
        criado = pets_service.adicionar(nome.value)
        if criado:
            nome.value = ""
            atualizar_lista()
            snack(page, "Tipo de pet cadastrado.")
        else:
            informar(
                page,
                titulo="Nome obrigatório",
                mensagem="Digite um nome para o tipo de pet antes de adicionar.",
            )

    atualizar_lista()

    return ft.Column(
        [
            ft.Text("Tipos de pet", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Row(
                [nome, ft.FilledButton("Adicionar", on_click=adicionar)],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Divider(),
            lista,
        ],
        expand=True,
        spacing=12,
    )
