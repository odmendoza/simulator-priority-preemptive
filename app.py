from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    dataframe = pd.DataFrame(columns=['Proceso', 'Tiempo de llegada', 'Rágada de CPU', 'Prioridad'])
    table = pd.DataFrame.to_html(dataframe, index=False)
    table = table.replace('class="dataframe"', 'class="table"')
    table = table.replace('right;', 'center;')
    return render_template('index.html', table=table)


@app.route('/priority-apropiative', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        proceso = request.form.get('proceso')
        llegada = request.form.get('llegada')
        rafaga = request.form.get('rafaga')
        prioridad = request.form.get('prioridad')
        row = {
            'Proceso': proceso,
            'Tiempo de llegada': llegada,
            'Rágada de CPU': rafaga,
            'Prioridad': prioridad
        }
        tb = request.form.get('table')

        dataframe = pd.read_html(tb, header=0)[0]
        dataframe = pd.DataFrame(dataframe)
        dataframe = dataframe.append(row, ignore_index=True)
        print(dataframe)

        table = pd.DataFrame.to_html(dataframe, index=False)
        table = table.replace('class="dataframe"', 'class="table"')
        table = table.replace('right;', 'center;')

        data = {
            'Proceso': '...',
            'Tiempo': [0]
        }
        grantt = pd.DataFrame(data)
        grantt = pd.DataFrame.to_html(grantt, index=False)
        grantt = grantt.replace('class="dataframe"', 'class="table"')
        grantt = grantt.replace('right;', 'center;')

    return render_template('priority.html', table=table, tiempo=0, grantt=grantt, total_CPU_time=0)


@app.route('/simulation', methods=['GET', 'POST'])
def simulation():
    if request.method == 'POST':
        tb = request.form.get('table')
        gr = request.form.get('grantt')
        tiempo = int(request.form.get('tiempo'))
        total_CPU_time = int(request.form.get('total_CPU_time'))

        dataframe = pd.read_html(tb, header=0)[0]
        grantt = pd.read_html(gr, header=0)[0]
        dataframe = pd.DataFrame(dataframe)
        grantt = pd.DataFrame(grantt)

        if (tiempo == 0):
            for index, row in dataframe.iterrows():
                total_CPU_time += row['Rágada de CPU']
        print('Total_CPU_time : ', total_CPU_time)
        if (tiempo < total_CPU_time):
            tiempo += 1
            current_process = dataframe[dataframe['Tiempo de llegada'] <= tiempo-1]
            print(current_process)
            if (current_process.empty):
                total_CPU_time += 1
                if (grantt.tail(1)['Proceso'].values[0] == '[ /// ]'):
                    aux = grantt.tail(1)
                    aux = aux.index.tolist()
                    grantt.at[aux[0], 'Tiempo'] += 1
                else:
                    data = {
                        'Proceso': '[ /// ]',
                        'Tiempo': tiempo
                    }
                    grantt = grantt.append(data, ignore_index=True)
            else:
                current_process = current_process[current_process['Rágada de CPU'] > 0]
                min = current_process['Prioridad'].values.min()
                for index, row in current_process.iterrows():
                    print('Tiempo [ ', tiempo, ' ]')
                    print('Proceso [ ', row['Proceso'], ' ]')
                prior_process = current_process[current_process['Prioridad'] == min]
                print('Procesos prioritarios', prior_process)

                if (len(prior_process) == 1):
                    ind = prior_process.index.tolist()
                    dataframe.at[ind[0], 'Rágada de CPU'] -= 1
                    print('Last : ', grantt.tail(1)['Proceso'].values[0])
                    if (grantt.tail(1)['Proceso'].values[0] == prior_process['Proceso'].values[0]):
                        aux = grantt.tail(1)
                        aux = aux.index.tolist()
                        grantt.at[aux[0], 'Tiempo'] += 1
                    else:
                        data = {
                            'Proceso': prior_process['Proceso'].values[0],
                            'Tiempo': tiempo
                        }
                        grantt = grantt.append(data, ignore_index=True)
                    print(grantt)

                if (len(prior_process) > 1):
                    first = current_process['Tiempo de llegada'].values.min()
                    print(current_process['Tiempo de llegada'])
                    print('FIFO -> ', first)
                    first_process = current_process[current_process['Tiempo de llegada'] == first]
                    print(first_process)
                    ind = first_process.index.tolist()
                    dataframe.at[ind[0], 'Rágada de CPU'] -= 1
                    if (grantt.tail(1)['Proceso'].values[0] == first_process['Proceso'].values[0]):
                        aux = grantt.tail(1)
                        aux = aux.index.tolist()
                        grantt.at[aux[0], 'Tiempo'] += 1
                    else:
                        data = {
                            'Proceso': first_process['Proceso'].values[0],
                            'Tiempo': tiempo
                        }
                        grantt = grantt.append(data, ignore_index=True)
                    print(grantt)

    table = pd.DataFrame.to_html(dataframe, index=False)
    table = table.replace('class="dataframe"', 'class="table"')
    table = table.replace('right;', 'center;')
    grantt = pd.DataFrame.to_html(grantt, index=False)
    grantt = grantt.replace('class="dataframe"', 'class="table"')
    grantt = grantt.replace('right;', 'center;')

    return render_template('simulation.html', table=table, tiempo=tiempo, grantt=grantt, total_CPU_time=total_CPU_time)


@app.route('/stadistics', methods=['GET', 'POST'])
def stadistics():
    if request.method == 'POST':
        tb = request.form.get('table')
        gr = request.form.get('grantt')

        dataframe = pd.read_html(tb, header=0)[0]
        grantt = pd.read_html(gr, header=0)[0]

        dataframe = pd.DataFrame(dataframe)
        grantt = pd.DataFrame(grantt)
        print(grantt)

        data = {
            'Proceso': '...',
            'Tiempo de espera': [0],
            'Tiempo de retorno': [0]
        }
        x = grantt.tail(len(grantt)-1)
        y = grantt.head(len(grantt)-1)
        d = {'Proceso':x['Proceso'].tolist(),'Inicio':y['Tiempo'].tolist()}
        df = pd.DataFrame(d)
        print(df)
        stadistics = pd.DataFrame(data)

        # Falta la parte de estadisticas

        table = pd.DataFrame.to_html(dataframe, index=False)
        table = table.replace('class="dataframe"', 'class="table"')
        table = table.replace('right;', 'center;')
        grantt = pd.DataFrame.to_html(grantt, index=False)
        grantt = grantt.replace('class="dataframe"', 'class="table"')
        grantt = grantt.replace('right;', 'center;')
        stadistics = pd.DataFrame.to_html(stadistics, index=False)
        stadistics = stadistics.replace('class="dataframe"', 'class="table"')
        stadistics = stadistics.replace('right;', 'center;')

    return render_template('stadistics.html', table=table, grantt=grantt, stadistics=stadistics)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run()
