

# **PROJETO DE VALIDAÇÃO DO GAP TOPOLOGICO NARRATIVO**

## **Título**

**Delta H — Validação Empírica do Gap Topológico Narrativo (ΔT): Relação entre Estrutura Semântica Global e Compreensão de Leitores**

---

# **1\. Hipótese Central**

Definimos

ΔT(r)=CT−Cobs(r)\\Delta\_T(r)=C\_T-C\_{obs}(r)ΔT​(r)=CT​−Cobs​(r)

onde:

* CTC\_TCT​ \= complexidade topológica da obra completa;  
* Cobs(r)C\_{obs}(r)Cobs​(r) \= complexidade observável em uma janela local de leitura rrr.

Hipótese principal:

S=f(ΔT)S=f(\\Delta\_T)S=f(ΔT​)

onde SSS é o desempenho do leitor.

Mais especificamente:

corr(ΔT,S)\<0\\boxed{ \\mathrm{corr}(\\Delta\_T,S)\<0 }corr(ΔT​,S)\<0​

ou seja:

quanto maior o Gap Topológico Narrativo,

menor a capacidade do leitor de reconstruir a estrutura global do texto.

---

# **2\. Fundamentação Matemática**

Complexidade Topológica:

CT=∑k=0m(k+1)βkC\_T= \\sum\_{k=0}^{m} (k+1)\\beta\_kCT​=k=0∑m​(k+1)βk​

onde:

βk\\beta\_kβk​

são os números de Betti.

---

## **Complexidade Observada**

Para uma janela de leitura

WrW\_rWr​

obtém-se

KrK\_rKr​

e define-se

Cobs(r)=∑k(k+1)βk(Kr)C\_{obs}(r)= \\sum\_{k} (k+1)\\beta\_k(K\_r)Cobs​(r)=k∑​(k+1)βk​(Kr​)

---

## **Gap**

ΔT(r)=CT−Cobs(r)\\Delta\_T(r)= C\_T-C\_{obs}(r)ΔT​(r)=CT​−Cobs​(r)

---

# **3\. Métrica Experimental de Compreensão**

Precisamos medir a reconstrução da narrativa.

---

## **Escore Local**

Perguntas sobre o trecho lido.

Exemplo:

* quem falou?  
* onde ocorreu?  
* qual o evento principal?

---

## **Escore Global**

Perguntas sobre:

* tema central;  
* destino dos personagens;  
* relações entre eventos distantes.

---

Definimos:

S=αSlocal+(1−α)SglobalS= \\alpha S\_{local} \+ (1-\\alpha)S\_{global}S=αSlocal​+(1−α)Sglobal​

com

0\<α\<10\<\\alpha\<10\<α\<1

sugerido:

α=0.3\\alpha=0.3α=0.3

dando mais peso à compreensão global.

---

# **4\. Predição Quantitativa**

Modelo mais simples:

S=a−bΔT+εS= a-b\\Delta\_T+\\varepsilonS=a−bΔT​+ε

com

b\>0b\>0b\>0

---

Teste estatístico:

Regressão linear.

---

Hipótese nula:

H0:b=0H\_0:b=0H0​:b=0

---

Hipótese alternativa:

H1:b\>0H\_1:b\>0H1​:b\>0

---

# **5\. Seleção de Obras**

Grupo simples:

* O Pequeno Príncipe  
* Harry Potter

---

Grupo intermediário:

* Dom Casmurro  
* Hamlet

---

Grupo complexo:

* Ulysses  
* Grande Sertão: Veredas

---

Objetivo:

obter ampla variação de

ΔT\\Delta\_TΔT​

---

# **6\. Pipeline Computacional**

## **Etapa 1**

Segmentação em janelas.

Python  
1  
def split\_text(text,n):  
2  
words=text.split()  
3  
return \[  
4  
words\[i:i+n\]  
5  
for i in range(0,len(words),n)  
6  
\]  
Mostrar mais linhas  
---

## **Etapa 2**

Embeddings semânticos

Python  
1  
from sentence\_transformers import SentenceTransformer  
2  
   
3  
model=SentenceTransformer(  
4  
"paraphrase-multilingual-MiniLM-L12-v2"  
5  
)  
Mostrar mais linhas  
---

## **Etapa 3**

Construção do grafo

Python  
1  
from sklearn.metrics.pairwise import cosine\_similarity  
Mostrar mais linhas  
Python  
1  
if sim\>tau:  
2  
adicionar\_aresta()  
Mostrar mais linhas  
---

## **Etapa 4**

Complexo Vietoris-Rips

Python  
1  
import gudhi  
Mostrar mais linhas  
Python  
1  
rips \= gudhi.RipsComplex(  
2  
points=data,  
3  
max\_edge\_length=eps  
4  
)  
Mostrar mais linhas  
---

## **Etapa 5**

Betti

Python  
1  
simplex\_tree \= rips.create\_simplex\_tree(  
2  
max\_dimension=3  
3  
)  
4  
   
5  
simplex\_tree.persistence()  
6  
   
7  
betti=simplex\_tree.betti\_numbers()  
Mostrar mais linhas  
---

## **Complexidade total**

Python  
1  
def C(betti):  
2  
   
3  
total=0  
4  
   
5  
for k,b in enumerate(betti):  
6  
   
7  
total \+= (k+1)\*b  
8  
   
9  
return total  
Mostrar mais linhas  
---

## **Gap**

Python  
1  
delta \= C\_global \- C\_local  
Mostrar mais linhas  
---

# **7\. Coleta com Leitores**

Para cada leitor:

1. Apresentar trecho;  
2. Aplicar questionário;  
3. Obter escore SSS.

---

Tabela:

| leitor | trecho | ΔT | S |
| ----- | ----- | ----- | ----- |
| 1 | A | 12 | 8 |
| 2 | A | 12 | 7 |
| 3 | B | 35 | 3 |

---

# **8\. Teste Estatístico**

Correlação de Pearson

Python  
1  
from scipy.stats import pearsonr  
2  
   
3  
r,p \= pearsonr(delta,S)  
Mostrar mais linhas  
---

Resultado esperado:

r\<0r\<0r\<0

estatisticamente significativo.

---

# **9\. Modelo Mais Robusto**

A dificuldade de leitura depende também de:

* escolaridade;  
* idade;  
* familiaridade com literatura.

Logo:

S=a−bΔT+cE+dI+eF+εS= a- b\\Delta\_T+ cE+ dI+ eF+ \\varepsilonS=a−bΔT​+cE+dI+eF+ε

onde:

* EEE \= escolaridade;  
* III \= idade;  
* FFF \= familiaridade.

---

Regressão múltipla.

---

# **10\. Homologia Persistente**

Primeira melhoria importante.

Em vez dos Betti fixos:

usar persistência.

Defina

Pk=∑i(di−bi)P\_k= \\sum\_i (d\_i-b\_i)Pk​=i∑​(di​−bi​)

onde

did\_idi​ \= morte

bib\_ibi​ \= nascimento

dos ciclos.

---

Nova complexidade:

CTpers=∑k(k+1)PkC\_T^{pers} \= \\sum\_k (k+1)P\_kCTpers​=k∑​(k+1)Pk​

---

Novo Gap:

ΔTpers=CTpers−Cobspers\\Delta\_T^{pers} \= C\_T^{pers} \- C\_{obs}^{pers}ΔTpers​=CTpers​−Cobspers​

Provavelmente mais estável.

---

# **11\. Aperfeiçoamento Original**

A versão mais promissora é usar entropia topológica.

Em vez de:

C=∑(k+1)βkC= \\sum(k+1)\\beta\_kC=∑(k+1)βk​

defina

pk=βk∑jβjp\_k= \\frac{\\beta\_k} {\\sum\_j \\beta\_j}pk​=∑j​βj​βk​​

e

HT=−∑kpklog⁡pkH\_T \= \-\\sum\_k p\_k \\log p\_kHT​=−k∑​pk​logpk​

---

Gap Entrópico

ΔH=HT−Hobs\\Delta\_H \= H\_T \- H\_{obs}ΔH​=HT​−Hobs​

Possível vantagem:

reduz dependência da escala do texto.

---

# **12\. Predição Forte da Teoria**

Se a hipótese estiver correta:

Deve existir uma constante negativa

λ\\lambdaλ

tal que

S≈e−λΔTS \\approx e^{-\\lambda \\Delta\_T}S≈e−λΔT​

ou seja:

a compreensão global decai exponencialmente com o aumento do gap.

---

# **13\. Critérios de Sucesso**

A teoria ganha forte suporte experimental se aparecer:

### **Correlação**

r\<−0.5r\<-0.5r\<−0.5

em múltiplas obras.

---

### **Reprodutibilidade**

Mesmo resultado para:

* BERT;  
* SBERT;  
* Word2Vec.

---

### **Robustez**

Mesmo resultado para:

* diferentes janelas;  
* diferentes limiares;  
* diferentes leitores.

---

# **14\. Próximo Passo Matemático**

A extensão mais interessante para o seu programa de pesquisa é substituir

ΔT=CT−Cobs\\Delta\_T=C\_T-C\_{obs}ΔT​=CT​−Cobs​

por

ΔT=dbottle(DT,Dobs)\\Delta\_T= d\_{bottle}(D\_T,D\_{obs})ΔT​=dbottle​(DT​,Dobs​)

onde:

* DTD\_TDT​ \= diagrama de persistência global;  
* DobsD\_{obs}Dobs​ \= diagrama local;  
* dbottled\_{bottle}dbottle​ \= distância bottleneck.

Isso cria um verdadeiro **Gap Topológico de Informação**, baseado na geometria dos diagramas persistentes, e o aproxima de uma medida canônica da análise topológica de dados.

