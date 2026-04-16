# Documentation

The requirements that this project was based on can be found in the `documentation` branch under `docs\requirements.md`

After the project has been completed we will merge this branch into main.

# Setup

### Production 
To turn the program into a packaged executable for production. 

### Development
To run the program from command line for development, one need to set up a `venv` using the `requirements.txt` file at the root this repo.

Once the `venv` is running open a terminal is said `venv` and run `python ./main.py`

# Basic Usage
For more detailed explanation of features please see the `docs\requirements.md`

### Loading data.
The data can be loaded using `File` button in the top right. From here you can select to load either the video or the wave forms. The video can be either a `.mp4` or `.mov`, the wave forms are loaded from HDF5 files whose extension is `.h5`. All of the selection is done through the host machines file explorer.

### Video Player
The video player is used like any other video player; containing a scrubber, pause/play button, and variable step sizes. Where this video player differs from traditional video players is you have the ability to trim off the beginning of the video, this feature is to enable the alignment of the wave form and video. It also allows the user to mark portions of the video for annotation which become highlighted in the timeline.

### Grapher
The grapher overlays two wave forms onto of each other with a bar in the center demarcating what current point where exactly the current time is. The wave form is lock to the video scrubber, i.e. moving the scrubber will change both the displayed frame and the corresponding wave form. Additionally there are tools on the left hand side of the pane that allow the user to cut off a portion of each wave forms beginning, which similarly to the video players trim feature allows the user to align the the two modalities.

### Annotations
The annotations are contained in a vertical pane on the right hand side of the window. The specifics of what each annotation contains can be seen in `docs\requirements.md`. To use start an annotation the user marks a portion of the video. This allows them to edit/add an annotation block. The blocks containing annotation like everything else are locked to the video scrubber. So when the user jumps to a portion of the video the accompanying annotations will be shown.


