import glfw
import glm
from OpenGL.GL import *
from typing import *
from numpy import *
from math import *
from ctypes import *
from shader import *
from camera import *
from PIL import Image

# configurações
SCR_WIDTH: Final[int] = 800
SCR_HEIGHT: Final[int] = 600

def main():
    global camera
    global deltaTime, lastFrame
    global firstMouse, lastX, lastY

    # câmera
    camera = Camera(glm.vec3(0.0, 0.0, 3.0))
    lastX = SCR_WIDTH / 2.0
    lastY = SCR_HEIGHT / 2.0
    firstMouse = True

    # tempo
    deltaTime = 0.0
    lastFrame = 0.0

    # iluminação
    lightPos = glm.vec3(1.2, 1.0, 2.0)

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
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # instruir o GLFW a capturar o mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # configurar estado global do OpenGL
    # --------------------------------------------------
    glEnable(GL_DEPTH_TEST)

    # construir e compilar nosso programa de shader
    # --------------------------------------------------
    lightingShader = Shader("multiple_lights.vs", "multiple_lights.fs")
    lightCubeShader = Shader("light_cube.vs", "light_cube.fs")

    # configurar dados de vértice (e buffer(s)) e configurar atributos de vértice
    # --------------------------------------------------
    vertices = array([
        # positions         # normals           # texture coords
        -0.5, -0.5, -0.5,   -1.0,  0.0,  0.0,   0.0, 0.0,
        -0.5, -0.5,  0.5,   -1.0,  0.0,  0.0,   1.0, 0.0,
        -0.5,  0.5,  0.5,   -1.0,  0.0,  0.0,   1.0, 1.0,
        -0.5, -0.5, -0.5,   -1.0,  0.0,  0.0,   0.0, 0.0,
        -0.5,  0.5,  0.5,   -1.0,  0.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,   -1.0,  0.0,  0.0,   0.0, 1.0,
        
         0.5, -0.5,  0.5,    1.0,  0.0,  0.0,   0.0, 0.0,
         0.5, -0.5, -0.5,    1.0,  0.0,  0.0,   1.0, 0.0,
         0.5,  0.5, -0.5,    1.0,  0.0,  0.0,   1.0, 1.0,
         0.5, -0.5,  0.5,    1.0,  0.0,  0.0,   0.0, 0.0,
         0.5,  0.5, -0.5,    1.0,  0.0,  0.0,   1.0, 1.0,
         0.5,  0.5,  0.5,    1.0,  0.0,  0.0,   0.0, 1.0,
        
        -0.5, -0.5, -0.5,    0.0, -1.0,  0.0,   0.0, 0.0,
         0.5, -0.5, -0.5,    0.0, -1.0,  0.0,   1.0, 0.0,
         0.5, -0.5,  0.5,    0.0, -1.0,  0.0,   1.0, 1.0,
        -0.5, -0.5, -0.5,    0.0, -1.0,  0.0,   0.0, 0.0,
         0.5, -0.5,  0.5,    0.0, -1.0,  0.0,   1.0, 1.0,
        -0.5, -0.5,  0.5,    0.0, -1.0,  0.0,   0.0, 1.0,
        
        -0.5,  0.5,  0.5,    0.0,  1.0,  0.0,   0.0, 0.0,
         0.5,  0.5,  0.5,    0.0,  1.0,  0.0,   1.0, 0.0,
         0.5,  0.5, -0.5,    0.0,  1.0,  0.0,   1.0, 1.0,
        -0.5,  0.5,  0.5,    0.0,  1.0,  0.0,   0.0, 0.0,
         0.5,  0.5, -0.5,    0.0,  1.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,    0.0,  1.0,  0.0,   0.0, 1.0,
        
         0.5, -0.5, -0.5,    0.0,  0.0, -1.0,   0.0, 0.0,
        -0.5, -0.5, -0.5,    0.0,  0.0, -1.0,   1.0, 0.0,
        -0.5,  0.5, -0.5,    0.0,  0.0, -1.0,   1.0, 1.0,
         0.5, -0.5, -0.5,    0.0,  0.0, -1.0,   0.0, 0.0,
        -0.5,  0.5, -0.5,    0.0,  0.0, -1.0,   1.0, 1.0,
         0.5,  0.5, -0.5,    0.0,  0.0, -1.0,   0.0, 1.0,
        
        -0.5, -0.5,  0.5,    0.0,  0.0,  1.0,   0.0, 0.0,
         0.5, -0.5,  0.5,    0.0,  0.0,  1.0,   1.0, 0.0,
         0.5,  0.5,  0.5,    0.0,  0.0,  1.0,   1.0, 1.0,
        -0.5, -0.5,  0.5,    0.0,  0.0,  1.0,   0.0, 0.0,
         0.5,  0.5,  0.5,    0.0,  0.0,  1.0,   1.0, 1.0,
        -0.5,  0.5,  0.5,    0.0,  0.0,  1.0,   0.0, 1.0
    ], 'f')

    # posiciona todos os contêineres
    cubePositions = [
        glm.vec3( 0.0,  0.0,  0.0),
        glm.vec3( 2.0,  5.0, -15.0),
        glm.vec3(-1.5, -2.2, -2.5),
        glm.vec3(-3.8, -2.0, -12.3),
        glm.vec3( 2.4, -0.4, -3.5),
        glm.vec3(-1.7,  3.0, -7.5),
        glm.vec3( 1.3, -2.0, -2.5),
        glm.vec3( 1.5,  2.0, -2.5),
        glm.vec3( 1.5,  0.2, -1.5),
        glm.vec3(-1.3,  1.0, -1.5)
    ]

    # posições das luzes pontuais
    pointLightPositions = [
        glm.vec3( 0.7,  0.2,  2.0),
        glm.vec3( 2.3, -3.3, -4.0),
        glm.vec3(-4.0,  2.0, -12.0),
        glm.vec3( 0.0,  0.0, -3.0)
    ]

    cubeVAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    glBindVertexArray(cubeVAO)

    # position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # normal attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    glEnableVertexAttribArray(1)

    # texture attribute
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(6 * sizeof(c_float)))
    glEnableVertexAttribArray(2)

    # segundo, configure o VAO da luz (o VBO permanece o mesmo; os vértices são os mesmos para o objeto de luz, que também é um cubo 3D)
    lightCubeVAO = glGenVertexArrays(1)
    glBindVertexArray(lightCubeVAO)

    # precisamos apenas vincular o VBO (para associá-lo ao glVertexAttribPointer), sem necessidade de preenchê-lo; os dados do VBO já contêm tudo o que precisamos (ele já está vinculado, mas fazemos isso novamente para fins didáticos)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    # observe que atualizamos o stride do atributo de posição da lâmpada para refletir os dados atualizados do buffer
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(c_float), c_void_p(0))
    glEnableVertexAttribArray(0)

    # carregar texturas (agora usamos uma função utilitária para manter o código mais organizado)
    # --------------------------------------------------
    diffuseMap = loadTexture("res/textures/container2.png")
    specularMap = loadTexture("res/textures/container2_specular.png")

    # configuração do shader
    # --------------------------------------------------
    lightingShader.use()
    lightingShader.setInt("material.diffuse", 0)
    lightingShader.setInt("material.specular", 1)

    # loop de renderização
    # --------------------------------------------------
    while (not glfw.window_should_close(window)):
        # lógica de tempo por quadro
        # --------------------------------------------------
        currentFrame = glfw.get_time()
        deltaTime = currentFrame - lastFrame
        lastFrame = currentFrame

        # input
        # --------------------------------------------------
        processInput(window)

        # render
        # --------------------------------------------------
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # certifique-se de ativar o shader ao definir uniforms ou desenhar objetos
        lightingShader.use()
        lightingShader.setVec3("viewPos", camera.Position)
        lightingShader.setFloat("material.shininess", 32.0)

        '''
        Aqui, definimos todos os *uniforms* para os 5 ou 6 tipos de luz que possuímos. Precisamos defini-los manualmente e indexar
        a estrutura `PointLight` correta no *array* para configurar cada variável *uniform*. Isso pode ser feito de uma forma mais elegante em termos de código,
        definindo os tipos de luz como classes e configurando seus valores nelas, ou utilizando uma abordagem de *uniforms* mais eficiente
        por meio de *Uniform Buffer Objects* — mas esse é um assunto que abordaremos no tutorial de "GLSL Avançado".
        '''

        # luz direcional
        lightingShader.setVec3("dirLight.direction", glm.vec3(-0.2, -1.0, -0.3))
        lightingShader.setVec3("dirLight.ambient", glm.vec3(0.05, 0.05, 0.05))
        lightingShader.setVec3("dirLight.diffuse", glm.vec3(0.4, 0.4, 0.4))
        lightingShader.setVec3("dirLight.specular", glm.vec3(0.5, 0.5, 0.5))

        # luz pontual 1
        lightingShader.setVec3("pointLights[0].position", pointLightPositions[0])
        lightingShader.setVec3("pointLights[0].ambient", glm.vec3(0.05, 0.05, 0.05))
        lightingShader.setVec3("pointLights[0].diffuse", glm.vec3(0.8, 0.8, 0.8))
        lightingShader.setVec3("pointLights[0].specular", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setFloat("pointLights[0].constant", 1.0)
        lightingShader.setFloat("pointLights[0].linear", 0.09)
        lightingShader.setFloat("pointLights[0].quadratic", 0.032)

        # luz pontual 2
        lightingShader.setVec3("pointLights[1].position", pointLightPositions[1])
        lightingShader.setVec3("pointLights[1].ambient", glm.vec3(0.05, 0.05, 0.05))
        lightingShader.setVec3("pointLights[1].diffuse", glm.vec3(0.8, 0.8, 0.8))
        lightingShader.setVec3("pointLights[1].specular", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setFloat("pointLights[1].constant", 1.0)
        lightingShader.setFloat("pointLights[1].linear", 0.09)
        lightingShader.setFloat("pointLights[1].quadratic", 0.032)

        # luz pontual 3
        lightingShader.setVec3("pointLights[2].position", pointLightPositions[2])
        lightingShader.setVec3("pointLights[2].ambient", glm.vec3(0.05, 0.05, 0.05))
        lightingShader.setVec3("pointLights[2].diffuse", glm.vec3(0.8, 0.8, 0.8))
        lightingShader.setVec3("pointLights[2].specular", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setFloat("pointLights[2].constant", 1.0)
        lightingShader.setFloat("pointLights[2].linear", 0.09)
        lightingShader.setFloat("pointLights[2].quadratic", 0.032)

        # luz pontual 4
        lightingShader.setVec3("pointLights[3].position", pointLightPositions[3])
        lightingShader.setVec3("pointLights[3].ambient", glm.vec3(0.05, 0.05, 0.05))
        lightingShader.setVec3("pointLights[3].diffuse", glm.vec3(0.8, 0.8, 0.8))
        lightingShader.setVec3("pointLights[3].specular", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setFloat("pointLights[3].constant", 1.0)
        lightingShader.setFloat("pointLights[3].linear", 0.09)
        lightingShader.setFloat("pointLights[3].quadratic", 0.032)

        # holofote
        lightingShader.setVec3("spotLight.position", camera.Position)
        lightingShader.setVec3("spotLight.direction", camera.Front)
        lightingShader.setVec3("spotLight.ambient", glm.vec3(0.0, 0.0, 0.0))
        lightingShader.setVec3("spotLight.diffuse", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setVec3("spotLight.specular", glm.vec3(1.0, 1.0, 1.0))
        lightingShader.setFloat("spotLight.constant", 1.0)
        lightingShader.setFloat("spotLight.linear", 0.09)
        lightingShader.setFloat("spotLight.quadratic", 0.032)
        lightingShader.setFloat("spotLight.cutOff", cos(glm.radians(12.5)))
        lightingShader.setFloat("spotLight.outerCutOff", cos(glm.radians(15.0)))

        # transformações de visualização/projeção
        projection = glm.perspective( 
            glm.radians(camera.Zoom),
            SCR_WIDTH / SCR_HEIGHT, 
            0.1, 
            100.0
        )
        view = camera.GetViewMatrix()

        lightingShader.setMat4("projection", projection)
        lightingShader.setMat4("view", view)

        # transformação do mundo
        model = glm.mat4(1.0)
        lightingShader.setMat4("model", model)

        # vincular mapa de difusão
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, diffuseMap)

        # vincular mapa especular
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, specularMap)

        # renderizar contêineres
        glBindVertexArray(cubeVAO)

        for i in range(10):
            # calcula a matriz de modelo para cada objeto e a passa para o shader antes de desenhar
            model = glm.mat4(1.0)
            model = glm.translate(model, cubePositions[i])
            angle = 20.0 * i
            model = glm.rotate(model, glm.radians(angle), glm.vec3(0.5, 1.0, 0.0))
            lightingShader.setMat4("model", model)

            glDrawArrays(GL_TRIANGLES, 0, 36)

        # também desenhe o(s) objeto(s) de luminária
        lightCubeShader.use()
        lightCubeShader.setMat4("projection", projection)
        lightCubeShader.setMat4("view", view)

        # agora desenhamos tantas lâmpadas quantas forem as nossas luzes pontuais.
        glBindVertexArray(cubeVAO)

        for i in range(4):
            model = glm.mat4(1.0)
            model = glm.translate(model, pointLightPositions[i])
            model = glm.scale(model, glm.vec3(0.2)) # um cubo menor
            lightCubeShader.setMat4("model", model)

            glDrawArrays(GL_TRIANGLES, 0, 36)

        # glfw: troca os buffers e processa eventos de E/S (teclas pressionadas/liberadas, movimento do mouse, etc.)
        # --------------------------------------------------
        glfw.swap_buffers(window)
        glfw.poll_events()

    # opcional: desalocar todos os recursos assim que não forem mais necessários:
    # --------------------------------------------------
    glDeleteVertexArrays(1, [cubeVAO])
    glDeleteVertexArrays(1, [lightCubeVAO])
    glDeleteBuffers(1, [VBO])

    # glfw: encerra, liberando todos os recursos do GLFW alocados anteriormente.
    # --------------------------------------------------
    glfw.terminate()

# processar toda a entrada: consultar a GLFW para saber se teclas relevantes foram pressionadas ou liberadas neste quadro e reagir de acordo
# --------------------------------------------------
def processInput(window): 
    global camera

    if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, True)

    if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
        camera.ProcessKeyboard(Camera_Movement.FORWARD, deltaTime)
    if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
        camera.ProcessKeyboard(Camera_Movement.BACKWARD, deltaTime)
    if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
        camera.ProcessKeyboard(Camera_Movement.LEFT, deltaTime)
    if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
        camera.ProcessKeyboard(Camera_Movement.RIGHT, deltaTime)

# glfw: sempre que o tamanho da janela é alterado (pelo SO ou por redimensionamento do usuário), esta função de callback é executada
# --------------------------------------------------
def framebuffer_size_callback(window, width, height):
    # certifique-se de que a viewport corresponda às novas dimensões da janela; observe que a largura e
    # a altura serão significativamente maiores do que as especificadas em telas Retina. 
    glViewport(0, 0, width, height)

# glfw: sempre que o mouse se move, este callback é chamado
# --------------------------------------------------
def mouse_callback(window, xposIn, yposIn):    
    global camera
    global firstMouse, lastX, lastY

    xpos = xposIn
    ypos = yposIn

    if (firstMouse):
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos # invertido, já que as coordenadas y vão de baixo para cima

    lastX = xpos
    lastY = ypos

    camera.ProcessMouseMovement(xoffset, yoffset)

# glfw: sempre que a roda de rolagem do mouse é girada, este callback é chamado
# --------------------------------------------------
def scroll_callback(window, xoffset, yoffset):
    global camera

    camera.ProcessMouseScroll(yoffset)

# função utilitária para carregar uma textura 2D a partir de um arquivo
# --------------------------------------------------
def loadTexture(path):
    textureID = glGenTextures(1)

    image = Image.open(path)
    width = image.width
    height = image.height
    data = array(image, 'uint8')

    try:
        if (image.mode == 'L'):
            format = GL_RED
        elif (image.mode == 'RGB'):
            format = GL_RGB
        elif (image.mode == 'RGBA'):
            format = GL_RGBA

        glBindTexture(GL_TEXTURE_2D, textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    except:
        print("Falha ao carregar a textura no caminho: " + path)

    return textureID

if (__name__ == "__main__"):
    main()
