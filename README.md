# cs-vojna-i-mir
A (computational) linguistic analysis of code-switching Russian-French in Lev Tolstoi's Война и мир (War and Peace).

## Installation
To create a virtual environment and install all required packages, run `bash install.sh`.
Download the dataset from [WikiSource](https://ru.wikisource.org/wiki/%D0%92%D0%BE%D0%B9%D0%BD%D0%B0_%D0%B8_%D0%BC%D0%B8%D1%80_(%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B9)) and place the .txt files in a directory `corpus`.

## Usage
scripts:
- `preprocess.py`: data preprocessing and computing CS types -> creates `cs_*.csv`
- `codeswitch.py`: annotate intrasentential CS instances with PoS tags, lemmata, dependency and morphological information -> creates `features.csv`
- `analysis.ipynb`: analyse outputs


outputs:
- `cs_*.csv`: overview of CS instances of each volume
- `features.csv`: linguistic features of intra-sentential CS instances
