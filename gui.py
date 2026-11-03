import flet as ft

class Gui:
    def __init__(self,page: ft.Page):
        self.page = page
        self.idle_content = ft.Image(
                                src="images/idle_image.png",
                                expand=True,
                            )
        self.recognize_content = ft.Image(
                                src="images/recognize_image.png",
                                expand=True,
                            )
        self.play_content = ft.Image(
                                src="images/play_image.png",
                                expand=True,
                            )
        self.set_content(self.idle_content)
    def failed_content(self,text):
        return ft.Text(f"認識結果:{text}")
    def set_content(self,content):
        self.page.controls.clear()
        self.page.add(content)
        self.page.update()


