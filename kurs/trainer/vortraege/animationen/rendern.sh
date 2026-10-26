#!/usr/bin/env bash
# Rendert eine Manim-Szene im offiziellen Docker-Image und legt das Video in ../public/videos ab.
#   ./rendern.sh vortrag1.py BigrammeZaehlen        volle Qualität (1080p, 60 Bilder/s)
#   ./rendern.sh vortrag1.py BigrammeZaehlen -ql    schnelle Vorschau
set -euo pipefail
cd "$(dirname "$0")"
datei=$1; szene=$2; qualitaet=${3:--qh}
docker run --rm --user "$(id -u):$(id -g)" -e XDG_CACHE_HOME=/tmp -v "$PWD:/manim:z" manimcommunity/manim:v0.22.0 \
  manim "$qualitaet" --media_dir /manim/media "$datei" "$szene"
case $qualitaet in
  -ql) ordner=480p15 ;; -qm) ordner=720p30 ;; -qh) ordner=1080p60 ;; -qk) ordner=2160p60 ;;
  *) echo "unbekannte Qualität: $qualitaet" >&2; exit 1 ;;
esac
video="media/videos/${datei%.py}/$ordner/$szene.mp4"
mkdir -p ../public/videos
cp "$video" "../public/videos/$szene.mp4"
echo "fertig: public/videos/$szene.mp4"
