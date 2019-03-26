#from flystim.options import OptionParser
import flystim.stim_server
from flystim.trajectory import RectangleTrajectory, Trajectory

def MovingSquareMap(name = 'MovingSquareMap',
                    azimuth_max = 180,
                    azimuth_min = 0,
                    elevation_max = 180,
                    elevation_min = 90,
                    square_width = 10,
                    velocity = 40):

    elevation_range = elevation_max - elevation_min
    azimuth_range = azimuth_max - azimuth_min
    line_duration = azimuth_range/velocity
    elevation_steps = int(elevation_range/square_width)
    duration = line_duration

    x = []
    y = []

    x.extend(((0,azimuth_max),(duration,azimuth_min)))
    y.extend(((0,elevation_min),(duration,elevation_min)))

    for shift in range(1,elevation_steps):
        x.append((duration,azimuth_max))
        y.append((duration,elevation_min+square_width*shift))
        duration += line_duration
        x.append((duration,azimuth_min))
        y.append((duration,elevation_min+square_width*shift))

    trajectory = RectangleTrajectory(x=x,
                                     y=y,
                                     w=square_width,
                                     h=square_width)
    trajectory = trajectory.to_dict()

    return trajectory, duration*1e3

def Loom(name = 'Loom',
         center_x = 90,
         center_y = 90,
         start_width = 0,
         end_width = 90,
         velocity = 60):

    duration = (end_width - start_width) / velocity

    w = []
    w.append((0,start_width))
    w.append((duration,end_width))

    trajectory = RectangleTrajectory(x=center_x,
                                     y=center_y,
                                     w=w,
                                     h=w)
    trajectory = trajectory.to_dict()

    return trajectory, duration*1e3
