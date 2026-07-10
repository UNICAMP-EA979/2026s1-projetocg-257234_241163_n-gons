import numpy as np

from .node import Node


class Camera(Node):
    '''
    Camera node, a perspective camera
    '''

    def __init__(self, name: str = "camera") -> None:
        '''
        Camera initilizer

        Args:
            name (str, optional): node name. Defaults to "camera".
        '''
        super().__init__(name)

        self.near_plane = 1.0
        self.far_plane = 10.0
        self.screen_width = 1920.0
        self.screen_height = 1080.0
        self.vertical_fov = 60.0
    
    @property
    def aspect_ratio(self) -> float:
        '''
        Camera aspect ratio

        Returns:
            float: aspect ratio
        '''
        return self.screen_width / self.screen_height

    @property
    def projection_matrix(self) -> np.ndarray:
        '''
        Camera projection matrix

        Returns:
            np.ndarray: 4x4 projection matrix
        '''

        matrix = np.zeros((4, 4))
        c = 1 / np.tan(np.radians(self.vertical_fov) / 2)
        matrix[0, 0] = c / self.aspect_ratio
        matrix[1, 1] = c
        matrix[2, 2] = - (self.far_plane + self.near_plane) / (self.far_plane - self.near_plane)
        matrix[2, 3] = - (2 * self.far_plane * self.near_plane) / (self.far_plane - self.near_plane)
        matrix[3, 2] = - 1

        return matrix