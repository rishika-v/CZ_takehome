from pymmcore_plus import CMMCorePlus
import useq
from useq import MDASequence, Position
import numpy as np
import tifffile as tf

#Full Code usage and documentation from: https://pymmcore-plus.github.io/pymmcore-plus/guides/mda_engine/

# Create the core instance
mmc = CMMCorePlus().instance()
mmc.loadSystemConfiguration()

# Create an empty list to store frames
frames = []

#Create different threads using event handlers to receive the frame and combine to create tiff file
#Usage and documentation from: https://pymmcore-plus.github.io/pymmcore-plus/api/events/

#Collect frames to build dataset
@mmc.mda.events.frameReady.connect 
def on_frame(image: np.ndarray, event: useq.MDAEvent):
    # Append the received frame to the list
    frames.append(image)

#Save stack of frames as TIFF file locally
@mmc.mda.events.sequenceFinished.connect
def on_end():
    # Convert the list of frames to a numpy array
    stack = np.stack(frames)

    # Save the stack as a single TIFF file
    tf.imwrite("CZex1_data.tif", stack)

# Define the positions in a 3x3 grid with 500 um spacing
positions = [Position(x=i*500, y=j*500, z=0) for i in range(3) for j in range(3)]

# Define the MDA sequence: following given parameters of 2 channels, 12 z slices
mda_sequence = MDASequence(
    channels=[
        {"config": "DAPI", "exposure": 50}, 
        {"config": "FITC", "exposure": 50},
    ],
    z_plan={"range": 1.1, "step": 0.1},  # 12 z slices spaced by 0.1 um
    stage_positions=positions
)

# Run the MDA sequence
mmc.run_mda(mda_sequence)