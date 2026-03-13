# Data Schema 

## SEVESO/COV extravtion fields

- Identificação da substância / produto

Estes vêm quase sempre da SDS (Safety Data Sheet) no PDF.
	-	Referencia
	-	Designação da substância / mistura / resíduo / água residual
	-	Tipo de substância / Utilização
	-	Fornecedor
	-	Língua

- Identificação química

Section 3 – Composition do SDS.
	-	Constituintes da mistura
	-	% na mistura
	-	N.º CAS (3.2)
	-	N.º CE (3.2)

- Classificação de perigo

Normalmente na Section 2 – Hazard Identification.
	-	Classificação da substância / mistura
	-	SEVESO

- Propriedades físicas

Normalmente na Section 9 – Physical and Chemical Properties.
	-   Densidade (g/cm³)

- Informação VOC / COV
Encontrado na secção 8
	-   COV g/l
	-   COV %
	-   Consumo COV (t)

- Informação de quantidades (Dentro do As 400 base de dados da IBM)

Estes podem não vir do PDF, dependem do processo interno.
	-	Consumo anual / Produção anual
	-	Capacidade de armazenamento
	-	Quantidade máxima armazenada

- Campos administrativos

Provavelmente dentro do As400 tbm
	-	Nº
	-	Local de utilização
	-	Modo potencial de emissão
	-	N. versão
	-	Data


## Esquema de Extração Estruturada

O sistema de extração deverá produzir os seguintes campos estruturados:

- referencia
- nome_substancia
- tipo_substancia
- fornecedor
- lingua

### Identificação Química
- constituintes_mistura
- percentagem_composicao
- numero_cas
- numero_ce

### Classificação de Perigo
- classificacao_perigo
- categoria_seveso

### Propriedades Físicas
- densidade_g_cm3

### Informação VOC / COV
- cov_g_l
- cov_percentagem

