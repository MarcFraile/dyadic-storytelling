# UpDySt: the Uppsala Dyadic Storytelling dataset

This repository contains code for the article *"UpDySt: the Uppsala Dyadic Storytelling dataset"* by Marc Fraile, Natalia Calvo-Barajas, Anastasia Akkuzu, Giovanna Varni, Joakim Lindblad, Nataša Sladoje and Ginevra Castellano.

It is organized as a "monorepo": each top-level directory is a separate codebase used for the research project.

* [storytelling-app/](storytelling-app/) contains the storytelling board game used in the study. It is implemented as a static webpage, using basic web technologies (HTML, CSS, JavaScript).
* [network-analysis/](network-analysis/) contains code related to analysing and partitioning the friendship network we obtained from asking participants to nominate their best friends. It also contains code related to the statistical analysis of questionnaire responses.
* [av-processing/](av-processing/) contains code for processing the original pair-level recordings into synchronized round-level recordings.
* [feature-extraction/](feature-extraction/) contains code for obtaining per-frame OpenFace and OpenPose features; with a re-constructed continuous identity over time.
* [feature-analysis/](feature-analysis/) contains code related to extracting summary statistics from the frame-by-frame features, and training Machine Learning models to predict the experimental condition (high-rapport pairs vs. low-rapport pairs).
