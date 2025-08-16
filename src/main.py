import flet as ft
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import AgeRestrictedError, VideoUnavailable, RegexMatchError, LiveStreamError
import os
import asyncio

# Callback para atualizar o progresso na UI
def on_progress_callback_ft(stream, chunk, bytes_remaining, page, status_text, progress_bar):
    """Callback para atualizar o progresso no Flet UI."""
    try:
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100

        progress_bar.value = percentage_of_completion / 100
        status_text.value = f"Baixando: {stream.title} ({percentage_of_completion:.1f}%)"
        page.update()
    except Exception as e:
        # Apenas para depuração, não afeta o usuário
        print(f"Erro no callback de progresso: {e}")

# Callback para finalizar o download
def on_complete_callback_ft(stream, file_path, page, status_text, progress_bar):
    """Callback para sinalizar o fim do download."""
    status_text.value = "✅ Download concluído!"
    progress_bar.value = 1.0
    page.snack_bar = ft.SnackBar(ft.Text("Download concluído com sucesso!"))
    page.snack_bar.open = True
    page.update()

async def video_download_task(url, qualidade, page, status_text, progress_bar, save_path):
    """Função de download de vídeo, executada em uma tarefa assíncrona."""
    try:
        yt = YouTube(
            url,
            on_progress_callback=lambda stream, chunk, bytes_remaining: on_progress_callback_ft(stream, chunk, bytes_remaining, page, status_text, progress_bar),
            on_complete_callback=lambda stream, file_path: on_complete_callback_ft(stream, file_path, page, status_text, progress_bar)
        )
        status_text.value = f"Iniciando download de: {yt.title}"
        page.update()

        stream = yt.streams.filter(res=qualidade).first()

        if not stream:
            stream = yt.streams.get_highest_resolution()
            if not stream:
                raise ValueError(f"Não foi possível encontrar a resolução de vídeo para {yt.title}.")
            status_text.value = f"Qualidade {qualidade} não disponível. Baixando a mais alta resolução disponível ({stream.resolution})."
            page.update()
        
        await asyncio.to_thread(stream.download, output_path=save_path)
    
    except (AgeRestrictedError, VideoUnavailable, LiveStreamError, RegexMatchError) as e:
        error_message = f"Erro no download: {type(e).__name__}. Verifique se a URL é válida ou se o vídeo está disponível."
        status_text.value = error_message
        page.snack_bar = ft.SnackBar(ft.Text(error_message))
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        error_message = f"Ocorreu um erro inesperado: {str(e)}"
        status_text.value = error_message
        page.snack_bar = ft.SnackBar(ft.Text(error_message))
        page.snack_bar.open = True
        page.update()

async def audio_download_task(url, modo, page, status_text, progress_bar, save_path):
    """Função de download de áudio, executada em uma tarefa assíncrona."""
    try:
        if modo == "playlist":
            pl = Playlist(url)
            status_text.value = f"Iniciando download da playlist: {pl.title}"
            page.update()
            
            for i, v in enumerate(pl.videos):
                try:
                    # Limpar a barra de progresso para cada vídeo
                    progress_bar.value = 0
                    page.update()
                    
                    yt = YouTube(
                        v.watch_url,
                        on_progress_callback=lambda stream, chunk, bytes_remaining: on_progress_callback_ft(stream, chunk, bytes_remaining, page, status_text, progress_bar),
                        on_complete_callback=lambda stream, file_path: on_complete_callback_ft(stream, file_path, page, status_text, progress_bar)
                    )
                    status_text.value = f"Baixando áudio {i+1}/{len(pl.videos)}: {yt.title}"
                    page.update()

                    ys = yt.streams.get_audio_only()
                    if ys:
                        await asyncio.to_thread(ys.download, output_path=save_path)
                    else:
                        raise ValueError(f"Áudio não encontrado para o vídeo: {yt.title}")
                except Exception as e:
                    print(f"Erro ao baixar {v.title}: {e}")
                    status_text.value = f"Falha no download de um vídeo da playlist: {v.title}"
                    page.snack_bar = ft.SnackBar(ft.Text(status_text.value))
                    page.snack_bar.open = True
                    page.update()
            
            status_text.value = "✅ Download da playlist concluído!"
            progress_bar.value = 1.0
            page.snack_bar = ft.SnackBar(ft.Text(status_text.value))
            page.snack_bar.open = True
            page.update()
            
        else: # modo == "unico"
            yt = YouTube(
                url,
                on_progress_callback=lambda stream, chunk, bytes_remaining: on_progress_callback_ft(stream, chunk, bytes_remaining, page, status_text, progress_bar),
                on_complete_callback=lambda stream, file_path: on_complete_callback_ft(stream, file_path, page, status_text, progress_bar)
            )
            status_text.value = f"Iniciando download de: {yt.title}"
            page.update()
            ys = yt.streams.get_audio_only()
            if ys:
                await asyncio.to_thread(ys.download, output_path=save_path)
            else:
                raise ValueError("Áudio não encontrado para a URL.")
    
    except (AgeRestrictedError, VideoUnavailable, LiveStreamError, RegexMatchError) as e:
        error_message = f"Erro no download: {type(e).__name__}. Verifique se a URL é válida ou se o vídeo está disponível."
        status_text.value = error_message
        page.snack_bar = ft.SnackBar(ft.Text(error_message))
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        error_message = f"Ocorreu um erro inesperado: {str(e)}"
        status_text.value = error_message
        page.snack_bar = ft.SnackBar(ft.Text(error_message))
        page.snack_bar.open = True
        page.update()

def main(page: ft.Page):
    page.title = "🎵 Youtube Downloader"
    page.scroll = "adaptive"
    page.theme_mode = "dark"
    page.bgcolor = "#121212"

    title = ft.Text("🎵 Youtube Download", size=32, weight="bold", color="#e53935")
    title_row = ft.Row([title], alignment=ft.MainAxisAlignment.CENTER)

    url_input = ft.TextField(
        label="Insira a URL do vídeo ou playlist",
        width=500,
        border_radius=15,
        bgcolor="#1e1e1e",
        border_color="#e53935",
        color="white",
    )

    audio_options = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="unico", label="🎧 Único"),
                ft.Radio(value="playlist", label="📂 Playlist"),
            ],
            spacing=10,
        ),
        value="unico",
    )

    video_options = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="1080p", label="📺 1080p"),
                ft.Radio(value="720p", label="🎬 720p"),
            ],
            spacing=10,
        ),
        value="1080p",
    )

    status_text = ft.Text("Pronto para baixar!", size=16, color="#e0e0e0")
    progress_bar = ft.ProgressBar(width=500, color="#e53935", bgcolor="#1e1e1e", value=0)

    content = ft.Column([], alignment=ft.MainAxisAlignment.CENTER)

    def make_tab(text):
        return ft.ElevatedButton(
            text,
            style=ft.ButtonStyle(
                bgcolor={"": "#1e1e1e"},
                color={"": "#ffffff"},
                overlay_color="#e53935",
                shape=ft.RoundedRectangleBorder(radius=12),
                text_style=ft.TextStyle(size=18, weight="bold"),
            ),
            on_click=change_tab,
        )

    def change_tab(e):
        tab = e.control.text
        if tab == "Audio":
            content.controls.clear()
            content.controls.append(
                ft.Card(
                    content=ft.Container(content=audio_options, padding=20),
                    elevation=2,
                    color="#1e1e1e",
                )
            )
        else:
            content.controls.clear()
            content.controls.append(
                ft.Card(
                    content=ft.Container(content=video_options, padding=20),
                    elevation=2,
                    color="#1e1e1e",
                )
            )
        page.update()

    tabs_row = ft.Row(
        [
            make_tab("Audio"),
            make_tab("Video"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=30,
    )
    
    file_picker = ft.FilePicker()
    
    async def on_dialog_result(e: ft.FilePickerResultEvent):
        if not e.path:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Nenhuma pasta selecionada!"))
            page.snack_bar.open = True
            page.update()
            return

        url = url_input.value.strip()
        
        status_text.value = "Iniciando..."
        progress_bar.value = 0
        page.update()
        
        if content.controls and isinstance(content.controls[0].content, ft.RadioGroup):
            group = content.controls[0].content
            escolha = group.value

            if group == audio_options:
                await audio_download_task(url, modo=escolha, page=page, status_text=status_text, progress_bar=progress_bar, save_path=e.path)
            else:
                await video_download_task(url, qualidade=escolha, page=page, status_text=status_text, progress_bar=progress_bar, save_path=e.path)

    async def baixar(e):
        url = url_input.value.strip()
        if not url:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Insira uma URL!"))
            page.snack_bar.open = True
            page.update()
            return
        
        file_picker.on_result = on_dialog_result
        await file_picker.get_directory_path_async()

    btn_baixar = ft.ElevatedButton(
        "⬇️ Baixar",
        on_click=baixar,
        style=ft.ButtonStyle(
            bgcolor={"": "#e53935"},
            color={"": "white"},
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=20,
            text_style=ft.TextStyle(size=20, weight="bold"),
        ),
    )

    page.add(
        ft.Column(
            [
                title_row,
                ft.Container(content=url_input, padding=20, border_radius=15),
                tabs_row,
                ft.Container(content=content, padding=10, expand=True),
                ft.Column(
                    [
                        status_text,
                        progress_bar
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row([btn_baixar], alignment=ft.MainAxisAlignment.CENTER),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
        )
    )

    content.controls.append(
        ft.Card(
            content=ft.Container(content=audio_options, padding=20),
            elevation=2,
            color="#1e1e1e",
        )
    )
    
    page.overlay.append(file_picker)
    page.update()
