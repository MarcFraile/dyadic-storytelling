# Audio / Video Processing

This directory contains code for the processing of the original video sources (left camera, right camera, and frontal camera), as well as the original audio sources (per-child head-mounted microphones).

## Folder Structure

* `Raw/` contains the original files, without classifying.
    * It contains one folder for each storage device (phone, SD card, etc.) used for recording.
    * Each folder contains all original files copied over from that device, using the original naming scheme.
* `Classified/` contains the original files, classified and renamed.
    * It contains one folder for each logical source (left cam, headset audio, etc.) used for recording.
    * Each file is named according to its logical source, its pair ID, and if relevant a round number.
* `Clean/` contains files after the first processing step.
    * It contains one folder for each logical source.
    * Each file is named according to its logical source, its pair ID, its round number, and if relevant its stage (planning vs. presentation).
    * Video:
        * Video files are processed with ffmpeg commands, preserved in `scripts/example_call.sh` for reproducibility.
        * Video files are reformatted for homogeneity, as well as somewhat compressed.
        * Left, Right, and Center camera files are cut at second-level precision into individual rounds of the game (only the planning phase).
        * Presentation camera files were already separated into rounds in their raw form.
    * Audio:
        * Audio files are processed in Audacity (free audio editing software).
        * Audio files are offset-centered and normalized to -1dB, per-channel.
        * Audio files are cut into each planning and presentation phase (per-round).
* `Cut/` contains files after automatic synchronization.
    * It contains one folder for each logical source.
    * Each file is named according to its logical source, its pair ID, its round number, and if relevant its stage (planning vs. presentation).
