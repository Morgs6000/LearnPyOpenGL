import glfw
from OpenGL.GL import *
from typing import *
from numpy import *

# configurações
SCR_WIDTH: Final[int] = 800
SCR_HEIGHT: Final[int] = 600

vertexShaderSource = """
    #version 330 core
    layout (location = 0) in vec3 aPos;

    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
    }
"""

fragmentShaderSource = """
    #version 330 core
    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
    } 
"""

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

    # vertex shader
    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShader, vertexShaderSource)
    glCompileShader(vertexShader)

    # verificar erros de compilação de shaders
    success: int
    infoLog: str

    success = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(vertexShader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog)

    # fragment shader
    fragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShader, fragmentShaderSource)
    glCompileShader(fragmentShader)

    # verificar erros de compilação de shaders
    success = glGetShaderiv(fragmentShader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(fragmentShader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog)

    # link shaders
    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragmentShader)
    glLinkProgram(shaderProgram)

    # verificar erros de vinculação
    success = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
    if (not success):
        infoLog = glGetProgramInfoLog(shaderProgram)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog)

    glDeleteShader(vertexShader)
    glDeleteShader(fragmentShader)

    # configurar dados de vértice (e buffer(s)) e configurar atributos de vértice
    # --------------------------------------------------
    firstTriangle = array([
        # primeiro triângulo
        -0.9,  -0.5,  0.0,
         0.0,  -0.5,  0.0,
        -0.45,  0.5,  0.0
    ], 'f')

    secondTriangle = array([
        # segundo triângulo
         0.0,  -0.5,  0.0,
         0.9,  -0.5,  0.0,
         0.45,  0.5,  0.0
    ], 'f')

    VAOs = glGenVertexArrays(2) # também podemos gerar múltiplos VAOs ou buffers ao mesmo tempo
    VBOs = glGenBuffers(2)

    # configuração do primeiro triângulo
    # --------------------------------------------------
    glBindVertexArray(VAOs[0])

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[0])
    glBufferData(GL_ARRAY_BUFFER, firstTriangle, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # Os atributos de vértice permanecem os mesmos
    glEnableVertexAttribArray(0)

    # glBindVertexArray(0) # não é necessário desfazer a vinculação, pois vinculamos diretamente um VAO diferente nas próximas linhas

    # configuração do segundo triângulo
    # --------------------------------------------------
    glBindVertexArray(VAOs[1]) # observe que agora vinculamos a um VAO diferente

    glBindBuffer(GL_ARRAY_BUFFER, VBOs[1]) # e um VBO diferente
    glBufferData(GL_ARRAY_BUFFER, secondTriangle, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # como os dados dos vértices estão compactados, também podemos especificar 0 como o stride do atributo de vértice para deixar o OpenGL determiná-lo
    glEnableVertexAttribArray(0)

    # glBindVertexArray(0) # também não é estritamente necessário, mas cuidado com chamadas que possam afetar VAOs enquanto este estiver vinculado (como vincular *element buffer objects* ou habilitar/desabilitar atributos de vértice)

    # descomente esta chamada para desenhar polígonos em wireframe.
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

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

        glUseProgram(shaderProgram)

        # desenha o primeiro triângulo usando os dados do primeiro VAO
        glBindVertexArray(VAOs[0])
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # então, desenhamos o segundo triângulo usando os dados do segundo VAO
        glBindVertexArray(VAOs[1])
        glDrawArrays(GL_TRIANGLES, 0, 3)

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(2, [VAOs])
    glDeleteBuffers(2, [VBOs])
    glDeleteProgram(shaderProgram)

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
