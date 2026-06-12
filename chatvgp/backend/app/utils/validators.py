def _apenas_digitos(valor: str) -> str:
    return "".join(filter(str.isdigit, valor or ""))


def _validar_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in (9, 10):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


def _validar_cnpj(cnpj: str) -> bool:
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    for i, pesos in zip((12, 13), (pesos_1, pesos_2)):
        soma = sum(int(cnpj[num]) * pesos[num] for num in range(0, i))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(cnpj[i]):
            return False

    return True


def validar_cpf_cnpj(valor: str) -> bool:
    """
    Valida CPF (11 dígitos) ou CNPJ (14 dígitos), incluindo dígitos
    verificadores. Aceita string com ou sem máscara.
    """
    digitos = _apenas_digitos(valor)

    if len(digitos) == 11:
        return _validar_cpf(digitos)
    if len(digitos) == 14:
        return _validar_cnpj(digitos)

    return False
