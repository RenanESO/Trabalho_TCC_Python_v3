import sys
import locale
import os
import uteis
from treinamento import Treinamento
from organiza import Organiza
from duplicidade import Duplicidade
from dotenv import load_dotenv

# ------------------------------------------------------ main -------------------------------------------------------- #
if __name__ == '__main__':
    try:
        print(' Executando ... ')

        # Forçando a localização padrão
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        # Definindo as variáveis de ambiente
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'

        # Carregar as variáveis do ambiente Env.
        load_dotenv()

        uteis.apagarArquivoLog()
        uteis.gravarArquivoLog()

        uteis.resetarPastaResultado(uteis.caminhoPastaTemp)

        if uteis.opcaoRotina == 'treinamento':
            objTreinamento = Treinamento()
            objTreinamento.configurarTreinamento()
            objTreinamento.treinarReconhecimentoFacial()

        elif uteis.opcaoRotina == 'organiza':
            objOrganiza = Organiza()
            objOrganiza.configurarOrganiza()
            objOrganiza.reconhecimentoFacialOrganizar()

        elif uteis.opcaoRotina == 'duplicidade':
            objDuplicidade = Duplicidade()
            objDuplicidade.configurarDuplicidade()
            objDuplicidade.verificarFotosDuplicadas()

        print(f' ======> "{uteis.opcaoRotina}" foi FINALIZADO <======  ')
        uteis.adicionarLog(f' ======> "{uteis.opcaoRotina}" foi FINALIZADO <======  ')
        uteis.gravarArquivoLog()
        sys.exit(0)

    except Exception as e:
        uteis.encontrouError(f' ======> ERROR:  "{e}" <======  ')

