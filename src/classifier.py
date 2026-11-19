from pathlib import Path


class LogoClassifier:
    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path
        self.classes = [
            "VW",
            "Mercedes",
            "BMW",
            "Audi",
            "Seat",
            "Opel",
            "Sonstige / Kein Logo",
        ]
        # TODO: Hier später das trainierte EfficientNet-Modell laden

    def predict(self, image_path: Path) -> tuple[str, int]:
        """
        Wertet das Bild aus und gibt (ErkannteMarke, Konfidenz_in_Prozent) zurück.
        """
        # TODO: Letterboxing auf 512x512 anwenden & Inferenz ausführen
        print(f"   -> Analysiere Bild: {image_path.name}")
        return "Audi", 96