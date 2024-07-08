#!/bin/sh

# =========================================================================================================================================================== #
# Reproducible commands used to extract each round of the game from the videos in Classified/ (full session per video) into Clean/ (one round per video).
#
# Parameters in the ffmpeg calls:
#     -hide_banner      --- avoid printing a very large header, describing the compilation details / capabilities of this `ffmpeg` command.
#     -y                --- yes to all (just overwrite files instead of asking interactively, etc.)
#     -i <input_file>   --- this file is the source video to be manipulated.
#     -ss HH:MM:SS      --- Seek to this timestamp before starting to process. Does a fast but imprecise seek if placed before -i; does a slow but precise seek if placed after -i.
#     -to HH:MM:SS      --- Process until this timestamp (in the source timeline).
#     -c:v <codec>      --- The output *video* stream(s) shall be encoded using this *video* codec.
#     -c:a <codec>      --- The output *audio* stream(s) shall be encoded using this *audio* codec.
#     -vf <f1,f2...>    --- Apply the video filters f1, f2... (comma-separated, no spaces).
#         scale=xxx:yyy --- Interpolate as necessary to obtain an output resolution of xxx (width) by yyy (height).
#         yadif         --- Use the YADIF filter to convert from interlaced frames to non-interlaced frames.
#     -preset <preset>  --- Choose a configuration regarding the tradeoff between *encoding time* and *video quality*. Values: slowest, slow, ..., fastest.
#     -crf <crf>        --- Set the bitrate using a *constant rate factor*. This determines the tradeoff between *file size* and *video quality*. Values: 0 (highest quality) - 51 (lowest quality). Recommended: 17-28.
#     <out_file>        --- this path will be used for the output file.
# =========================================================================================================================================================== #

# ==== N249 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N249.MTS" -ss 00:00:27 -to 00:03:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N249-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N249.MTS" -ss 00:04:18 -to 00:07:10 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N249-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N249.MTS" -ss 00:08:15 -to 00:10:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N249-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N249.MTS" -ss 00:00:21 -to 00:03:11 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N249-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N249.MTS" -ss 00:04:13 -to 00:07:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N249-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N249.MTS" -ss 00:08:10 -to 00:10:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N249-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N249.mp4" -ss 00:00:30 -to 00:03:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N249-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N249.mp4" -ss 00:04:22 -to 00:07:15 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N249-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N249.mp4" -ss 00:08:19 -to 00:10:34 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N249-planning-3.mp4"

# ==== N250 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N250.MTS" -ss 00:00:41 -to 00:02:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N250-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N250.MTS" -ss 00:03:02 -to 00:04:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N250-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N250.MTS" -ss 00:05:47 -to 00:07:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N250-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N250.MTS" -ss 00:00:25 -to 00:01:44 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N250-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N250.MTS" -ss 00:02:46 -to 00:04:15 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N250-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N250.MTS" -ss 00:05:31 -to 00:07:07 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N250-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N250.mp4" -ss 00:00:48 -to 00:02:08 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N250-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N250.mp4" -ss 00:03:11 -to 00:04:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N250-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N250.mp4" -ss 00:05:55 -to 00:07:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N250-planning-3.mp4"

# ==== N251 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N251.MTS" -ss 00:00:07 -to 00:01:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N251-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N251.MTS" -ss 00:02:38 -to 00:04:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N251-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N251.MTS" -ss 00:05:34 -to 00:07:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N251-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N251.MTS" -ss 00:00:12 -to 00:01:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N251-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N251.MTS" -ss 00:02:43 -to 00:04:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N251-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N251.MTS" -ss 00:05:39 -to 00:07:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N251-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N251.mp4" -ss 00:00:12 -to 00:01:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N251-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N251.mp4" -ss 00:02:43 -to 00:04:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N251-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N251.mp4" -ss 00:05:39 -to 00:07:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N251-planning-3.mp4"

# ==== N252 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N252.MTS" -ss 00:00:20 -to 00:05:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N252-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N252.MTS" -ss 00:08:49 -to 00:13:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N252-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N252.MTS" -ss 00:15:42 -to 00:18:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N252-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N252.MTS" -ss 00:00:07 -to 00:05:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N252-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N252.MTS" -ss 00:08:36 -to 00:13:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N252-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N252.MTS" -ss 00:15:29 -to 00:17:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N252-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N252.mp4" -ss 00:00:16 -to 00:05:36 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N252-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N252.mp4" -ss 00:08:45 -to 00:13:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N252-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N252.mp4" -ss 00:15:38 -to 00:17:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N252-planning-3.mp4"

# ==== N253 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N253.MTS" -ss 00:00:48 -to 00:01:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N253-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N253.MTS" -ss 00:02:43 -to 00:03:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N253-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N253.MTS" -ss 00:04:43 -to 00:06:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N253-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N253.MTS" -ss 00:08:00 -to 00:09:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N253-planning-4.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N253.MTS" -ss 00:00:39 -to 00:01:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N253-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N253.MTS" -ss 00:02:34 -to 00:03:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N253-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N253.MTS" -ss 00:04:34 -to 00:06:32 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N253-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N253.MTS" -ss 00:07:52 -to 00:09:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N253-planning-4.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N253.mp4" -ss 00:00:47 -to 00:01:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N253-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N253.mp4" -ss 00:02:42 -to 00:03:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N253-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N253.mp4" -ss 00:04:42 -to 00:06:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N253-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N253.mp4" -ss 00:07:59 -to 00:09:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N253-planning-4.mp4"

# ==== N254 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N254.MTS" -ss 00:00:28 -to 00:01:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N254-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N254.MTS" -ss 00:02:14 -to 00:03:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N254-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N254.MTS" -ss 00:04:15 -to 00:05:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N254-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N254.MTS" -ss 00:00:31 -to 00:01:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N254-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N254.MTS" -ss 00:02:17 -to 00:03:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N254-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N254.MTS" -ss 00:04:18 -to 00:05:29 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N254-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N254.mp4" -ss 00:00:06 -to 00:00:57 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N254-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N254.mp4" -ss 00:01:52 -to 00:03:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N254-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N254.mp4" -ss 00:03:53 -to 00:05:04 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N254-planning-3.mp4"

# ==== N255 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N255.MTS" -ss 00:00:16 -to 00:01:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N255-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N255.MTS" -ss 00:02:22 -to 00:03:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N255-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N255.MTS" -ss 00:04:30 -to 00:05:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N255-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N255.MTS" -ss 00:06:51 -to 00:08:12 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N255-planning-4.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N255.MTS" -ss 00:00:10 -to 00:01:07 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N255-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N255.MTS" -ss 00:02:16 -to 00:03:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N255-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N255.MTS" -ss 00:04:24 -to 00:05:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N255-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N255.MTS" -ss 00:06:45 -to 00:08:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N255-planning-4.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N255.mp4" -ss 00:00:17 -to 00:01:14 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N255-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N255.mp4" -ss 00:02:23 -to 00:03:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N255-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N255.mp4" -ss 00:04:31 -to 00:05:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N255-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N255.mp4" -ss 00:06:52 -to 00:08:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N255-planning-4.mp4"

# ==== N256 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N256.MTS" -ss 00:00:36 -to 00:04:12 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N256-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N256.MTS" -ss 00:05:26 -to 00:07:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N256-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N256.MTS" -ss 00:07:53 -to 00:10:14 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N256-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N256.MTS" -ss 00:00:39 -to 00:04:15 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N256-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N256.MTS" -ss 00:05:29 -to 00:07:03 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N256-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N256.MTS" -ss 00:07:56 -to 00:10:17 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N256-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N256.mp4" -ss 00:00:08 -to 00:03:44 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N256-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N256.mp4" -ss 00:04:58 -to 00:06:32 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N256-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N256.mp4" -ss 00:07:25 -to 00:09:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N256-planning-3.mp4"

# ==== N257 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N257.MTS" -ss 00:01:05 -to 00:02:56 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N257-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N257.MTS" -ss 00:04:01 -to 00:05:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N257-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N257.MTS" -ss 00:07:16 -to 00:08:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N257-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N257.MTS" -ss 00:00:57 -to 00:02:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N257-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N257.MTS" -ss 00:03:54 -to 00:05:12 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N257-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N257.MTS" -ss 00:07:09 -to 00:08:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N257-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N257.mp4" -ss 00:00:12 -to 00:02:03 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N257-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N257.mp4" -ss 00:03:08 -to 00:04:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N257-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N257.mp4" -ss 00:06:23 -to 00:07:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N257-planning-3.mp4"

# ==== N258 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N258.MTS" -ss 00:00:28 -to 00:02:15 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N258-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N258.MTS" -ss 00:03:16 -to 00:04:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N258-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N258.MTS" -ss 00:05:30 -to 00:07:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N258-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N258.MTS" -ss 00:00:14 -to 00:02:01 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N258-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N258.MTS" -ss 00:03:02 -to 00:04:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N258-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N258.MTS" -ss 00:05:16 -to 00:07:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N258-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N258.mp4" -ss 00:00:33 -to 00:02:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N258-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N258.mp4" -ss 00:03:21 -to 00:04:43 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N258-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N258.mp4" -ss 00:05:35 -to 00:07:35 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N258-planning-3.mp4"

# ==== N260 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N260.MTS" -ss 00:01:20 -to 00:03:08 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N260-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N260.MTS" -ss 00:04:05 -to 00:05:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N260-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N260.MTS" -ss 00:06:05 -to 00:07:01 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N260-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N260.MTS" -ss 00:07:43 -to 00:08:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N260-planning-4.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N260.MTS" -ss 00:00:43 -to 00:02:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N260-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N260.MTS" -ss 00:03:28 -to 00:04:36 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N260-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N260.MTS" -ss 00:05:28 -to 00:06:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N260-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N260.MTS" -ss 00:07:06 -to 00:08:10 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N260-planning-4.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N260.mp4" -ss 00:00:54 -to 00:02:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N260-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N260.mp4" -ss 00:03:39 -to 00:04:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N260-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N260.mp4" -ss 00:05:39 -to 00:06:35 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N260-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N260.mp4" -ss 00:07:17 -to 00:08:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N260-planning-4.mp4"

# ==== N261 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N261.MTS" -ss 00:00:17 -to 00:02:18 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N261-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N261.MTS" -ss 00:03:13 -to 00:05:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N261-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N261.MTS" -ss 00:05:39 -to 00:07:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N261-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N261.MTS" -ss 00:00:12 -to 00:02:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N261-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N261.MTS" -ss 00:03:08 -to 00:04:55 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N261-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N261.MTS" -ss 00:05:34 -to 00:07:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N261-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N261.mp4" -ss 00:00:10 -to 00:02:11 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N261-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N261.mp4" -ss 00:03:06 -to 00:04:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N261-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N261.mp4" -ss 00:05:32 -to 00:07:14 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N261-planning-3.mp4"

# ==== N262 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N262.MTS" -ss 00:00:14 -to 00:02:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N262-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N262.MTS" -ss 00:03:40 -to 00:05:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N262-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N262.MTS" -ss 00:06:29 -to 00:08:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N262-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N262.MTS" -ss 00:00:09 -to 00:02:15 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N262-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N262.MTS" -ss 00:03:35 -to 00:05:11 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N262-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N262.MTS" -ss 00:06:24 -to 00:08:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N262-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N262.mp4" -ss 00:00:11 -to 00:02:17 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N262-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N262.mp4" -ss 00:03:37 -to 00:05:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N262-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N262.mp4" -ss 00:06:26 -to 00:08:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N262-planning-3.mp4"

# ==== N332 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N332.MTS" -ss 00:01:15 -to 00:02:44 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N332-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N332.MTS" -ss 00:04:16 -to 00:05:58 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N332-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N332.MTS" -ss 00:07:20 -to 00:09:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N332-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N332.MTS" -ss 00:01:07 -to 00:02:36 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N332-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N332.MTS" -ss 00:04:08 -to 00:05:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N332-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N332.MTS" -ss 00:07:12 -to 00:09:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N332-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N332.mp4" -ss 00:04:11 -to 00:05:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N332-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N332.mp4" -ss 00:07:12 -to 00:08:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N332-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N332.mp4" -ss 00:10:16 -to 00:12:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N332-planning-3.mp4"

# ==== N333 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N333.MTS" -ss 00:00:25 -to 00:08:18 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N333-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N333.MTS" -ss 00:13:52 -to 00:21:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N333-planning-2.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N333.MTS" -ss 00:00:13 -to 00:08:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N333-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N333.MTS" -ss 00:13:40 -to 00:20:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N333-planning-2.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N333.mp4" -ss 00:00:26 -to 00:08:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N333-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N333.mp4" -ss 00:13:53 -to 00:21:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N333-planning-2.mp4"

# ==== N334 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N334.MTS" -ss 00:00:12 -to 00:05:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N334-planning-1.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N334.MTS" -ss 00:00:22 -to 00:05:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N334-planning-1.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N334.mp4" -ss 00:00:15 -to 00:05:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N334-planning-1.mp4"

# ==== N335 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N335.MTS" -ss 00:00:27 -to 00:01:48 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N335-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N335.MTS" -ss 00:03:09 -to 00:04:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N335-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-N335.MTS" -ss 00:06:37 -to 00:08:56 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-N335-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N335.MTS" -ss 00:00:18 -to 00:01:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N335-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N335.MTS" -ss 00:03:00 -to 00:04:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N335-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-N335.MTS" -ss 00:06:28 -to 00:08:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-N335-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N335.mp4" -ss 00:00:29 -to 00:01:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N335-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N335.mp4" -ss 00:03:11 -to 00:04:51 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N335-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-N335.mp4" -ss 00:06:39 -to 00:08:58 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-N335-planning-3.mp4"

# ==== P203 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P203.MTS" -ss 00:00:39 -to 00:02:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P203-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P203.MTS" -ss 00:03:36 -to 00:05:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P203-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P203.MTS" -ss 00:06:56 -to 00:08:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P203-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P203.MTS" -ss 00:00:29 -to 00:02:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P203-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P203.MTS" -ss 00:03:26 -to 00:05:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P203-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P203.MTS" -ss 00:06:46 -to 00:07:55 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P203-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P203.mp4" -ss 00:00:39 -to 00:02:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P203-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P203.mp4" -ss 00:03:36 -to 00:05:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P203-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P203.mp4" -ss 00:06:56 -to 00:08:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P203-planning-3.mp4"

# ==== P237 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P237.MTS" -ss 00:07:09 -to 00:10:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P237-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P237.MTS" -ss 00:13:08 -to 00:15:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P237-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P237.MTS" -ss 00:17:58 -to 00:20:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P237-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P237.MTS" -ss 00:06:48 -to 00:10:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P237-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P237.MTS" -ss 00:12:47 -to 00:15:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P237-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P237.MTS" -ss 00:17:37 -to 00:20:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P237-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P237.mp4" -ss 00:00:10 -to 00:03:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P237-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P237.mp4" -ss 00:06:09 -to 00:08:55 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P237-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P237.mp4" -ss 00:10:59 -to 00:13:43 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P237-planning-3.mp4"

# ==== P239 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P239.MTS" -ss 00:00:29 -to 00:02:44 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P239-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P239.MTS" -ss 00:04:02 -to 00:05:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P239-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P239.MTS" -ss 00:06:27 -to 00:08:44 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P239-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P239.MTS" -ss 00:00:16 -to 00:02:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P239-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P239.MTS" -ss 00:03:49 -to 00:05:12 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P239-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P239.MTS" -ss 00:06:14 -to 00:08:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P239-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P239.mp4" -ss 00:00:34 -to 00:02:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P239-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P239.mp4" -ss 00:04:07 -to 00:05:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P239-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P239.mp4" -ss 00:06:32 -to 00:08:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P239-planning-3.mp4"

# ==== P240 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P240.MTS" -ss 00:00:11 -to 00:08:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P240-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P240.MTS" -ss 00:09:38 -to 00:17:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P240-planning-2.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P240.MTS" -ss 00:00:07 -to 00:08:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P240-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P240.MTS" -ss 00:09:34 -to 00:17:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P240-planning-2.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P240.mp4" -ss 00:00:06 -to 00:08:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P240-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P240.mp4" -ss 00:09:33 -to 00:17:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P240-planning-2.mp4"

# ==== P241 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P241.MTS" -ss 00:00:46 -to 00:01:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P241-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P241.MTS" -ss 00:03:16 -to 00:03:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P241-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P241.MTS" -ss 00:05:14 -to 00:05:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P241-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P241.MTS" -ss 00:06:02 -to 00:06:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P241-planning-4.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P241.MTS" -ss 00:07:20 -to 00:09:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P241-planning-5.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P241.MTS" -ss 00:00:51 -to 00:01:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P241-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P241.MTS" -ss 00:03:21 -to 00:03:58 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P241-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P241.MTS" -ss 00:05:19 -to 00:05:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P241-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P241.MTS" -ss 00:06:07 -to 00:06:29 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P241-planning-4.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P241.MTS" -ss 00:07:25 -to 00:09:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P241-planning-5.mp4"

# Frontal cam
# MISSING DATA!

# ==== P242 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P242.MTS" -ss 00:01:02 -to 00:03:29 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P242-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P242.MTS" -ss 00:04:21 -to 00:05:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P242-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P242.MTS" -ss 00:06:37 -to 00:08:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P242-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P242.MTS" -ss 00:01:09 -to 00:03:36 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P242-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P242.MTS" -ss 00:04:28 -to 00:05:56 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P242-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P242.MTS" -ss 00:06:44 -to 00:08:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P242-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P242.mp4" -ss 00:00:10 -to 00:02:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P242-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P242.mp4" -ss 00:03:29 -to 00:04:57 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P242-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P242.mp4" -ss 00:05:45 -to 00:07:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P242-planning-3.mp4"

# ==== P243 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P243.MTS" -ss 00:02:38 -to 00:04:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P243-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P243.MTS" -ss 00:07:30 -to 00:08:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P243-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P243.MTS" -ss 00:09:58 -to 00:11:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P243-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P243.MTS" -ss 00:13:27 -to 00:15:11 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P243-planning-4.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P243.MTS" -ss 00:02:29 -to 00:04:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P243-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P243.MTS" -ss 00:07:21 -to 00:08:45 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P243-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P243.MTS" -ss 00:09:49 -to 00:11:18 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P243-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P243.MTS" -ss 00:13:18 -to 00:15:02 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P243-planning-4.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P243.mp4" -ss 00:00:08 -to 00:01:52 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P243-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P243.mp4" -ss 00:05:00 -to 00:06:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P243-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P243.mp4" -ss 00:07:28 -to 00:08:57 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P243-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P243.mp4" -ss 00:10:57 -to 00:12:41 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P243-planning-4.mp4"

# ==== P244 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P244.MTS" -ss 00:02:44 -to 00:04:14 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P244-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P244.MTS" -ss 00:05:56 -to 00:07:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P244-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P244.MTS" -ss 00:08:17 -to 00:09:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P244-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P244.MTS" -ss 00:02:28 -to 00:03:58 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P244-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P244.MTS" -ss 00:05:40 -to 00:07:10 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P244-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P244.MTS" -ss 00:08:01 -to 00:09:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P244-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P244.mp4" -ss 00:00:08 -to 00:01:38 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P244-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P244.mp4" -ss 00:03:20 -to 00:04:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P244-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P244.mp4" -ss 00:05:41 -to 00:06:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P244-planning-3.mp4"

# ==== P245 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P245.MTS" -ss 00:05:40 -to 00:07:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P245-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P245.MTS" -ss 00:08:54 -to 00:11:30 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P245-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P245.MTS" -ss 00:12:56 -to 00:14:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P245-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P245.MTS" -ss 00:05:37 -to 00:06:57 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P245-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P245.MTS" -ss 00:08:51 -to 00:11:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P245-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P245.MTS" -ss 00:12:53 -to 00:14:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P245-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P245.mp4" -ss 00:00:47 -to 00:02:07 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P245-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P245.mp4" -ss 00:04:01 -to 00:06:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P245-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P245.mp4" -ss 00:08:03 -to 00:10:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P245-planning-3.mp4"

# ==== P246 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P246.MTS" -ss 00:00:24 -to 00:01:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P246-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P246.MTS" -ss 00:02:48 -to 00:05:03 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P246-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P246.MTS" -ss 00:07:31 -to 00:09:08 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P246-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P246.MTS" -ss 00:00:07 -to 00:01:02 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P246-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P246.MTS" -ss 00:02:31 -to 00:04:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P246-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P246.MTS" -ss 00:07:14 -to 00:08:51 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P246-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P246.mp4" -ss 00:00:33 -to 00:01:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P246-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P246.mp4" -ss 00:02:57 -to 00:05:12 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P246-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P246.mp4" -ss 00:07:40 -to 00:09:17 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P246-planning-3.mp4"

# ==== P248 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P248.MTS" -ss 00:00:22 -to 00:04:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P248-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P248.MTS" -ss 00:05:53 -to 00:07:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P248-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P248.MTS" -ss 00:08:23 -to 00:09:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P248-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P248.MTS" -ss 00:00:36 -to 00:05:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P248-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P248.MTS" -ss 00:06:07 -to 00:07:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P248-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P248.MTS" -ss 00:08:37 -to 00:09:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P248-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P248.mp4" -ss 00:00:32 -to 00:04:56 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P248-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P248.mp4" -ss 00:06:03 -to 00:07:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P248-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P248.mp4" -ss 00:08:33 -to 00:09:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P248-planning-3.mp4"

# ==== P263 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P263.MTS" -ss 00:00:57 -to 00:03:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P263-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P263.MTS" -ss 00:05:32 -to 00:09:26 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P263-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P263.MTS" -ss 00:11:33 -to 00:16:24 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P263-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P263.MTS" -ss 00:00:50 -to 00:03:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P263-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P263.MTS" -ss 00:05:25 -to 00:09:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P263-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P263.MTS" -ss 00:11:26 -to 00:16:17 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P263-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P263.mp4" -ss 00:00:53 -to 00:03:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P263-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P263.mp4" -ss 00:05:28 -to 00:09:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P263-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P263.mp4" -ss 00:11:29 -to 00:16:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P263-planning-3.mp4"

# ==== P264 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P264.MTS" -ss 00:00:13 -to 00:02:53 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P264-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P264.MTS" -ss 00:03:59 -to 00:05:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P264-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P264.MTS" -ss 00:06:34 -to 00:08:27 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P264-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P264.MTS" -ss 00:09:27 -to 00:10:29 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P264-planning-4.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P264.MTS" -ss 00:00:06 -to 00:02:46 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P264-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P264.MTS" -ss 00:03:52 -to 00:05:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P264-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P264.MTS" -ss 00:06:27 -to 00:08:20 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P264-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P264.MTS" -ss 00:09:20 -to 00:10:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P264-planning-4.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P264.mp4" -ss 00:00:09 -to 00:02:49 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P264-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P264.mp4" -ss 00:03:55 -to 00:05:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P264-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P264.mp4" -ss 00:06:30 -to 00:08:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P264-planning-3.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P264.mp4" -ss 00:09:23 -to 00:10:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P264-planning-4.mp4"

# ==== P265 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P265.MTS" -ss 00:00:37 -to 00:01:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P265-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P265.MTS" -ss 00:02:27 -to 00:03:28 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P265-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P265.MTS" -ss 00:04:07 -to 00:04:47 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P265-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P265.MTS" -ss 00:00:31 -to 00:01:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P265-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P265.MTS" -ss 00:02:21 -to 00:03:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P265-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P265.MTS" -ss 00:04:01 -to 00:04:41 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P265-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P265.mp4" -ss 00:00:06 -to 00:01:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P265-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P265.mp4" -ss 00:01:56 -to 00:02:57 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P265-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P265.mp4" -ss 00:03:36 -to 00:04:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P265-planning-3.mp4"

# ==== P314 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P314.MTS" -ss 00:00:23 -to 00:03:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P314-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P314.MTS" -ss 00:07:00 -to 00:11:18 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P314-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P314.MTS" -ss 00:13:32 -to 00:16:22 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P314-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P314.MTS" -ss 00:00:05 -to 00:03:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P314-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P314.MTS" -ss 00:06:42 -to 00:11:00 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P314-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P314.MTS" -ss 00:13:14 -to 00:16:04 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P314-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P314.mp4" -ss 00:00:18 -to 00:03:32 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P314-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P314.mp4" -ss 00:06:55 -to 00:11:13 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P314-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P314.mp4" -ss 00:13:27 -to 00:16:17 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P314-planning-3.mp4"

# ==== P315 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P315.MTS" -ss 00:00:19 -to 00:04:41 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P315-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P315.MTS" -ss 00:06:27 -to 00:09:35 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P315-planning-2.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P315.MTS" -ss 00:00:15 -to 00:04:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P315-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P315.MTS" -ss 00:06:23 -to 00:09:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P315-planning-2.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P315.mp4" -ss 00:00:23 -to 00:04:45 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P315-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P315.mp4" -ss 00:06:31 -to 00:09:39 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P315-planning-2.mp4"

# ==== P316 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P316.MTS" -ss 00:01:39 -to 00:03:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P316-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P316.MTS" -ss 00:04:47 -to 00:06:45 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P316-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P316.MTS" -ss 00:08:31 -to 00:10:34 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P316-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P316.MTS" -ss 00:01:10 -to 00:02:37 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P316-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P316.MTS" -ss 00:04:18 -to 00:06:16 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P316-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P316.MTS" -ss 00:08:02 -to 00:10:05 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P316-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P316.mp4" -ss 00:00:37 -to 00:02:04 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P316-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P316.mp4" -ss 00:03:45 -to 00:05:43 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P316-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P316.mp4" -ss 00:07:29 -to 00:09:32 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P316-planning-3.mp4"

# ==== P317 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P317.MTS" -ss 00:00:42 -to 00:02:07 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P317-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P317.MTS" -ss 00:03:23 -to 00:08:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P317-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P317.MTS" -ss 00:09:47 -to 00:12:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P317-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P317.MTS" -ss 00:00:54 -to 00:02:19 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P317-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P317.MTS" -ss 00:03:35 -to 00:08:31 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P317-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P317.MTS" -ss 00:09:59 -to 00:12:52 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P317-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P317.mp4" -ss 00:00:56 -to 00:02:21 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P317-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P317.mp4" -ss 00:03:37 -to 00:08:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P317-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P317.mp4" -ss 00:10:01 -to 00:12:54 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P317-planning-3.mp4"

# ==== P318 ==== #

# Left cam
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P318.MTS" -ss 00:00:11 -to 00:03:23 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P318-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P318.MTS" -ss 00:05:33 -to 00:07:56 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P318-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/left-cam/left-cam-P318.MTS" -ss 00:09:44 -to 00:13:40 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/left-cam/left-cam-P318-planning-3.mp4"

# Right cam
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P318.MTS" -ss 00:00:13 -to 00:03:25 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P318-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P318.MTS" -ss 00:05:35 -to 00:07:58 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P318-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/right-cam/right-cam-P318.MTS" -ss 00:09:46 -to 00:13:42 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/right-cam/right-cam-P318-planning-3.mp4"

# Frontal cam
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P318.mp4" -ss 00:00:21 -to 00:03:33 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P318-planning-1.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P318.mp4" -ss 00:05:43 -to 00:08:06 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P318-planning-2.mp4"
ffmpeg -hide_banner -y -i "Classified/frontal-cam/frontal-cam-P318.mp4" -ss 00:09:54 -to 00:13:50 -c:v libx264 -c:a aac -vf scale=1920:1080,yadif -preset slow -crf 20 "Clean/frontal-cam/frontal-cam-P318-planning-3.mp4"
