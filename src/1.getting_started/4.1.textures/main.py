import glfw
from OpenGL.GL import *
from typing import *
from numpy import *
from math import *
from ctypes import *
from shader import *
from PIL import Image

# configurações
SCR_WIDTH: Final[int] = 800
SCR_HEIGHT: Final[int] = 600

def main():
    # glfw: inicializar e configurar
    # --------------------------------------------------
    if (not glfw.init()):
        return

    # Criação de janela GLFW
    # --------------------------------------------------
    window = glfw.create_window(SCR_WIDTH, SCR_HEIGHT, "Learn PyOpenGL", None, None)

    if (not window):
        glfw.terminate()
        return

    # Centralizar a janela na tela
    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    monitor_width = mode.size.width
    monitor_height = mode.size.height

    # Calcular posição central
    pos_x = (monitor_width - SCR_WIDTH) // 2
    pos_y = (monitor_height - SCR_HEIGHT) // 2

    # Definir posição da janela
    glfw.set_window_pos(window, pos_x, pos_y)

    # Torne o contexto da janela o atual
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    # construir e compilar nosso programa de shader
    # --------------------------------------------------
    outShader = Shader("texture.vs", "texture.fs")

    # configurar dados de vértice (e buffer(s)) e configurar atributos de vértice
    # --------------------------------------------------
    vertices = array([
        # positions         # colors         # texture coords
        -0.5, -0.5,  0.0,   1.0, 0.0, 0.0,   0.0, 0.0, # inferior esquerdo
         0.5, -0.5,  0.0,   0.0, 1.0, 0.0,   1.0, 0.0, # inferior direito
         0.5,  0.5,  0.0,   0.0, 0.0, 1.0,   1.0, 1.0, # superior direito
        -0.5,  0.5,  0.0,   1.0, 1.0, 0.0,   0.0, 1.0  # superior esquerdo
    ], 'f')

    indices = array([
        0, 1, 2, # primeiro triângulo
        0, 2, 3  # segundo triângulo
    ], 'i')

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # texture coord attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(6 * sizeof(c_float)))
    glEnableVertexAttribArray(2)

    # carregar e criar uma textura
    # --------------------------------------------------
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture) # todas as operações GL_TEXTURE_2D subsequentes agora afetam este objeto de textura

    # define os parâmetros de repetição da textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # definir parâmetros de filtragem de textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    image = Image.open("res/textures/container.jpg")
    width = image.width
    height = image.height
    data = array(image, 'uint8')

    try:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    except:
        print("Falha ao carregar a textura")

    # loop de renderização
    # --------------------------------------------------
    while (not glfw.window_should_close(window)):
        # input
        # --------------------------------------------------
        processInput(window)

        # render
        # --------------------------------------------------
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # vincular textura
        glBindTexture(GL_TEXTURE_2D, texture)

        # renderiza o contêiner
        outShader.use()
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])

    # glfw: encerra, liberando todos os recursos do GLFW alocados anteriormente.
    # --------------------------------------------------
    glfw.terminate()

# processar toda a entrada: consultar a GLFW para saber se teclas relevantes foram pressionadas ou liberadas neste quadro e reagir de acordo
# --------------------------------------------------
def processInput(window):
    if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)

# glfw: sempre que o tamanho da janela é alterado (pelo SO ou por redimensionamento do usuário), esta função de callback é executada
# --------------------------------------------------
def framebuffer_size_callback(window, width, height):
    # certifique-se de que a viewport corresponda às novas dimensões da janela; observe que a largura e
    # a altura serão significativamente maiores do que as especificadas em telas Retina. 
    glViewport(0, 0, width, height)

if (__name__ == "__main__"):
    main()
