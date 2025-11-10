# Project introduction

The primary objective of this repository is to provide some code and data support to analyze answers made by Gemini LLM in comparision of the specialist analysis.
Is important to mention that we do not provide the base study with PDF's and specialist analysis in this repository. The pdfs are in the original study https://dl.acm.org/doi/abs/10.1145/3546932.3546997 .

# Folder separation explanation
One of the segments of that study have the objective of find the best way of find section(e.g Introduction, Background, Conclusion) in an academic article. That was explored and compared at the regex folder
```
├── regex/
│   ├── pdf_handler.py
│   ├── plots.ipynb
|   ├── results/
```
In the results folder, I save the result of my experiments tested in 
validation.ipynb, using the sqlite format.

## Important observation
To recreate this findings is important to have all pdfs downloaded and separated in the following way:

	├── ACM
	│   ├── ....pdf
	├── ScienceDirect
	│   ├── ....pdf

### Sample of my structure
```
├── papers_pdf
│   ├── ACM
│   │   ├── amraoui2022_splc.pdf
│   │   ├── cheng2023_tse.pdf
│   │   ├── dorn2020_vamos.pdf
│   │   ├── friesel2022_icse.pdf
│   │   ├── gong2022_msr.pdf
│   │   ├── gong2023_fse.pdf
│   │   ├── gonzalez-rojas2019_otm.pdf
│   │   ├── isaev2023_hpcc.pdf
│   │   ├── kolesnikov2019_emse.pdf
│   │   ├── kolesnikov2019_ssm.pdf
│   │   ├── lesoil2022_vamos.pdf
│   │   ├── magrin2022_twc.pdf
│   │   ├── muhlbauer2023_icse.pdf
│   │   ├── peeters2021_ida.pdf
│   │   ├── ros2020_emse.pdf
│   │   └── yufei2024_jss.pdf
│   ├── ScienceDirect
│   │   ├── Arcaini2020.pdf
│   │   ├── H. Martin2022.pdf
│   │   ├── lesoil2023.pdf
│   │   ├── lesoil2024.pdf
│   │   └── Švogor2019.pdf
│   ├── Scopus
│   │   ├── Alshehri2020.pdf
│   │   ├── alves2020-icpe.pdf
│   │   ├── Arcaini2020.pdf
│   │   ├── ballesteros2021.pdf
│   │   ├── chen2020.pdf
│   │   ├── Chen2022.pdf
│   │   ├── chen2023.pdf
│   │   ├── damasceno2019.pdf
│   │   ├── Damasceno2021.pdf
│   │   ├── Gao2021-ICSE.pdf
│   │   ├── García2021.pdf
│   │   ├── ghofrani2019.pdf
│   │   ├── Ha2019-icse.pdf
│   │   ├── Ha-2019ICSME.pdf
│   │   ├── Iorio2019.pdf
│   │   ├── Iqbal2022.pdf
│   │   ├── Iqbal2023.pdf
│   │   ├── Kaltenecker2019.pdf
│   │   ├── Krishna2021.pdf
│   │   ├── Kumara2023.pdf
│   │   ├── lesoil2021-icps.pdf
│   │   ├── lesoil2021.pdf
│   │   ├── lesoil2022-icps.pdf
│   │   ├── li2020-ase.pdf
│   │   ├── li2020.pdf
│   │   ├── Liu2022.pdf
│   │   ├── martin2021.pdf
│   │   ├── mehlstäubl2022.pdf
│   │   ├── Muhlbauer2020.pdf
│   │   ├── Muhlbauer2023.pdf
│   │   ├── Nair2020.pdf
│   │   ├── nascimento2021-bigdata.pdf
│   │   ├── OH2023.pdf
│   │   ├── Salman2023.pdf
│   │   ├── schmid2022.pdf
│   │   ├── shu2020.pdf
│   │   ├── silva2020.pdf
│   │   ├── silva2021-icps.pdf
│   │   ├── Silva2023.pdf
│   │   ├── sree-kumar2021.pdf
│   │   ├── temple2019.pdf
│   │   ├── Temple2021.pdf
│   │   ├── tërnava2022.pdf
│   │   ├── valov2020-icpe.pdf
│   │   ├── Weber2021.pdf
│   │   ├── Xiang2022.pdf
│   │   └── Yu2021.pdf
│   ├── Snowballing
│   │   ├── 978-3-031-61874-1.pdf
│   │   ├── david2024-splc.pdf
│   │   ├── hugo2021-tse.pdf
│   │   ├── jose-miguel2023-jss.pdf
│   │   ├── larissa2024-hpdc.pdf
│   │   ├── lukas2024-splc.pdf
│   │   ├── mathieu2023-splc.pdf
│   │   ├── mukelabai2023-tse.pdf
│   │   ├── shaghayegh2022-splc.pdf
│   │   ├── tamim2024-splc.pdf
│   │   ├── xhevahire2023-sac.pdf
│   │   └── yuanjie2023-ase.pdf
│   └── SpringerLink
│       ├── cao2023ase.pdf
│       ├── Dorn2023ese.pdf
│       ├── Kaltenecker2023ese.pdf
│       ├── li2019_ssm.pdf
│       ├── li2023_scis.pdf
│       ├── liang2024cc.pdf
│       ├── lima2022ese.pdf
│       ├── marcén2022ssm.pdf
│       ├── metzger2024computing.pdf
│       ├── peng2023ese.pdf
│       ├── safdar2020_ase.pdf
│       ├── sakhrawi2019_cc.pdf
│       ├── seewal2021_ijpp.pdf
│       ├── sewal2024cc.pdf
│       ├── tipu2022_cc.pdf
│       ├── vázquez-ingelmo2020_cc.pdf
│       └── Vitui2021ese.pdf
```

The other part of my project try to acctually extract the information of the pdf, it also need the pdf struct previosly cited and the data-extraction.xlsx.

You could encounter the actual code to run it in the analysis folder.

# How to run it

## Clone the repository
    git clone https:tree//github.com/PedroVerardo/AutoSLR.git

## Env creation
	python -m venv venv

	//Linux venv activation
	source venv/bin/activate

	//Windows activation
	./venv/Scripts/Activate.ps1

## Pip the requirement pakages
    pip install -r requirements.txt
	
	
