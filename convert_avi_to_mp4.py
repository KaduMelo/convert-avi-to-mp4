#!/usr/bin/env python3
"""Converte arquivos .avi para .mp4 usando o ffmpeg, preservando a qualidade original."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "Erro: ffmpeg não encontrado no PATH.\n"
            "Instale com: sudo apt install ffmpeg"
        )


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
        capture_output=True,
        text=True,
    )


def convert_file(input_path: Path, output_path: Path, lossless: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_args = ["-c:v", "libx264", "-preset", "veryslow", "-crf", "0"]

    # Cada tentativa é tentada em ordem até uma funcionar. Todas preservam a
    # qualidade original — a diferença é só se recodificam vídeo/áudio ou não.
    attempts = []
    if not lossless:
        attempts.append(
            ("remux, sem recodificar", ["-c", "copy", "-map", "0"])
        )
    attempts.append(
        ("vídeo recodificado sem perdas, áudio copiado", [*video_args, "-c:a", "copy"])
    )
    attempts.append(
        (
            "vídeo e áudio recodificados sem perdas",
            [*video_args, "-c:a", "flac", "-strict", "-2"],
        )
    )

    last_stderr = ""
    for label, extra_args in attempts:
        result = run_ffmpeg(["-i", str(input_path), *extra_args, str(output_path)])
        if result.returncode == 0:
            print(f"[{label}] {input_path.name} -> {output_path.name}")
            return
        last_stderr = result.stderr

    print(f"[FALHOU] {input_path.name}:\n{last_stderr}", file=sys.stderr)


def gather_inputs(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    return sorted(source.rglob("*.avi")) + sorted(source.rglob("*.AVI"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Converte arquivos .avi para .mp4 sem perder qualidade."
    )
    parser.add_argument("source", type=Path, help="Arquivo .avi ou diretório com arquivos .avi")
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=None,
        help="Diretório de saída (padrão: mesmo diretório do arquivo de entrada)",
    )
    parser.add_argument(
        "--lossless", action="store_true",
        help="Força recodificação sem perdas (CRF 0) em vez de tentar remux direto",
    )
    args = parser.parse_args()

    check_ffmpeg()

    if not args.source.exists():
        sys.exit(f"Erro: '{args.source}' não existe.")

    inputs = gather_inputs(args.source)
    if not inputs:
        sys.exit(f"Nenhum arquivo .avi encontrado em '{args.source}'.")

    for input_path in inputs:
        out_dir = args.output_dir or input_path.parent
        output_path = out_dir / (input_path.stem + ".mp4")
        convert_file(input_path, output_path, args.lossless)


if __name__ == "__main__":
    main()
