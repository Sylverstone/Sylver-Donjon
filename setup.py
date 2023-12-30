import sys
from cx_Freeze import setup, Executable

# Define the executables
executables = [Executable("SylverDonjon.py", base=None)]


build_options = {
    "packages": ["pygame","random","os","json","cryptography","sys","dotenv","email","ssl","smtplib"],
    "include_files": [
        ("dossier_police", "dossier_police"),
        ("image_site", "image_site"),
        ("playlist_music", "playlist_music"),
        ("file","file"),
        ("key","key"),
        (".env",".env"),
        
    ],
}

# Set up the setup function
setup(
    name="SylverDonjon",
    version='5.6',
    options={"build_exe": build_options},
    author = "by Sylvio Pelage-Maxime",
    executables=executables,
)