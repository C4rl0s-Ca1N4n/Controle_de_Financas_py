from modelo import Conta, engine, Status, Historico, Tipos
from sqlmodel import Session, select
from datetime import date
import matplotlib.pyplot as plt

# função responsável em criar as contas

def criar_conta(conta: Conta):
    with Session(engine) as conexao:
        statement = select(Conta).where(Conta.banco==conta.banco)
        results = conexao.exec(statement).all()
    if results:
        print("Já existe uma conta nesse banco!")
        return
    conexao.add(conta)
    conexao.commit()
    return conta

# função responsável em listar todas as contas

def listar_contas():
    with Session(engine) as conexao:
        statement = select(Conta)
        results = conexao.exec(statement).all()
    return results

# função responsável por desativar uma determinada conta

def desativar_conta(id):
    with Session(engine) as conexao:
        statement = select(Conta).where(Conta.id==id)
        conta = conexao.exec(statement).first()
    if conta.valor > 0:
        raise ValueError('Essa conta ainda possui saldo, não é possível desativar.')
    conta.status = Status.INATIVO
    conexao.commit()

# função responsável por transferir o saldo entre as contas.

def transferir_saldo(id_conta_saida, id_conta_entrada, valor):
    with Session(engine) as conexao:
        statement = select(Conta).where(Conta.id==id_conta_saida)
        conta_saida = conexao.exec(statement).first()
    if conta_saida.valor < valor:
        raise ValueError('Saldo insuficiente')
    statement = select(Conta).where(Conta.id==id_conta_entrada)
    conta_entrada = conexao.exec(statement).first()
    conta_saida.valor -= valor
    conta_entrada.valor += valor
    conexao.commit()

# função responsável por tmovimentar o saldo das contas.

def movimentar_dinheiro(historico: Historico):
    with Session(engine) as conexao:
        statement = select(Conta).where(Conta.id==historico.conta_id)
        conta = conexao.exec(statement).first()

    if conta.status == Status.INATIVO:  # Verifica se a conta está inativa
            raise ValueError("A conta está inativa e não pode receber movimentações.")

    if historico.tipo == Tipos.ENTRADA:
        conta.valor += historico.valor
    else:
        if conta.valor < historico.valor:
            raise ValueError("Saldo insuficiente")
            conta.valor -= historico.valor

    conexao.add(historico)
    conexao.commit()
    return historico

#  função responsável pelo saldo somado de todas as contas:

def total_contas():
    with Session(engine) as conexao:
        statement = select(Conta)
        contas = conexao.exec(statement).all()

    total = 0
    for conta in contas:
        total += conta.valor
    return float(total)

# funcão responsável por filtrar as movimentações financeiras dentro de um período específico

def buscar_historicos_entre_datas(data_inicio: date, data_fim: date):
    with Session(engine) as conexao:
        statement = select(Historico).where(
            Historico.data >= data_inicio,
            Historico.data <= data_fim
        )
        resultados = conexao.exec(statement).all()
        return resultados
    
#  Funcao para gerar um gráfico que mostra o total de dinheiro em cada conta para o usuário

def criar_grafico_por_conta():
    with Session(engine) as conexao:
        statement = select(Conta).where(Conta.status==Status.ATIVO)
        contas = conexao.exec(statement).all()
        bancos = [i.banco.value for i in contas]
        total = [i.valor for i in contas]

    plt.bar(bancos, total)
    plt.show()


