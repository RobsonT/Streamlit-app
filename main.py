import streamlit as st
import pandas as pd
import altair as alt
import base64

def desenhaLinha():
    st.write('___________________________________________________________________________________')

def getDownloadLink(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="dataset.csv">Baixar arquivo csv</a>'
    return href

def criarHistograma(coluna, df):
    histograma = alt.Chart(df, width=600).mark_bar().encode(
        alt.X(coluna, bin=True),
        y='count()', tooltip=[coluna, 'count()']
    ).interactive()
    return histograma

def criarBarras(coluna_num, coluna_cat, df):
    barras = alt.Chart(df, width = 600).mark_bar().encode(
        x=alt.X(coluna_num, stack='zero'),
        y=alt.Y(coluna_cat),
        tooltip=[coluna_cat, coluna_num]
    ).interactive()
    return barras

def criarBoxplot(coluna_num, coluna_cat, df):
    boxplot = alt.Chart(df, width=600).mark_boxplot().encode(
        x=coluna_num,
        y=coluna_cat
    )
    return boxplot

def criarScatterplot(x, y, color, df):
    scatter = alt.Chart(df, width=800, height=400).mark_circle().encode(
        alt.X(x),
        alt.Y(y),
        color = color,
        tooltip = [x, y]
    ).interactive()
    return scatter

def criaCorrelationplot(df, colunas_numericas):
    cor_data = (df[colunas_numericas]).corr().stack().reset_index().rename(columns={0: 'correlation', 'level_0': 'variable', 'level_1': 'variable2'})
    cor_data['correlation_label'] = cor_data['correlation'].map('{:.2f}'.format)  # Round to 2 decimal
    base = alt.Chart(cor_data, width=500, height=500).encode( x = 'variable2:O', y = 'variable:O')
    text = base.mark_text().encode(text = 'correlation_label',color = alt.condition(alt.datum.correlation > 0.5,alt.value('white'),
    alt.value('black')))
    
    cor_plot = base.mark_rect().encode(
    color = 'correlation:Q')

    return cor_plot + text

def main():
    st.title('AceleraDev Data Science')
    st.sidebar.image('logo.png', width= 300)
    st.sidebar.title('Opções')
    sidebarCategoria = st.sidebar.radio(
        '',('Informações básicas', 'Ánalise exploratoria', 'Inputação de dados', 'Visualização dos dados'))
    file  = st.file_uploader('Escolha a base de dados que deseja analisar (.csv)', type = 'csv')
    if file is not None:
        index = st.checkbox('Utilizar primeira coluna como index')
        df = pd.read_csv(file, index_col=0) if index else pd.read_csv(file)
        aux = pd.DataFrame({"colunas": df.columns, 'tipos': df.dtypes})
        colunas_numericas = list(aux[aux['tipos'] != 'object']['colunas'])
        colunas_object = list(aux[aux['tipos'] == 'object']['colunas'])
        colunas = list(df.columns)
        st.subheader(sidebarCategoria)
        if(sidebarCategoria == 'Informações básicas'):
            st.markdown('Visualização do dataframe')
            numero_colunas = st.slider('Escolha o numero de colunas que deseja visualizar', min_value=1, max_value=50)
            st.dataframe(df.head(numero_colunas))
            desenhaLinha()
            st.markdown('número de amostras e de atributos')
            st.markdown('Número de amostras:')
            st.markdown(df.shape[0])
            st.markdown('Número de atributos:')
            st.markdown(df.shape[1])
            desenhaLinha()
            st.markdown('Atributos:')
            st.dataframe(aux.reset_index(drop=True), 500, 180)
            desenhaLinha()
            st.markdown('Visualização das amostras(valores únicos):')
            atributo = st.selectbox('Escolha um atributo', df.columns)
            st.dataframe(pd.DataFrame({atributo: df[atributo].unique()}))
        elif(sidebarCategoria == 'Ánalise exploratoria'):
            st.markdown('Descrição do dataset:')
            st.table(df[colunas_numericas].describe().transpose())
            desenhaLinha()
            st.markdown('Estatística descritiva univariada')
            col = st.selectbox('Selecione a coluna :', colunas_numericas)
            if col is not None:
                st.markdown('Selecione o que deseja analisar :')
                mean = st.checkbox('Média')
                if mean:
                    st.markdown(df[col].mean())
                median = st.checkbox('Mediana')
                if median:
                    st.markdown(df[col].median())
                desvio_pad = st.checkbox('Desvio padrão')
                if desvio_pad:
                    st.markdown(df[col].std())
                kurtosis = st.checkbox('Kurtosis')
                if kurtosis:
                    st.markdown(df[col].kurtosis())
                skewness = st.checkbox('Skewness')
                if skewness:
                    st.markdown(df[col].skew())
            desenhaLinha()
            st.markdown('Quantidade de dados faltantes:')
            dados_faltante = pd.DataFrame({'atributos' : df.columns,'tipos': df.dtypes,
                             'NA %' : (df.isna().sum() / df.shape[0]) * 100})
            st.table(dados_faltante)
        elif(sidebarCategoria == 'Inputação de dados'):
            dados_faltante = pd.DataFrame({'atributos' : df.columns,'tipos': df.dtypes,
                             'NA %' : (df.isna().sum() / df.shape[0]) * 100})
            percentual = st.slider('Escolha o limite de percentual faltante para as colunas que você deseja inputar os dados', min_value=0, max_value=100)
            lista_colunas = list(dados_faltante[dados_faltante['NA %']  <= percentual][dados_faltante['tipos'] != 'object']['atributos'])
            select_method = st.radio('Escolha um metodo abaixo :', ('Média', 'Mediana', 'moda'))
            if select_method == 'Média':
                df_inputado = df[lista_colunas].fillna(df[lista_colunas].mean())
            if select_method == 'Mediana':
                df_inputado = df[lista_colunas].fillna(df[lista_colunas].mean())
            if select_method == 'moda':
                df_inputado = df[lista_colunas].fillna(df[lista_colunas].mode())
            dados_inputado = pd.DataFrame({'atributos': df_inputado.columns, 'tipos': df_inputado.dtypes, 
                                    'NA %': (df_inputado.isna().sum() / df_inputado.shape[0]) * 100})
            st.table(dados_inputado[dados_inputado['tipos'] != 'object']['NA %'])
            st.markdown('Download do csv com dados inputados')
            st.markdown(getDownloadLink(df_inputado), unsafe_allow_html=True)
        elif(sidebarCategoria == 'Visualização dos dados'):
            histograma = st.checkbox('Histograma')
            if histograma:
                col_num = st.selectbox('Selecione a Coluna Numerica: ', colunas_numericas,key = 'unique')
                st.markdown('Histograma da coluna' + str(col_num) + ': ')
                st.write(criarHistograma(col_num, df))
            barras = st.checkbox('Gráfico de barras')
            if barras:
                col_num_barras = st.selectbox('Selecione a coluna numerica: ', colunas_numericas, key = 'unique')
                col_cat_barras = st.selectbox('Selecione uma coluna categorica : ', colunas_object, key = 'unique')
                st.markdown('Gráfico de barras da coluna ' + str(col_cat_barras) + ' pela coluna ' + col_num_barras)
                st.write(criarBarras(col_num_barras, col_cat_barras, df))
            boxplot = st.checkbox('Boxplot')
            if boxplot:
                col_num_box = st.selectbox('Selecione a Coluna Numerica:', colunas_numericas,key = 'unique' )
                col_cat_box = st.selectbox('Selecione uma coluna categorica : ', colunas_object, key = 'unique')
                st.markdown('Boxplot ' + str(col_cat_box) + ' pela coluna ' + col_num_box)
                st.write(criarBoxplot(col_num_box, col_cat_box, df))
            scatter = st.checkbox('Scatterplot')
            if scatter:
                col_num_x = st.selectbox('Selecione o valor de x ', colunas_numericas, key = 'unique')
                col_num_y = st.selectbox('Selecione o valor de y ', colunas_numericas, key = 'unique')
                col_color = st.selectbox('Selecione a coluna para cor', colunas)
                st.markdown('Selecione os valores de x e y')
                st.write(criarScatterplot(col_num_x, col_num_y, col_color, df))
            correlacao = st.checkbox('Correlacao')
            if correlacao:
                st.markdown('Gráfico de correlação das colunas númericas')
                st.write(criaCorrelationplot(df, colunas_numericas))
    
    


if __name__ == '__main__':
	main()