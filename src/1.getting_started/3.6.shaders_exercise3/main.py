import glfw
from OpenGL.GL import *
from typing import *
from numpy import *
from math import *
from ctypes import *
from shader import *

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
    outShader = Shader("shader.vs", "shader.fs")

    # configurar dados de vértice (e buffer(s)) e configurar atributos de vértice
    # --------------------------------------------------
    vertices = array([
        # positions         # colors
        -0.5, -0.5,  0.0,   1.0, 0.0, 0.0,
         0.5, -0.5,  0.0,   0.0, 1.0, 0.0,
         0.0,  0.5,  0.0,   0.0, 0.0, 1.0
    ], 'f')

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    # primeiro vincule o Vertex Array Object, depois vincule e configure o(s) buffer(s) de vértices e, em seguida, configure o(s) atributo(s) de vértice.
    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # Você pode desvincular o VAO posteriormente para que outras chamadas de VAO não modifiquem acidentalmente este VAO, mas isso raramente acontece. Modificar outros
    # VAOs exige uma chamada para glBindVertexArray de qualquer forma, então geralmente não desvinculamos VAOs (nem VBOs) quando não é diretamente necessário.
    # glBindVertexArray(0)

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

        # renderiza o triângulo
        outShader.use()
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])

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
