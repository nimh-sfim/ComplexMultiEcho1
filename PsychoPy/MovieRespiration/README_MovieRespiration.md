# Movie viewing with cued breathing and cued breathing (no movie) tasks

The psychopy script to run is [SpringMovieResp.py](SpringMovieResp.py)

Stimulus conditions:

- There is always a cued breathing task where a hollow circle gets larger and smaller and participants are instructed
to inhale when the circle gets larger and exhale when the circle gets smaller
- The task can include just the cued breathing or also a move with audio [spring-blender-open-movie.mp4](spring-blender-open-movie.mp4)
from: <https://studio.blender.org/films/spring/> ([Creative Commons Attribution 4.0 license](https://studio.blender.org/films/spring/pages/about/))
- The breathing pattern uses frequency modulation to shift between 4s and 6s breathing cycles every 60sec and with amplitude modulation
so that the slower breaths are also deeper breaths
- There are 21sec of breathing before the movie, the movie is 420sec, and there are 15sec of paced breathing after the movie
- For the cued breathing only runs, there is 456sec of cued breathing
  - [ViewingRespirationPatterns.ipynb](ViewingRespirationPatterns.ipynb) was used to create the respiration patterns and is a nice place to see how the patterns were created
- There are 3 different breathing cycles (A, B, & C) that all follow the same FM & AM pattern, but start at
a different point in the cycle so that the points where breathing is deepest and slowest is different between runs.
  - [IdealBreathingPattern_RunA.tsv](IdealBreathingPattern_RunA.tsv) (and ...RunB and ...RunC) are the diameters of the
  circle over time. These can be used for visualization and comparision to behavioral data, but are not used by the Psychopy script
