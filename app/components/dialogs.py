"""Diálogos e feedback simples."""

from __future__ import annotations

import flet as ft


def snack(page: ft.Page, message: str, *, erro: bool = False) -> None:
    page.snack_bar = ft.SnackBar(
        ft.Text(message),
        bgcolor=ft.Colors.RED_700 if erro else ft.Colors.GREEN_700,
    )
    page.snack_bar.open = True
    page.update()


def informar(
    page: ft.Page,
    *,
    titulo: str,
    mensagem: str,
    rotulo_ok: str = "Entendi",
) -> None:
    """Diálogo simples (um botão) para avisos de regra de negócio ou bloqueios."""

    def fechar(_):
        page.close(dlg)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo),
        content=ft.Text(mensagem),
        actions=[ft.FilledButton(rotulo_ok, on_click=fechar)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.open(dlg)


def confirmar(
    page: ft.Page,
    *,
    titulo: str,
    mensagem: str,
    rotulo_confirmar: str = "Confirmar",
    ao_confirmar,
) -> None:
    def fechar(_):
        page.close(dlg)

    def ok(_):
        page.close(dlg)
        ao_confirmar()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo),
        content=ft.Text(mensagem),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.TextButton(rotulo_confirmar, on_click=ok),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.open(dlg)


def editar_texto(
    page: ft.Page,
    *,
    titulo: str,
    label: str,
    valor_inicial: str,
    ao_salvar,
) -> None:
    campo = ft.TextField(label=label, value=valor_inicial, autofocus=True)

    def fechar(_):
        page.close(dlg)

    def salvar(_):
        page.close(dlg)
        ao_salvar(campo.value)

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo),
        content=campo,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.FilledButton("Salvar", on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.open(dlg)
