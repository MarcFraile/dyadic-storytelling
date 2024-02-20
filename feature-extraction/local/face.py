import warnings
from pathlib import Path
from typing import Iterable, TypeAlias, Literal, Any, Optional

import numpy as np
import pandas as pd
import imageio.v3 as iio
from imageio.core.v3_plugin_api import PluginV3 as IioPlugin
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from local import draw


FACE_KEYPOINT_COUNT = 68 # Face keypoints are numbered consecutively 0..67

FACE_2D_X_COLUMNS = [ f"x_{n}" for n in range(FACE_KEYPOINT_COUNT) ]
FACE_2D_Y_COLUMNS = [ f"y_{n}" for n in range(FACE_KEYPOINT_COUNT) ]

FACE_3D_X_COLUMNS = [ f"X_{n}" for n in range(FACE_KEYPOINT_COUNT) ]
FACE_3D_Y_COLUMNS = [ f"Y_{n}" for n in range(FACE_KEYPOINT_COUNT) ]
FACE_3D_Z_COLUMNS = [ f"Z_{n}" for n in range(FACE_KEYPOINT_COUNT) ]

LEFT_EYE_LANDMARKS  = [ 42, 43, 44, 45, 46, 47 ]
RIGHT_EYE_LANDMARKS = [ 36, 37, 38, 39, 40, 41 ]


def get_3d_keypoint(data: pd.DataFrame, frame: int, face_id: int, keypoint_id: int) -> np.ndarray:
    """Returns the 3D face landmark point given by `keypoint_id` as a length-3 `ndarray`, in the given `frame` and for the given `face_id`."""
    return np.array([
        data.loc[(frame, face_id), f"X_{keypoint_id}"],
        data.loc[(frame, face_id), f"Y_{keypoint_id}"],
        data.loc[(frame, face_id), f"Z_{keypoint_id}"],
    ])


def get_keypoint_average(data: pd.DataFrame, frame: int, face_id: int, keypoint_ids: Iterable[int] = range(FACE_KEYPOINT_COUNT)) -> np.ndarray:
    """
    Returns the vector average of the 3D face landmark points (X_*, Y_*, Z_*) in the given `frame` for the given `face_id`.

    * If `keypoint_ids` is not provided, all keypoints are used.
    * If `keypoint_ds` is provided, only points in the collection are included for averaging.
    """

    endings = tuple(str(id) for id in keypoint_ids)
    return np.array([
        data.loc[(frame, face_id), [ col for col in FACE_3D_X_COLUMNS if col.endswith(endings) ]].mean(),
        data.loc[(frame, face_id), [ col for col in FACE_3D_Y_COLUMNS if col.endswith(endings) ]].mean(),
        data.loc[(frame, face_id), [ col for col in FACE_3D_Z_COLUMNS if col.endswith(endings) ]].mean(),
    ])

# ================================================== #


AABB : TypeAlias = tuple[float, float, float, float]

NOSE_MARKER_RADIUS = 10
NOSE_MARKER_THICKNESS = 2

GAZE_LENGTH = 50
GAZE_WIDTH = 6
GAZE_EXTRA = 5

ID_OFFSET = ( -20, -100 )
FONT = ImageFont.truetype('FreeMono.ttf', size=40)

BBOX_THICKNESS = 4

ALPHA_PADDING = 0.15
ALPHA_RANGE = 1 - 2 * ALPHA_PADDING

CORNER_MARKER_RADIUS = 16

BLUR = ImageFilter.GaussianBlur(radius=16)


def get_eye_center(data: pd.Series, eye: Literal["left", "right"]) -> tuple[float, float]:
    """
    Approximate the eye position (in pixels) as the average of the face landmarks corresponding to the eye.
    * Expects face landmarks to be columns named `(x|y)_*`, and include a certain range of landmarks for each eye
      (see `LEFT_EYE_LANDMARKS` AND `RIGHT_EYE_LANDMARKS`).
    """

    landmark_ids = LEFT_EYE_LANDMARKS if (eye == "left") else RIGHT_EYE_LANDMARKS
    x, y = 0.0, 0.0

    for id in landmark_ids:
        lmk_x, lmk_y = data[[f"x_{id}", f"y_{id}"]]

        x += lmk_x
        y += lmk_y

    x /= len(landmark_ids)
    y /= len(landmark_ids)

    return x, y


# See https://github.com/TadasBaltrusaitis/OpenFace/wiki/Output-Format
def get_face_bounding_box(data: pd.Series) -> AABB:
    """
    Returns an `AABB` (axis-aligned bounding box) as coordinates `(x0, y0, x1, y1)`, tightly containing all the (2D) facial landmarks.
    * 2D landmarks are expected to be columns named `(x|y)_*`. Indices in range `0..67` (inclusive).
    """

    x0 = data[FACE_2D_X_COLUMNS].min()
    y0 = data[FACE_2D_Y_COLUMNS].min()

    x1 = data[FACE_2D_X_COLUMNS].max()
    y1 = data[FACE_2D_Y_COLUMNS].max()

    return x0, y0, x1, y1


def draw_marker(brush: ImageDraw, position: tuple[float, float], color: Any) -> None:
    """
    Draws a marker of radius `CORNER_MARKER_RADIUS` at the specified `position`, with the specified `color`.
    """

    (x, y) = position
    brush.ellipse(
        xy=(x - CORNER_MARKER_RADIUS, y - CORNER_MARKER_RADIUS, x + CORNER_MARKER_RADIUS, y + CORNER_MARKER_RADIUS),
        fill=color,
    )


def draw_nose(brush: ImageDraw, id: int, data: pd.Series, base_color: draw.RGB, transparent: draw.RGBA) -> None:
    """
    Draws a big transparent circle on the person's nose (with an opaque edge).
    """

    nose_x, nose_y = data[["x_33", "y_33"]]
    brush.ellipse(
        xy=(nose_x - NOSE_MARKER_RADIUS, nose_y - NOSE_MARKER_RADIUS, nose_x + NOSE_MARKER_RADIUS, nose_y + NOSE_MARKER_RADIUS),
        fill=transparent,
        outline=base_color,
        width=NOSE_MARKER_THICKNESS,
    )

    brush.text(
        xy=(nose_x + ID_OFFSET[0], nose_y + ID_OFFSET[1]),
        text=f"{id:02}",
        fill=base_color,
        font=FONT,
    )


def draw_bounding_box(brush: ImageDraw, data: pd.Series, transparent: draw.RGBA) -> None:
    """
    Draws a tight bounding box around the person's face.
    * Decides the bounding box by taking the smallest `AABB` that includes all face landmarks (see `get_face_bounding_box()`).
    """
    bbox = get_face_bounding_box(data)
    (r, g, b, a) = transparent
    brush.rectangle(xy=bbox, outline=(r, g, b, a), width=BBOX_THICKNESS)


def draw_gaze_side(brush: ImageDraw, data: pd.Series, base_color: draw.RGB, eye: Literal["left", "right"], has_gaze_vector: bool) -> None:
    """
    Draws one of the person's eyes, and the gaze direction.
    * Expects face landmarks to be columns named `(x|y)_*`, and include a certain range of landmarks for each eye
      (see `LEFT_EYE_LANDMARKS` AND `RIGHT_EYE_LANDMARKS`).
    * Will attempt to draw gaze vectors if `has_gaze_vector` is `True`.
    * Expects the gaze vectors to be columns named `gaze_(0|1)_(x|y)`,with `0` being the leftmost eye in the image
      (person's right eye), and `1` being the rightmost eye in the image (person's left eye).
    """

    eye_x, eye_y = get_eye_center(data, eye)

    circle_thickness = GAZE_WIDTH + 2 * GAZE_EXTRA
    brush.ellipse(
        xy=(eye_x - circle_thickness, eye_y - circle_thickness, eye_x + circle_thickness, eye_y + circle_thickness),
        fill=base_color,
    )

    if has_gaze_vector:
        gaze_idx = 1 if eye == "left" else 0 # OpenFace counts the eyes from the camera point of view, left to right => right eye = 0, left eye = 1.
        gaze_x, gaze_y = data[[f"gaze_{gaze_idx}_x", f"gaze_{gaze_idx}_y"]]

        eye_color = (0, 0, 255) if eye == "left" else (255, 0, 0)

        brush.line(
            xy=(eye_x, eye_y, eye_x + gaze_x * (GAZE_LENGTH + GAZE_EXTRA), eye_y + gaze_y * (GAZE_LENGTH + GAZE_EXTRA)),
            fill=base_color,
            width=GAZE_WIDTH + GAZE_EXTRA,
        )
        brush.line(
            xy=(eye_x, eye_y, eye_x + gaze_x * GAZE_LENGTH, eye_y + gaze_y * GAZE_LENGTH),
            fill=eye_color,
            width=GAZE_WIDTH,
        )


def draw_gaze(brush: ImageDraw, data: pd.Series, base_color: tuple[int, int, int]) -> None:
    """
    Draws both of the person's eyes.
    * Face landmarks are mandatory.
    * Expects face landmarks to be columns named `(x|y)_*`, and include a certain range of landmarks for each eye
      (see `LEFT_EYE_LANDMARKS` AND `RIGHT_EYE_LANDMARKS`).
    * Gaze vectors are optional.
    * Expects the gaze vectors to be columns named `gaze_(0|1)_(x|y)`,with `0` being the leftmost eye in the image
      (person's right eye), and `1` being the rightmost eye in the image (person's left eye).
    """
    has_gaze_vector = False
    if "gaze_0_x" in data.index: # We use the right eye x coordinate as a sentinel value; we assume the rest exist as well.
        has_gaze_vector = True

    draw_gaze_side(brush, data, base_color, eye="left" , has_gaze_vector=has_gaze_vector)
    draw_gaze_side(brush, data, base_color, eye="right", has_gaze_vector=has_gaze_vector)


def draw_frame(face_data_frame: pd.DataFrame, frame: np.ndarray) -> np.ndarray:
    """
    Overlays the custom face visualization on the given frame.
    """

    pil_img = Image.fromarray(frame)
    brush = ImageDraw.Draw(pil_img, mode="RGBA")

    for (face_id, row) in face_data_frame.iterrows():
        rgb = draw.get_rgb_from_id(face_id)
        alpha = draw.fraction_to_uint8(ALPHA_PADDING + ALPHA_RANGE * row["confidence"])
        rgba = (*rgb, alpha)

        draw_nose(brush, id=face_id, data=row, base_color=rgb, transparent=rgba)
        draw_bounding_box(brush, data=row, transparent=rgba)
        draw_gaze(brush, data=row, base_color=rgb)

    return np.asarray(pil_img)


def expand_bbox(bbox: AABB, factor: float) -> AABB:
    """
    Grows the bounding box `bbox` by the given proportional `factor`, keeping the center of the box at the same location.
    """
    (x0, y0, x1, y1) = bbox

    w = x1 - x0
    h = y1 - y0

    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2

    x0 = cx - (factor * w) / 2
    x1 = cx + (factor * w) / 2

    y0 = cy - (factor * h) / 2
    y1 = cy + (factor * h) / 2

    return (x0, y0, x1, y1)


def blur_frame(face_data_frame: pd.DataFrame, frame: np.ndarray) -> np.ndarray:
    """
    Blurs faces out of the given `frame`.
    """

    pil_img = Image.fromarray(frame)

    for (_, row) in face_data_frame.iterrows():
        bbox = get_face_bounding_box(data=row)
        bbox = expand_bbox(bbox, factor=1.30)
        bbox = tuple(map(int, map(round, bbox)))

        crop = pil_img.crop(box=bbox)
        crop = crop.filter(filter=BLUR)
        pil_img.paste(im=crop, box=bbox)

    return np.asarray(pil_img)


VID_TYPES = [ "overlay", "anonymized", "feature" ]
STEM_ENDS = {
    "overlay": "custom-face-viz",
    "anonymized": "anonymized",
    "feature": "face-features",
}
assert set(VID_TYPES) == set(STEM_ENDS.keys())

def visualize(
        vid: Path,
        viz_dir: Path,
        face_data: pd.DataFrame,
        create_overlay: bool = True,
        create_anonymized: bool = True,
        create_feature: bool = True,
) -> None:
    """
    Creates any of a number of video visualizations by combining `face_data` and `vid`, as determined by the `create_*` flags.
    * Overlay: superimposes the data visualization on the original video frames.
    * Anonymized: blurs the faces in the original video frames, but does not visualize the extracted featues.
    * Feature: Displays the data visualization on a black background, without using the original frames.
    """
    assert viz_dir.is_dir(), f"Expected `viz_dir` to be a dir: {viz_dir}"
    assert vid.is_file(), f"Expected `vid` to be a file: {vid}"

    create = {
        "overlay": create_overlay,
        "anonymized": create_anonymized,
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

        for frame_idx, in_frame in tqdm(enumerate(iio.imiter(vid), start=1), desc="frame", total=int(meta["fps"] * meta["duration"])):

            # There will be no entries if no face was detected , and if more than 2 faces are detected
            face_data_frame: Optional[pd.DataFrame] = None
            if frame_idx in face_data.index:
                face_data_frame = face_data.loc[frame_idx]

            if create["overlay"]:
                overlay_handle = handles["overlay"]
                overlay_frame = in_frame.copy()
                if face_data_frame is not None:
                    overlay_frame = draw_frame(face_data_frame, overlay_frame)
                overlay_handle.write_frame(overlay_frame)

            if create["anonymized"]:
                anonymized_handle = handles["anonymized"]
                anonymized_frame = in_frame.copy()
                if face_data_frame is not None:
                    anonymized_frame = blur_frame(face_data_frame, anonymized_frame)
                anonymized_handle.write_frame(anonymized_frame)

            if create["feature"]:
                feature_handle = handles["feature"]
                feature_frame = np.zeros_like(in_frame)
                if face_data_frame is not None:
                    feature_frame    = draw_frame(face_data_frame, feature_frame)
                feature_handle.write_frame(feature_frame)
    finally:
        for handle in handles.values():
            handle.close()
