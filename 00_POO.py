class Carro:
    def __init__(self, modelo, cor):  
        self.modelo = modelo
        self.cor = cor
        self.velocidade = 0  # o carro começa parado

    def acelerar(self, incremento):
        self.velocidade += incremento
        print(f'o {self.modelo} acelerou para {self.velocidade} Km/h.')

    def desacelerar (self, decremento):
        self.velocidade -= decremento
        print(f'o {self.modelo} desacelerou para {self.velocidade} Km/h.')

#Criando um objeto carro
meu_carro = Carro('Fusca', 'Vermelho')      
outro_carro = Carro('Range Rover', 'Preto') 

meu_carro.acelerar(20)
meu_carro.acelerar(40)
meu_carro.acelerar(60)
meu_carro.desacelerar(20)
