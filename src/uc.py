 #!/usr/bin/python
 #-*- coding: utf-8-*-

############################
# Control Unit Simulator
# Duo: Matheus Lima     (github.com/matheus-lima)
#      Vinicius Matheus (github.com/vnicius)
############################

import re

class ControlUnit():
    def __init__(self, data_mem, instr_mem):
        self.data_mem = data_mem     #Memória de dados
        self.instr_mem = instr_mem   #Memória de instruções
        self.reg = [0] * 4           #Array de registradores
        self.ir = ""                 #Armazena a instrução atual
        self.pc = 0                  #Armazena o endereço da próxima instrução
        self.flags = [False] * 4     #Flags condicionais [zero, menor que, maior que, igual]
                                    # zero = 1000 , maior que = 0010, igual que = 0001 ...

    def fill_instr_mem(self, instr):
        self.instr_mem.append(instr)

    def fetch(self):
        self.ir = self.instr_mem[self.pc] #busca na memoria de instrucao e atualiza IR
        self.pc += 1                      #atualiza pc

    def decode_exec(self):
        instr = self.ir.split(" ")  #Divide a instrução
        op = instr[0].upper()       #Pega a operação da instrução
        data = ''.join(instr[1:]).replace(" ", '')
        #Avalia qual tipo de operacao
        if (op == "ADD") or (op == "SUB") or (op == "DIV") or (op == "MULT"):   #Casos seja uma operação aritmética
            self.arithmetic(op, data)
        elif op == "STORE":
            self.store(data)
        elif op == "LOAD":
            self.load(data)
        elif op == "MOV":
            self.mov(data)
        elif op == "JMP":
            self.jmp(data)
        elif op == "CMP":
            self.cmp(data)
        elif op == "JL" or op == "JG" or op == "JE" or op == "JZ":
            self.conditional_jump(op, data)

    def arithmetic(self, operation, data):
        #data: Transforma o array data em string e retira os espaços
        operands = data.split(",")               #Separa os operandos
        op1 = op2 = 0                            #Variaveis para guardar os dois operandos da operação

        reg_result = int(operands[0][1])         #Guarda o indíce do registrador de saída

        if "R" in operands[1].upper():           #Confere se é um registrador
            op1 = self.reg[int(operands[1][1])]  #Pega apenas o número do registrador
        elif "MD" in operands[1].upper():        #Confere se é um acesso à memória de dados
            op1 = self.data_mem[int(re.sub(r'[^\d]', '', operands[1].upper()))]   #Pega apenas o endereço da memória
        else:
            op1 = int(operands[1])               #Caso seja um número

        if "R" in operands[2].upper():
            op2 = self.reg[int(operands[2][1])]
        elif "MD" in operands[2].upper():
            op2 = self.data_mem[int(re.sub(r'[^\d]', '', operands[2].upper()))]
        else:
            op2 = int(operands[2])

        if operation == "ADD":
            self.reg[reg_result] = op1 + op2
        elif operation == "SUB":
            self.reg[reg_result] = op1 - op2
        elif operation == "MULT":
            self.reg[reg_result] = op1 * op2
        elif operation == "DIV":
            self.reg[reg_result] = int(op1 / op2)

    def store(self, data): # STORE MD[] R[] or MD[] X
        """Recebe um endereço da memória e o dado que será armazenado nele"""
        operands = data.split(',')
        value = 0

        adress_mem = int(re.sub(r'[^\d]', '', operands[0].upper()))     #Endereço na memória

        if "R" in operands[1].upper():          #Confere se é um registrador
            value = self.reg[int(operands[1][1])]
        else:
            value = int(operands[1])

        self.data_mem[adress_mem] = value         #Armazena o dado no endereço da memória


    def load(self, data): # lOAD R[] MD[]
        '''Armazena dados da memória de dados (ou valores) no registrador indicado'''
        operands = data.split(',')
        value = -1

        reg_result = int(operands[0][1])

        if "MD" in operands[1].upper():         #Confere se é um acesso à memória
            value = self.data_mem[int(re.sub(r'[^\d]', '', operands[1].upper()))]   #Pega apenas o endereço da memória

        self.reg[reg_result] = value

    def mov(self, data): #MOV R0, R1 or MOV R0, 5
        operands = data.split(',')
        value = -1

        reg_result = int(operands[0][1])

        if "R" in operands[1]:
            value = self.reg[int(operands[1][1])]
        else:
            value = int(operands[1])

        self.reg[reg_result] = value

    def jmp(self, data): # JMP MI[]

        if "MI" in data.upper():         #Confere se é um acesso à memória
            self.pc = int(re.sub(r'[^\d]', '', data.upper()))   #Pega apenas o endereço da memória
        else:
            #data é o rotulo
            for x in range(len(self.instr_mem)):
                if self.instr_mem[x].upper() == data.upper():
                    self.pc = x+1
                    break

        self.flags = [False] * 4 #reset flags

    def cmp(self, data): #CMP R[X] R[Y]
    #atualiza as flahs
        operands = data.split(',')
        value = -1

        if len(operands) == 1: #Compara se eh igual a zero
            value = self.reg[int(operands[0][1])]
            if value == 0:
                self.flags[0] = True
            #else ja eh falso
        else: #dois argumentos: R[X] <operation> R[Y]
            #recovery values from regs
            value = self.reg[int(operands[0][1])]
            value2 = self.reg[int(operands[1][1])]
            if value > value2:
                self.flags[2] = True
            elif value < value2:
                self.flags[1] = True
            elif value == value2:
                self.flags[3] = True

    def conditional_jump(self, op, data):
        if op == "JZ" and self.flags[0]:
            self.jmp(data)
        elif op == "JL" and self.flags[1]:
            self.jmp(data)
        elif op == "JG" and self.flags[2]:
            self.jmp(data)
        elif op == "JE" and self.flags[3]:
            self.jmp(data)


    def __str__(self):
        return ("\nIR: "+self.ir+"\ndata_mem: "+str(self.data_mem)+"\nReg: "+str(self.reg)+"\nPC: "+str(self.pc)+"\nFlags: "+str(self.flags))

#########################
if __name__ == "__main__":
    data_mem = [0] * 16
    instr_mem = []

    #name = "fibonacci.txt"
    name = input("Programa: ")
    file = open(name, "r")

    uc = ControlUnit(data_mem, instr_mem)

    for line in file.readlines():
        if line is not "\s":
            uc.fill_instr_mem(line.replace("\n", ""))
    file.close()

    tam = len(uc.instr_mem)

    while uc.pc < tam:
        uc.fetch()
        uc.decode_exec()
        print(uc)
        input()
