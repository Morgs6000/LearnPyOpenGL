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
    outShader = Shader("transform.vs", "transform.fs")

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

        # criar transformações
        transform = glm.mat4(1.0) # Certifique-se de inicializar a matriz como uma matriz identidade primeiro.
        transform = glm.rotate(transform, glfw.get_time(), glm.vec3(0.0, 0.0, 1.0)) # inverti a ordem
        transform = glm.translate(transform, glm.vec3(0.5, -0.5, 0.5)) # inverti a ordem

        # obtém a localização do uniform da matriz e define a matriz
        outShader.use()
        transformLoc = glGetUniformLocation(outShader.ID, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(transform))

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

"""
Por que nosso contêiner agora gira pela tela?
== ===================================================
Lembre-se de que a multiplicação de matrizes é aplicada na ordem inversa. Assim, desta vez, uma translação é aplicada primeiro ao contêiner, posicionando-o no canto inferior direito da tela. Após a translação, a rotação é aplicada ao contêiner já transladado.

Uma transformação de rotação também é conhecida como transformação de mudança de base quando analisamos a álgebra linear mais a fundo. Como estamos alterando a base do contêiner, as translações subsequentes moverão o contêiner com base nos novos vetores da base. Uma vez que o vetor tenha sido levemente rotacionado, as translações verticais, por exemplo, também ocorrerão de forma ligeiramente inclinada.

Se aplicássemos as rotações primeiro, elas ocorreriam em torno da origem de rotação (0,0,0); porém, como o contêiner é transladado antes, sua origem de rotação deixa de ser (0,0,0), fazendo com que ele pareça girar em torno da origem da cena.

Se você teve dificuldade para visualizar ou compreender isso, não se preocupe. Ao experimentar com transformações, você logo pegará o jeito; tudo o que é preciso é prática e experiência.
"""

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
