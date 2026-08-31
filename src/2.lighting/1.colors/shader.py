import glm
from pathlib import *
from OpenGL.GL import *

class Shader:
    ID: int

    # o construtor gera o shader em tempo de execução
    # --------------------------------------------------
    def __init__(self, vertexPath, fragmentPath):
        # 1. recuperar o código-fonte do vértice/fragmento a partir de filePath
        vertexCode: str
        fragmentCode: str

        try:
            vertexCode = Path(vertexPath).read_text()
            fragmentCode = Path(fragmentPath).read_text()
        except Exception as e:
            print("ERROR::SHADER::FILE_NOT_SUCCESSFULLY_READ: " + e)
            return

        vShaderCode = vertexCode
        fShaderCode = fragmentCode

        # 2. compilar shaders
        vertex: int; fragment: int

        # vertex shader
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, vShaderCode)
        glCompileShader(vertex)
        self.checkCompileErrors(vertex, "VERTEX")

        # fragment Shader
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, fShaderCode)
        glCompileShader(fragment)
        self.checkCompileErrors(fragment, "FRAGMENT")

        # shader Program
        self.ID = glCreateProgram()
        glAttachShader(self.ID, vertex)
        glAttachShader(self.ID, fragment)
        glLinkProgram(self.ID)
        self.checkCompileErrors(self.ID, "PROGRAM")

        # exclua os shaders, pois eles já estão vinculados ao nosso programa e não são mais necessários
        glDeleteShader(vertex)
        glDeleteShader(fragment)

    # ativa o shader
    # --------------------------------------------------
    def use(self, ):
        glUseProgram(self.ID)

    # funções utilitárias de uniformes
    # --------------------------------------------------
    def setBool(self, name, value: bool):
        location = glGetUniformLocation(self.ID, name)
        glUniform1i(location, value)
    # --------------------------------------------------
    def setInt(self, name, value: int):
        location = glGetUniformLocation(self.ID, name)
        glUniform1i(location, value)
    # --------------------------------------------------
    def setFloat(self, name, value: float):
        location = glGetUniformLocation(self.ID, name)
        glUniform1f(location, value)
    # --------------------------------------------------
    def setVec2(self, name, x, y):
        location = glGetUniformLocation(self.ID, name)
        glUniform2f(location, x, y)
    # def setVec2(self, name, value: glm.vec2):
    #     location = glGetUniformLocation(self.ID, name)
    #     glUniform2fv(location, value)

    # PYTHON É LIXO, NÃO ACEITA SOBRECARGA
    
    # --------------------------------------------------
    def setVec3(self, name, x, y, z):
        location = glGetUniformLocation(self.ID, name)
        glUniform3f(location, x, y, z)
    # def setVec3(self, name, value: glm.vec3):
    #     location = glGetUniformLocation(self.ID, name)
    #     glUniform3fv(location, value)
    # --------------------------------------------------
    def setVec4(self, name, x, y, z, w):
        location = glGetUniformLocation(self.ID, name)
        glUniform4f(location, x, y, z, w)
    # def setVec4(self, name, value: glm.vec4):
    #     location = glGetUniformLocation(self.ID, name)
    #     glUniform4fv(location, value)
    # --------------------------------------------------
    def setMat2(self, name, mat: glm.mat2):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix2fv(location, 1, GL_FALSE, glm.value_ptr(mat))
    # --------------------------------------------------
    def setMat3(self, name, mat: glm.mat3):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix3fv(location, 1, GL_FALSE, glm.value_ptr(mat))
    # --------------------------------------------------
    def setMat4(self, name, mat: glm.mat4):
        location = glGetUniformLocation(self.ID, name)
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(mat))

    # função utilitária para verificar erros de compilação/vinculação de shaders.
    # --------------------------------------------------
    def checkCompileErrors(self, shader, type):
        succes: int
        infoLog: str

        if (type != "PROGRAM"):
            succes = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if (not succes):
                infoLog = glGetShaderInfoLog(shader)
                print(
                    "ERROR::SHADER_COMPILATION_ERROR of type: " + type + "\n" +
                    infoLog + "\n" +
                    " -- --------------------------------------------------- -- "
                )
        else:
            succes = glGetProgramiv(shader, GL_LINK_STATUS)
            if (not succes):
                infoLog = glGetProgramInfoLog(shader)
                print(
                    "ERROR::PROGRAM_LINKING_ERROR of type: " + type + "\n" +
                    infoLog + "\n" +
                    " -- --------------------------------------------------- -- "
                )
