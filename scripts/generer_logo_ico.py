from pathlib import Path
from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent
ASSETS = RACINE / "assets"
PNG = ASSETS / "logo.png"
ICO = ASSETS / "logo.ico"

COULEUR_FOND = (3, 11, 53, 255)
COULEUR_ACCENT = (192, 182, 36, 255)


def _icone_par_defaut(taille: int = 256) -> Image.Image:
    img = Image.new("RGBA", (taille, taille), COULEUR_FOND)
    draw = ImageDraw.Draw(img)
    m = taille // 8
    draw.ellipse([m, m, taille - m, taille - m], outline=COULEUR_ACCENT, width=max(4, taille // 32))
    s = taille // 4
    draw.rectangle([taille // 2 - s, taille // 2, taille // 2 + s, taille - m], fill=COULEUR_ACCENT)
    draw.arc(
        [taille // 2 - s, taille // 4, taille // 2 + s, taille // 2 + s // 2],
        start=180,
        end=0,
        fill=COULEUR_ACCENT,
        width=max(4, taille // 24),
    )
    return img

def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    if PNG.is_file():
        img = Image.open(PNG).convert("RGBA")
    else:
        img = _icone_par_defaut()
    tailles = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICO, format="ICO", sizes=tailles)


if __name__ == "__main__":
    main()
