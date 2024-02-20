#!/bin/env -S python3


from pathlib import Path
import json
import subprocess
import argparse
from typing import Dict, Any, Literal

import pandas as pd
from pretty_cli import PrettyCli


VIDEO_EXTENSIONS = [ ".mp4", ".mov", ".mts" ]
AUDIO_EXTENSIONS = [ ".mp3", ".wav" ]

AUDIO_FIELDS = [ "codec_name", "sample_fmt", "sample_rate", "channels", "channel_layout", "start_time", "duration", "file_extension" ]
VIDEO_FIELDS = [ "codec_name", "width", "height", "pix_fmt", "r_frame_rate", "start_time", "duration", "file_extension" ]
CONTINUOUS_FIELDS = [ "start_time", "duration" ]

cli = PrettyCli()


class Collector:
    def __init__(self):
        self.data : Dict[str, Dict[Any, int]] = dict() # key => value => count

    def ingest(self, meta: Dict[str, Any]) -> None:
        for key, value in meta.items():
            if key not in self.data:
                self.data[key] = dict()
            if value not in self.data[key]:
                self.data[key][value] = 1
            else:
                self.data[key][value] += 1

    def get_counts(self) -> Dict[str, Dict[str, int]]:
        return { name: { str(k): v for (k, v) in values.items() } for (name, values) in self.data.items() if name not in CONTINUOUS_FIELDS }

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        output = dict()
        for field in CONTINUOUS_FIELDS:
            values = []
            for (k, v) in self.data[field].items():
                if k is not None:
                    values += [ float(k) ] * v
            output[field] = pd.Series(values).describe().to_dict()
        return output


def parse_fraction(fraction: str) -> float:
    numerator, denominator = fraction.split("/")
    return float(numerator) / float(denominator)


def get_data(file: Path, type: Literal["audio", "video"]) -> Dict[str, Any]:
    flag = type[0]
    ret = subprocess.run(f"ffprobe -hide_banner -v quiet -show_streams -of json -select_streams {flag}:0 -i {file}", shell=True, stdout=subprocess.PIPE)

    data = json.loads(ret.stdout)
    data = data["streams"][0]
    data["file_extension"] = file.suffix.lower()

    return data


def get_audio_data(file: Path) -> Dict[str, Any]:
    data = get_data(file, type="audio")
    data = { field: data.get(field, None) for field in AUDIO_FIELDS }
    return data


def get_video_data(file: Path) -> Dict[str, Any]:
    data = get_data(file, type="video")
    data = { field: data.get(field, None) for field in VIDEO_FIELDS }

    # Get fps as a nice float instead of a fraction string.
    data["fps"] = parse_fraction(data["r_frame_rate"])
    del data["r_frame_rate"]

    # Get the resolution as a tuple to keep it together.
    data["resolution"] = (data["width"], data["height"])
    del data["width"]
    del data["height"]

    return data


def handle_args():
    parser = argparse.ArgumentParser(description="Collect media format stats from the files in all subdirs of the given dir")
    parser.add_argument("dir", help="Directory to be processed")
    args = parser.parse_args()
    return args


def main() -> None:
    args = handle_args()

    cli.main_title("MEDIA STATS")
    stats : Dict[str, Any] = dict()

    root = Path(args.dir)
    assert root.is_dir(), f"Positional argument <dir> should be a directory, but we received non-dir value: {dir}"

    dirs = [ item for item in root.iterdir() if item.is_dir() ]
    dirs.sort()
    cli.print(dirs)

    for dir in dirs:
        dir_name = str(dir)
        cli.chapter(dir_name)
        stats[dir_name] = dict()

        audio = [ item for item in dir.iterdir() if item.suffix.lower() in AUDIO_EXTENSIONS ]
        audio.sort()

        if len(audio) > 0:
            cli.subchapter("Audio")

            stats[dir_name]["audio_files"] = dict()
            stats[dir_name]["audio_files"]["audio"] = dict()

            cli.print(f"Num files: {len(audio)}")
            stats[dir_name]["audio_files"]["num_files"] = len(audio)

            audio_collector = Collector()
            for file in audio:
                audio_data = get_audio_data(file)
                audio_collector.ingest(audio_data)

            cli.section("Counts")
            audio_counts = audio_collector.get_counts()
            stats[dir_name]["audio_files"]["audio"]["counts"] = audio_counts
            cli.print(audio_counts)

            cli.section("Stats")
            audio_stats = audio_collector.get_stats()
            stats[dir_name]["audio_files"]["audio"]["stats"] = audio_stats
            cli.print(audio_stats)

        video = [ item for item in dir.iterdir() if item.suffix.lower() in VIDEO_EXTENSIONS ]
        video.sort()

        if len(video) > 0:
            cli.subchapter("Video")

            stats[dir_name]["video_files"] = dict()
            stats[dir_name]["video_files"]["audio"] = dict()
            stats[dir_name]["video_files"]["video"] = dict()

            cli.print(f"Num files: {len(video)}")
            stats[dir_name]["video_files"]["num_files"] = len(video)

            audio_collector = Collector()
            video_collector = Collector()

            for file in video:
                audio_data = get_audio_data(file)
                audio_collector.ingest(audio_data)

                video_data = get_video_data(file)
                video_collector.ingest(video_data)

            cli.section("Audio Counts")
            audio_counts = audio_collector.get_counts()
            stats[dir_name]["video_files"]["audio"]["counts"] = audio_counts
            cli.print(audio_counts)

            cli.section("Audio Stats")
            audio_stats = audio_collector.get_stats()
            stats[dir_name]["video_files"]["audio"]["stats"] = audio_stats
            cli.print(audio_stats)

            cli.section("Video Counts")
            video_counts = video_collector.get_counts()
            stats[dir_name]["video_files"]["video"]["counts"] = video_counts
            cli.print(video_counts)

            cli.section("Video Stats")
            video_stats = video_collector.get_stats()
            stats[dir_name]["video_files"]["video"]["stats"] = video_stats
            cli.print(video_stats)

    with open(root / "media_stats.json", "w") as file:
        json.dump(stats, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
