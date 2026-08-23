import glm
import typing

from enum import Enum, auto
from math import *

# Define várias opções possíveis para o movimento da câmera. Utilizado como uma abstração para evitar a dependência de métodos de entrada específicos do sistema de janelas.
class Camera_Movement(Enum):
    FORWARD = auto(),
    BACKWARD = auto(),
    LEFT = auto(),
    RIGHT = auto()

# Valores padrão da câmera
YAW:         Final[float] = -90.0
PITCH:       Final[float] =  0.0
SPEED:       Final[float] = 2.5
SENSITIVITY: Final[float] = 0.1
ZOOM:        Final[float] = 45.0

# Uma classe de câmera abstrata que processa a entrada e calcula os ângulos de Euler, vetores e matrizes correspondentes para uso no OpenGL
class Camera:
    # Atributos da câmera
    Position = glm.vec3()
    Front = glm.vec3()
    Up = glm.vec3()
    Right = glm.vec3()
    WorldUp = glm.vec3()

    # Ângulos de Euler
    Yaw: float
    Pitch: float

    # opções de câmera
    MovementSpeed: float
    MouseSensitivity: float
    Zoom: float

    @typing.overload
    def __init__(self, position: tuple, up: tuple, yaw: Yaw, pitch: Pitch):
        pass

    @typing.overload
    def __init__(
        self,
        posX: float,
        posY: float,
        posZ: float,
        upX: float,
        upY: float,
        upZ: float,
        yaw: Yaw,
        pitch: Pitch
    ):
        pass

    def __init__(
            self,
            position: tuple | None = None,
            up: tuple | None = None,

            posX: float | None = None,
            posY: float | None  = None,
            posZ: float | None = None,
            upX: float | None = None,
            upY: float | None = None,
            upZ: float | None = None,

            yaw: Yaw | None = None,
            pitch: Pitch | None = None,
        ):

        self.Front = glm.vec3(0.0, 0.0, -1.0)
        self.MovementSpeed = SPEED
        self.MouseSensitivity = SENSITIVITY
        self.Zoom = ZOOM

        if position is not None or up is not None:
            self.Position = glm.vec3(*(position or (0.0, 0.0, 0.0)))
            self.WorldUp  = glm.vec3(*(up or (0.0, 1.0, 0.0)))

        elif None not in (posX, posY, posZ, upX, upY, upZ):
            self.Position = glm.vec3(posX, posY, posZ)
            self.WorldUp  = glm.vec3(upX, upY, upZ)
        
        else:
            self.Position = glm.vec3(0.0, 0.0, 0.0)
            self.WorldUp  = glm.vec3(0.0, 1.0, 0.0)

        self.Yaw   = yaw if yaw is not None else YAW
        self.Pitch = pitch if pitch is not None else PITCH        
        
        self.updateCameraVectors()

    # # construtor com vetores
    # def __init__(self, position = glm.vec3(0.0, 0.0, 0.0), up = glm.vec3(0.0, 1.0, 0.0), yaw = YAW, pitch = PITCH):
    #     self.Front = glm.vec3(0.0, 0.0, -1.0)
    #     self.MovementSpeed = SPEED
    #     self.MouseSensitivity = SENSITIVITY
    #     self.Zoom = ZOOM
    #
    #     self.Position = position
    #     self.WorldUp = up
    #     self.Yaw = yaw
    #     self.Pitch = pitch
    #
    #     self.updateCameraVectors()

    # construtor com valores escalares
    # def __init__(self, posX, posY, posZ, upX, upY, upZ, yaw, pitch):
    #     self.Front = glm.vec3(0.0, 0.0, -1.0)
    #     self.MovementSpeed = SPEED
    #     self.MouseSensitivity = SENSITIVITY
    #     self.Zoom = ZOOM

    #     self.Position = glm.vec3(posX, posY, posZ)
    #     self.WorldUp = glm.vec3(upX, upY, upZ)
    #     self.Yaw = yaw
    #     self.Pitch = pitch

    #     self.updateCameraVectors()

    # retorna a matriz de visualização calculada usando ângulos de Euler e a matriz LookAt
    def GetViewMatrix(self):
        return glm.lookAt(
            self.Position,
            self.Position + self.Front,
            self.Up
        )

    # processa a entrada recebida de qualquer sistema de entrada do tipo teclado. Aceita um parâmetro de entrada na forma de um ENUM definido pela câmera (para abstraí-lo de sistemas de janelas)
    def ProcessKeyboard(self, direction, deltaTime):
        velocity = self.MovementSpeed * deltaTime

        if (direction == Camera_Movement.FORWARD):
            self.Position += velocity * self.Front
        if (direction == Camera_Movement.BACKWARD):
            self.Position -= velocity * self.Front
        if (direction == Camera_Movement.LEFT):
            self.Position -= velocity * self.Right
        if (direction == Camera_Movement.RIGHT):
            self.Position += velocity * self.Right

    # processa a entrada recebida de um sistema de entrada de mouse. Espera o valor de deslocamento nas direções x e y.
    def ProcessMouseMovement(self, xoffset, yoffset, constrainPitch = True):
        xoffset += self.MouseSensitivity
        yoffset += self.MouseSensitivity

        self.Yaw   += xoffset
        self.Pitch += yoffset

        # certifique-se de que a tela não seja invertida quando o pitch estiver fora dos limites
        if (constrainPitch):
            if (self.Pitch > 89.0):
                self.Pitch = 89.0
            if (self.Pitch < -89.0):
                self.Pitch = -89.0

        # atualiza os vetores Front, Right e Up usando os ângulos de Euler atualizados
        self.updateCameraVectors()

    # processa a entrada recebida de um evento de roda de rolagem do mouse. Requer entrada apenas no eixo vertical da roda.
    def ProcessMouseScroll(self, yoffset):
        self.Zoom -= yoffset

        if (self.Zoom < 1.0):
            self.Zoom = 1.0
        if (self.Zoom > 45.0):
            self.Zoom = 45.0

    # calcula o vetor frontal a partir dos ângulos de Euler (atualizados) da câmera
    def updateCameraVectors(self):
        # calcula o novo vetor Front
        front = glm.vec3()

        front.x = cos(glm.radians(self.Pitch)) * cos(glm.radians(self.Yaw))
        front.y = sin(glm.radians(self.Pitch))
        front.z = cos(glm.radians(self.Pitch)) * sin(glm.radians(self.Yaw))

        self.Front = glm.normalize(front)

        # também recalcule os vetores Direita e Cima
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp)) # Normaliza os vetores, pois o comprimento deles se aproxima de zero quanto mais você olha para cima ou para baixo, o que resulta em um movimento mais lento.

        self.Up = glm.normalize(glm.cross(self.Right, self.Front))

