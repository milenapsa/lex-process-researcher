SUPERIOR = ["tst", "tse", "stj", "stm"]
TRFS = [f"trf{i}" for i in range(1, 7)]
TJS = [
    "tjac", "tjal", "tjam", "tjap", "tjba", "tjce", "tjdft", "tjes", "tjgo",
    "tjma", "tjmg", "tjms", "tjmt", "tjpa", "tjpb", "tjpe", "tjpi", "tjpr",
    "tjrj", "tjrn", "tjro", "tjrr", "tjrs", "tjsc", "tjse", "tjsp", "tjto",
]
TRTS = [f"trt{i}" for i in range(1, 25)]
TRE_UFS = [
    "ac", "al", "am", "ap", "ba", "ce", "dft", "es", "go", "ma", "mg", "ms",
    "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn", "ro", "rr", "rs", "sc",
    "se", "sp", "to",
]
TRES = [f"tre-{uf}" for uf in TRE_UFS]
TJMS = ["tjmmg", "tjmrs", "tjmsp"]

ALL_TRIBUNALS = SUPERIOR + TRFS + TJS + TRTS + TRES + TJMS
DATAJUD_ALIASES = {tribunal: f"api_publica_{tribunal}" for tribunal in ALL_TRIBUNALS}

MANUAL_OFFICIAL_SOURCES = {
    "tjsc_process": {
        "name": "TJSC — Consulta processual/eproc",
        "url": "https://www.tjsc.jus.br/consulta-comarcas-e-turmas",
        "coverage": ["autos_publicos", "consulta_processual"],
        "reason": "portal oficial protegido; não contornar controles",
    },
    "tjsc_jurisprudence": {
        "name": "TJSC — Portal da Jurisprudência",
        "url": "https://www.tjsc.jus.br/web/jurisprudencia",
        "coverage": ["acordaos", "decisoes_monocraticas", "inteiro_teor"],
        "reason": "consulta integral preservada no portal oficial",
    },
    "tjrs_jurisprudence": {
        "name": "TJRS — Pesquisa de Jurisprudência",
        "url": "https://www.tjrs.jus.br/buscas/jurisprudencia/?aba=jurisprudencia",
        "coverage": ["acordaos", "decisoes", "ementas"],
        "reason": "mecanismo de busca não automatizado",
    },
    "tjpr_jurisprudence": {
        "name": "TJPR — Pesquisa de Jurisprudência",
        "url": "https://portal.tjpr.jus.br/jurisprudencia/publico/pesquisa.do?actionType=pesquisar",
        "coverage": ["acordaos", "decisoes", "ementas"],
        "reason": "portal integral mantido como consulta oficial separada",
    },
    "tjsp_jurisprudence": {
        "name": "TJSP — Consulta de Jurisprudência",
        "url": "https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do",
        "coverage": ["acordaos", "decisoes", "ementas"],
        "reason": "portal completo mantido como consulta oficial separada",
    },
}

CURATED_AUTOMATED_SOURCES = {
    "tjsc_sumulas": "TJSC — Súmulas",
    "tjsc_enunciados": "TJSC — Enunciados",
    "tjrs_sumulas_tr_fazenda": "TJRS — Súmulas das Turmas Recursais da Fazenda Pública",
    "tjpr_enunciados_turmas": "TJPR — Enunciados das Turmas Recursais",
    "tjhr_enunciados_tuj": "TJPR — Enunciados da Turma de Uniformização",
    "tjsp_enunciados_comesp": "TJSP — Enunciados COMESP",
}
