import numpy as np


class TrackerManager:
    """
    TrackerManager quản lý ByteTrack từ BoxMOT.
    """

    def __init__(self):
        try:
            from boxmot.trackers.bytetrack.bytetrack import ByteTrack
        except Exception as e:
            raise ImportError(
                "Không import được ByteTrack. Hãy cài trong đúng env: pip install boxmot"
            ) from e

        self.tracker = ByteTrack(
            track_thresh=0.45,
            match_thresh=0.85,
            track_buffer=50,
            frame_rate=30
        )

    def update(self, detections, frame):
        if len(detections) == 0:
            detections = np.empty((0, 6), dtype=float)
        else:
            detections = np.asarray(detections, dtype=float)

        return self.tracker.update(detections, frame)