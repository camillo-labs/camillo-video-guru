"""Velocity to motion blur: how much directional blur a layer moving v pixels per frame should get.

Same rule as the playbook: references/motion.md for the
rule ("anything over about 12 px/frame gets directional blur, about 0.12 px of blur per px/frame, capped at
22 px") and remotion-kit/mblur.tsx for the nine preset blur steps and the dominant-axis choice. There the blur
is an SVG feGaussianBlur; here it is the same Gaussian along one axis in OpenCV.

    sigma = sigma_for_velocity(vx)                 # 0 for a slow move, up to 22 for a very fast one
    img = directional_blur(img, vx, vy)            # blur along whichever axis moves faster
    v = velocity(lambda f: pos_px(f), frame)       # px/frame of any position function
"""
import numpy as np
import cv2

BLUR_PER_PX = 0.12                         # px of blur per px/frame of travel (motion.md)
BLUR_CAP = 22.0                            # largest blur, px
STEPS = (0, 2, 4, 6, 8, 11, 14, 18, 22)    # mblur.tsx presets: the blur snaps to the nearest one


def sigma_for_velocity(v, quantise=True):
    """Gaussian sigma in px for a layer moving v px/frame (the sign is ignored). With quantise on, snaps to the
    nearest preset step as mblur.tsx does, which stops the blur flickering between neighbouring values from one
    frame to the next. 0 means no blur."""
    s = min(BLUR_CAP, abs(float(v)) * BLUR_PER_PX)
    if not quantise:
        return s
    return float(min(STEPS, key=lambda a: abs(a - s)))


def velocity(position, frame):
    """Speed in px/frame of position(f) at a frame: the central difference over one frame, as vel() in mblur.tsx."""
    return position(frame + 0.5) - position(frame - 0.5)


def directional_blur(img, vx, vy=0.0, quantise=True):
    """Gaussian blur of a uint8 image along the axis the layer moves fastest on, sized by that axis's speed.
    Returns img itself when the move is too slow to need blur."""
    horizontal = abs(vx) >= abs(vy)
    s = sigma_for_velocity(vx if horizontal else vy, quantise)
    if s <= 0:
        return img
    n = 2 * int(np.ceil(3 * s)) + 1
    if horizontal:
        return cv2.GaussianBlur(img, (n, 1), sigmaX=s, sigmaY=0, borderType=cv2.BORDER_REFLECT)
    return cv2.GaussianBlur(img, (1, n), sigmaX=0, sigmaY=s, borderType=cv2.BORDER_REFLECT)
