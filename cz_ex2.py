from pymmcore_plus import CMMCorePlus
import useq
from useq import MDASequence, MDAEvent
import numpy as np
import tifffile as tf

# Create the core instance
mmc = CMMCorePlus().instance()
mmc.loadSystemConfiguration()

# Set camera mode to noise
mmc.setProperty("Camera", "Mode", "Noise")
print("Current camera mode:", mmc.getProperty("Camera", "Mode"))

# Define the function to modify images in real-time
def modify_image(image):
    modified_image = np.copy(image)
    # Iterate over each pixel in the image
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Check if pixel value is exactly 700
            if image[i, j] == 700:
                # Set neighboring pixels within a radius of 15 pixels to zero
                # This part of the code was generated using ChatGPT
                # Create a meshgrid and use Euclidean distance to make circular mask
                x, y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
                dist = np.sqrt((x - j)**2 + (y - i)**2)
                mask = dist <= 15
                modified_image[mask] = 0
    return modified_image

# Create an empty list to store frames
frames = []

# Define the frameReady event handler (separate thread)
@mmc.mda.events.frameReady.connect
def on_frame(image: np.ndarray, event: useq.MDAEvent):
    # Modify the image in real-time
    modified_image = modify_image(image)
    # Save the modified image in the frames stack
    frames.append(modified_image)

#Save stack of frames as TIFF file locally
@mmc.mda.events.sequenceFinished.connect
def on_end():
    # Convert the list of frames to a numpy array
    stack = np.stack(frames)

    # Save the stack as a single TIFF file
    tf.imwrite("CZex2_im.tif", stack)

# Define the MDA sequence for timelapse acquisition
mda_sequence = MDASequence(
    time_plan={"interval": 0.1, "loops": 100},
    channels=[
        {"config": "DAPI", "exposure": 10.0}
    ]
)

# Run the MDA acquisition
mmc.run_mda(mda_sequence)
