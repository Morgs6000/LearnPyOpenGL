import glfw
import glm
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
    outShader = Shader("coordinate_systems.vs", "coordinate_systems.fs")

    # configurar dados de vértice (e buffer(s)) e configurar atributos de vértice
    # --------------------------------------------------
    vertices = array([
        # positions         # texture coords
        -0.5, -0.5,  0.0,   0.0, 0.0, # inferior esquerdo
         0.5, -0.5,  0.0,   1.0, 0.0, # inferior direito
         0.5,  0.5,  0.0,   1.0, 1.0, # superior direito
        -0.5,  0.5,  0.0,   0.0, 1.0  # superior esquerdo
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
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # texture coord attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # carregar e criar uma textura
    # --------------------------------------------------

    # texture 1
    # --------------------------------------------------
    texture1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture1) # todas as operações GL_TEXTURE_2D subsequentes agora afetam este objeto de textura

    # define os parâmetros de repetição da textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # definir parâmetros de filtragem de textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    image = Image.open("res/textures/container.jpg")

    image = image.transpose(Image.FLIP_TOP_BOTTOM) # instrui a stb_image.h a inverter as texturas carregadas no eixo Y.
    
    width = image.width
    height = image.height
    data = array(image, 'uint8')

    try:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    except:
        print("Falha ao carregar a textura")

    # texture 2
    # --------------------------------------------------
    texture2 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture2) # todas as operações GL_TEXTURE_2D subsequentes agora afetam este objeto de textura

    # define os parâmetros de repetição da textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT) # define o modo de repetição da textura como GL_REPEAT (método padrão)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # definir parâmetros de filtragem de textura
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # carregar imagem, criar textura e gerar mipmaps
    image = Image.open("res/textures/awesomeface.png")

    image = image.transpose(Image.FLIP_TOP_BOTTOM) # instrui a stb_image.h a inverter as texturas carregadas no eixo Y.

    width = image.width
    height = image.height
    data = array(image, 'uint8')

    try:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
    except:
        print("Falha ao carregar a textura")

    # informar ao OpenGL, para cada sampler, a qual unidade de textura ele pertence (isso só precisa ser feito uma vez)
    # --------------------------------------------------
    outShader.use()
    outShader.setInt("texture1", 0)
    outShader.setInt("texture2", 1)

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

        # vincular texturas às unidades de textura correspondentes
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture2)

        # ativar shader
        outShader.use()

        # criar transformações
        model = glm.mat4(1.0) # certifique-se de inicializar a matriz como a matriz identidade primeiro
        view = glm.mat4(1.0)
        projection = glm.mat4(1.0)

        model = glm.rotate(model, glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))
        view = glm.translate(view, glm.vec3(0.0, 0.0, -3.0))
        projection = glm.perspective(
            glm.radians(45.0), 
            SCR_WIDTH / SCR_HEIGHT, 
            0.1, 
            100.0
        )

        # obtém as localizações dos uniforms de matriz
        modelLoc = glGetUniformLocation(outShader.ID, "model")
        viewLoc = glGetUniformLocation(outShader.ID, "view")

        # passe-os para os shaders (3 maneiras diferentes)
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view))

        # nota: atualmente definimos a matriz de projeção a cada quadro, mas, como ela raramente muda, geralmente é uma boa prática defini-la apenas uma vez, fora do loop principal.
        outShader.setMat4("projection", projection)

        # renderiza o contêiner
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
