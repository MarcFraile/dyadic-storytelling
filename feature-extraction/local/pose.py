import math
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Literal, TypeAlias

import numpy as np
import pandas as pd
import imageio.v3 as iio
from imageio.core.v3_plugin_api import PluginV3 as IioPlugin
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

from local import util, draw


# Based on https://cmu-perceptual-computing-lab.github.io/openpose/web/html/doc/md_doc_02_output.html
JOINTS = [
    "nose",
    "neck",
    "right_shoulder",
    "right_elbow",
    "right_wrist",
    "left_shoulder",
    "left_elbow",
    "left_wrist",
    "mid_hip",
    "right_hip",
    "right_knee",
    "right_ankle",
    "left_hip",
    "left_knee",
    "left_ankle",
    "right_eye",
    "left_eye",
    "right_ear",
    "left_ear",
    "left_big_toe",
    "left_small_toe",
    "left_heel",
    "right_big_toe",
    "right_small_toe",
    "right_heel",
]


JOINTS_CATEGORICAL = pd.CategoricalDtype(JOINTS, ordered=True)


# lower idx joint => list of higher index joints. Each bone appears only once.
JOINT_CONNECTIONS : dict[str, list[str]] = {
    "nose"            : [ "neck", "right_eye", "left_eye" ],
    "neck"            : [ "right_shoulder", "left_shoulder", "mid_hip" ],
    "right_shoulder"  : [ "right_elbow" ],
    "right_elbow"     : [ "right_wrist" ],
    "right_wrist"     : [],
    "left_shoulder"   : [ "left_elbow" ],
    "left_elbow"      : [ "left_wrist" ],
    "left_wrist"      : [],
    "mid_hip"         : [ "left_hip", "right_hip" ],
    "right_hip"       : [ "right_knee" ],
    "right_knee"      : [ "right_ankle" ],
    "right_ankle"     : [],
    "left_hip"        : [ "left_knee" ],
    "left_knee"       : [ "left_ankle" ],
    "left_ankle"      : [],
    "right_eye"       : [ "right_ear" ],
    "left_eye"        : [ "left_ear" ],
    "right_ear"       : [],
    "left_ear"        : [],
    "left_big_toe"    : [],
    "left_small_toe"  : [],
    "left_heel"       : [],
    "right_big_toe"   : [],
    "right_small_toe" : [],
    "right_heel"      : [],
}


@dataclass
class Keypoint:
    x          : float
    y          : float
    confidence : float


@dataclass
class Skeleton:
    joints : dict[str, Keypoint]
    id     : Optional[int] = None


MIN_CONFIDENCE = 0.20
BAD_MATCH_RMSE = 1e30

VIZ_CIRCLE_RADIUS = 12 # TODO: Check if it needs to be int or it can also be float
VIZ_BONE_WIDTH = 10 # TODO: Check if it needs to be int or it can also be float
VIZ_ID_OFFSET = ( -60, -140 )
VIZ_ID_PADDING = 50
VIZ_FONT_BIG = ImageFont.truetype('FreeMono.ttf', size=42)
VIZ_FONT_SMALL = ImageFont.truetype('FreeMono.ttf', size=26)


def get_rmse(first: Skeleton, second: Skeleton) -> float:
    """
    Calculates the Root Mean Square Error (RMSE) between the joints in `first` and `second`, ignoring joints whose confidence is below `MIN_CONFIDENCE`. If no joints are matched, returns `BAD_MATCH_RMSE` (finite but large number).
    """

    sum_errors = 0.0
    count = 0

    for joint in JOINTS:
        assert joint in first.joints , f"Expected `first` to contain all joints, but '{joint}' is missing."
        assert joint in second.joints, f"Expected `second` to contain all joints, but '{joint}' is missing."

        first_keypoint = first.joints[joint]
        second_keypoint = second.joints[joint]

        if (first_keypoint.confidence < MIN_CONFIDENCE) or (second_keypoint.confidence < MIN_CONFIDENCE):
            continue # Ignore low condifence joints for the matching.

        square_error = (first_keypoint.x - second_keypoint.x) ** 2 + (first_keypoint.y - second_keypoint.y) ** 2

        sum_errors += square_error
        count += 1

    if count < 1:
        return BAD_MATCH_RMSE
    else:
        return math.sqrt(sum_errors / count)


def get_center_of_mass(skeleton: Skeleton) -> Keypoint:
    """
    Returns the geometric center of all joints in `skeleton` whose confidence is above `MIN_CONFIDENCE`.

    * The returned keypoint's `confidence` is calculated averaging ALL joints, including those with `confidence < MIN_CONFIDENCE`.
    """
    xy = np.array([ (joint.x, joint.y) for joint in skeleton.joints.values() if joint.confidence > MIN_CONFIDENCE ], dtype=float)
    confidences = np.array([ joint.confidence for joint in skeleton.joints.values() ])

    if len(xy) == 0:
        return Keypoint(x=np.nan, y=np.nan, confidence=0.0)

    (x, y) = xy.mean(axis=0)
    confidence = confidences.mean()

    return Keypoint(x, y, confidence)


def _id_to_text(id: str, id_style: Literal["hex", "dec"]) -> str:
    """Converts the `id` to a string in a predefined format, based on the chosen `id_style`."""
    return f"0x{id:08x}" if (id_style == "hex") else f"{id:02}"


def draw_frame(
        frame: np.ndarray,
        skeletons: list[Skeleton],
        show_joint_names: bool,
        id_style: Literal["hex", "dec"],
        score: Optional[float],
) -> np.ndarray:

    if len(skeletons) < 1:
        return frame

    id_to_color: dict[int, draw.RGB] = {}

    pil = Image.fromarray(frame)
    brush = ImageDraw.Draw(pil, mode="RGBA")

    for skelly in skeletons:

        if skelly.id not in id_to_color:
            id_to_color[skelly.id] = draw.get_rgb_from_id(skelly.id)
        rgb = id_to_color[skelly.id]

        for keypoint in skelly.joints.values():
            x, y = keypoint.x, keypoint.y
            joint_alpha = int(255 * keypoint.confidence)
            brush.ellipse(xy=(x - VIZ_CIRCLE_RADIUS, y - VIZ_CIRCLE_RADIUS, x + VIZ_CIRCLE_RADIUS, y + VIZ_CIRCLE_RADIUS), fill=(*rgb, joint_alpha))

        for first_joint, joint_list in JOINT_CONNECTIONS.items():
            first_keypoint = skelly.joints[first_joint]
            for second_joint in joint_list:
                second_keypoint = skelly.joints[second_joint]
                if first_keypoint.confidence > 0 and second_keypoint.confidence > 0:
                    bone_alpha = int(255 * min(first_keypoint.confidence, second_keypoint.confidence))
                    brush.line(xy=(first_keypoint.x, first_keypoint.y, second_keypoint.x, second_keypoint.y), fill=(*rgb, bone_alpha), width=VIZ_BONE_WIDTH)

        if show_joint_names:
            for (joint, keypoint) in skelly.joints.items():
                x, y, confidence = keypoint.x, keypoint.y, keypoint.confidence
                if confidence > MIN_CONFIDENCE:
                    joint_alpha = int(255 * confidence)

                    brush.text(xy=(x,y), text=joint, fill=(*rgb, joint_alpha), font=VIZ_FONT_SMALL, stroke_width=1, stroke_fill=(0,0,0,joint_alpha))

        label_anchor = None
        for joint in JOINTS:
            candidate = skelly.joints[joint]
            if candidate.confidence > MIN_CONFIDENCE:
                label_anchor = candidate
                break

        if label_anchor is not None:
            x = max(VIZ_ID_PADDING, min(frame.shape[1] - VIZ_ID_PADDING, label_anchor.x + VIZ_ID_OFFSET[0]))
            y = max(VIZ_ID_PADDING, min(frame.shape[0] - VIZ_ID_PADDING, label_anchor.y + VIZ_ID_OFFSET[1]))
            text = _id_to_text(skelly.id, id_style)
            brush.text(xy=(x,y), text=text, fill=rgb, font=VIZ_FONT_BIG, stroke_width=2, stroke_fill=(0,0,0,joint_alpha))

    brush.text(xy=(50, frame.shape[0] - 80), text=f"Skeletons in Frame: {len(skeletons)}", fill="white", font=VIZ_FONT_SMALL, stroke_fill="black", stroke_width=1)

    if score is not None:
        brush.text(xy=(50, frame.shape[0] - 50), text=f"Score: {score:6.2f}", fill="white", font=VIZ_FONT_SMALL, stroke_fill="black", stroke_width=1)

    for (idx, (id, color)) in enumerate(id_to_color.items()):
        x = frame.shape[1] - 160
        y = frame.shape[0] - 30 * (2 + len(id_to_color) - idx)
        text = _id_to_text(id, id_style)
        brush.text(xy=(x,y), text=text, fill=color, font=VIZ_FONT_SMALL, stroke_fill="black", stroke_width=1)

    return np.asarray(pil)


VID_TYPES = [ "overlay", "feature" ]
STEM_ENDS = {
    "overlay": "pose-viz",
    "feature": "pose-features",
}
assert set(VID_TYPES) == set(STEM_ENDS.keys())

def visualize_skeletons(
        viz_dir: Path,
        vid: Path,
        skeletons: List[List[Skeleton]],
        id_style: Literal["hex", "dec"],
        scores: Optional[List[float]] = None,
        show_joint_names: bool = False,
        create_overlay: bool = True,
        create_feature: bool = True,
) -> None:
    """Overlays the given `skeletons` list-of-lists (frame => person => `Skeleton`) on the `vid`, and saves the result in `viz_dir`."""

    assert viz_dir.is_dir(), f"Expected `viz_dir` to be a dir: {viz_dir}"
    assert vid.is_file(), f"Expected `vid` to be a file: {vid}"

    create = {
        "overlay": create_overlay,
        "feature": create_feature,
    }
    assert set(VID_TYPES) == set(create.keys())
    assert any(create.values()), f"At least one type of video should be created; got: {create}"

    # ImageIO can be chatty. This with-clause suppresses warnings raised inside it.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        meta = iio.immeta(vid)
    assert "codec" in meta, f"Expected video metadata to contain a `'codec'` entry. Fields: {meta.keys()}"
    assert "fps" in meta, f"Expected video metadata to contain a `'fps'` entry. Fields: {meta.keys()}"
    assert "duration" in meta, f"Expected video metadata to contain a `'duration'` entry. Fields: {meta.keys()}"

    handles: dict[str, IioPlugin] = {}
    try:
        for vid_type in VID_TYPES:
            if create[vid_type]:
                path = viz_dir / f"{vid.stem}-{STEM_ENDS[vid_type]}{vid.suffix}"
                handle = iio.imopen(path, "w", plugin="pyav")
                handles[vid_type] = handle
                handle.init_video_stream(codec=meta["codec"], fps=meta["fps"])

        for frame_idx, in_frame in tqdm(enumerate(iio.imiter(vid)), desc="frame", total=int(meta["fps"] * meta["duration"])):

            frame_skellys = []
            if frame_idx < len(skeletons):
                frame_skellys = skeletons[frame_idx]

            score = None
            if (scores is not None) and frame_idx < len(scores):
                score = scores[frame_idx]

            if create["overlay"]:
                overlay_handle = handles["overlay"]
                overlay_frame = draw_frame(in_frame.copy(), frame_skellys, show_joint_names, id_style, score)
                overlay_handle.write_frame(overlay_frame)

            if create["feature"]:
                feature_handle = handles["feature"]
                feature_frame = draw_frame(np.zeros_like(in_frame), frame_skellys, show_joint_names, id_style, score)
                feature_handle.write_frame(feature_frame)
    finally:
        for handle in handles.values():
            handle.close()


def get_keypoint(data: pd.DataFrame, frame: int, person_id: int, joint: str) -> Keypoint:
    """Parses one keypoint from the pose `data` (output from `scripts/extract-pose`)."""
    row = data.loc[(frame, person_id, joint), :]
    return Keypoint(x=row["x"], y=row["y"], confidence=row["confidence"])


def get_skeleton(data: pd.DataFrame, frame: int, person_id: int) -> Skeleton:
    """Parses one skeleton from the pose `data` (output from `scripts/extract-pose`)."""
    return Skeleton(
        joints = { joint: get_keypoint(data, frame, person_id, joint) for joint in JOINTS },
        id     = person_id,
    )

def get_first_ordered_pair(data: pd.DataFrame, id_key: str = "person_id") -> tuple[int, int]:
    """
    Returns the leftmost and rightmost IDs for the first frame containing more than one skeleton.
    * `data` should be a `DataFrame` indexed by `(frame, person_id)`, with columns `(joint, x, y, confidence)`.
    * Returns in order `(leftmost_id, rightmost_id)`.
    """
    # Previously, we assumed there were at least two visible skeletons by the first logged frame.
    # A counter-example to this is right-cam-P248-planning-3 where only one of the children was detected in the first few frames.
    # We have weakened the assumption: now we search for the first frame with at least two skeletons, and assume that all previous skeletons match one of the IDs listed there.

    frames = data.index.get_level_values("frame").unique().sort_values()

    min_ids = None
    min_cm = None

    for frame in frames:
        min_ids = data.loc[frame].index.get_level_values(id_key).unique()
        if len(min_ids) > 1:
            min_cm = [ (person_id, get_center_of_mass(get_skeleton(data, frame, person_id))) for person_id in min_ids ]
            break

    assert (min_ids is not None) and (len(min_ids) > 1), f"Expected `min_ids` to be a collection with at least 2 elements; got: {min_ids}"
    assert (min_cm is not None) and (len(min_cm) == len(min_ids)), f"Expected `min_cm` to be a collection with {len(min_ids)} elements; got: {min_cm}"

    (leftmost_id , leftmost_keypoint ) = min(min_cm, key=lambda pair: pair[1].x)
    (rightmost_id, rightmost_keypoint) = max(min_cm, key=lambda pair: pair[1].x)

    assert(leftmost_id != rightmost_id), f"In (frame: {frame}; IDs in frame: {list(min_ids)}), expected the leftmost ID ({leftmost_id}) to be different from the rightmost ID ({rightmost_id})."
    assert(leftmost_keypoint.x < rightmost_keypoint.x)
    assert(leftmost_keypoint.confidence > 0)
    assert(rightmost_keypoint.confidence > 0)

    return leftmost_id, rightmost_id
