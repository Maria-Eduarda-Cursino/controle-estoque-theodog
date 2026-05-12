"""Shell Flet Theodog: navegação e tema."""

from __future__ import annotations

import flet as ft

from app.pages.caixa_page import build_view as build_caixa
from app.pages.pets_page import build_view as build_pets
from app.pages.racoes_page import build_view as build_racoes


def main(page: ft.Page) -> None:
    page.title = "Theodog — Estoque e Caixa"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START

    holder = ft.Column(expand=True, spacing=0)

    def mostrar(indice: int):
        holder.controls.clear()
        if indice == 0:
            holder.controls.append(build_pets(page))
        elif indice == 1:
            holder.controls.append(build_racoes(page))
        else:
            holder.controls.append(build_caixa(page))
        page.update()

    def on_nav(e):
        mostrar(e.control.selected_index)

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        leading=ft.Container(
            content=ft.Icon(ft.Icons.PETS),
            padding=ft.padding.only(top=8, bottom=4),
            tooltip="Theodog",
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CATEGORY_OUTLINED,
                selected_icon=ft.Icons.CATEGORY,
                label="Tipos de pet",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                selected_icon=ft.Icons.INVENTORY_2,
                label="Rações",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.POINT_OF_SALE_OUTLINED,
                selected_icon=ft.Icons.POINT_OF_SALE,
                label="Caixa",
            ),
        ],
        on_change=on_nav,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )

    mostrar(0)

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=holder, expand=True, padding=20),
            ],
            expand=True,
        )
    )


def run_app() -> None:
    ft.app(target=main)
