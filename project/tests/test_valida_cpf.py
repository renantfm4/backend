import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.valida_cpf import valida_cpf

def test_cpf_valido():
    assert valida_cpf("529.982.247-25") is True

def test_cpf_com_digitos_repetidos():
    assert valida_cpf("111.111.111-11") is False

def test_cpf_incompleto():
    assert valida_cpf("12345678") is False