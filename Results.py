from datetime import datetime
import pandas as pd


class Results:
    def __init__(self, trades):
        self.trades = trades

    def _add_trade(self, flag, trade_list):
        if flag['buy'] > 0 and flag['sell'] > 0:
            trade_list = trade_list.append(flag, ignore_index=True)
            return {'buy': 0, 'sell': 0}, trade_list
        return flag, trade_list

    def _set_all(self, trades):
        flag = {'buy': 0, 'sell': 0}
        trade_list = pd.DataFrame({'buy': [], 'sell': []})

        for index, trade in trades.iterrows():
            if trade['is_buyer']:
                flag, trade_list = self._add_trade(flag, trade_list)
                flag['buy'] += trade['qty']
            else:
                if flag['buy'] > 0:
                    flag['sell'] += trade['qty']

        _, trade_list = self._add_trade(flag, trade_list)
        trade_list['reward'] = trade_list['sell'] - trade_list['buy']
        trade_list['tasa'] = trade_list['sell'] / trade_list['buy'] - 1

        return trade_list


    def _get_number_of_trades(self, trades):
        n_trades = len(trades['reward'])
        n_positive_trades = len(trades[trades['reward'] >= 0])
        n_negative_trades = n_trades - n_positive_trades
        return n_trades, n_positive_trades, n_negative_trades

    def _get_rates(self, trades):
        positive_rate = trades[trades['tasa'] >= 0]['tasa'].mean() * 100
        negative_rate = trades[trades['tasa'] < 0]['tasa'].mean() * 100
        mean_rate = trades['tasa'].mean() * 100
        return mean_rate, positive_rate, negative_rate

    def _get_gain_and_loss(self, trades):
        return sum(trades[trades['reward'] > 0]['reward']), sum(trades[trades['reward'] < 0]['reward'])

    def _get_amounts(self, trades):
        initial_amount, final_amount = trades['buy'][0], trades['sell'][len(trades) - 1]
        return initial_amount, final_amount

    def _get_time(self, trades):
        initial_time = trades['time'][0].strftime('%H:%M %d-%m-%Y')
        final_time = trades['time'][len(trades) - 1].strftime('%H:%M %d-%m-%Y')
        time = datetime.strptime(final_time, '%H:%M %d-%m-%Y') - datetime.strptime(initial_time, '%H:%M %d-%m-%Y')
        return time

    def __str__(self):
        msg = ''
        trades = self.trades.copy()
        results = self._set_all(trades)
        reward = sum(results['reward'])
        n_trades, n_positive_trades, n_negative_trades = self._get_number_of_trades(results)
        mean_rate, positive_rate, negative_rate = self._get_rates(results)
        performance = mean_rate * n_trades
        gain, loss = self._get_gain_and_loss(results)
        initial_amount, final_amount = self._get_amounts(results)
        tasa_de_aciertos = 100 * (1 - abs(loss) / (abs(loss) * 2 + reward))
        tasa_de_ganancia = (final_amount / initial_amount)
        time = self._get_time(trades)
        daily_performance = performance / time.days
        monthly_performance = daily_performance * 30
        annual_performance = daily_performance * 365

        msg += '#' * 25 + '\n'
        msg += f'TRADEANDO DURANTE\n'
        msg += f'{int(time.days / 365)} AÑOS, {int((time.days % 365) / 31)} MESES Y {(time.days % 365) % 31 + time.seconds / 86400: .0f} DÍAS'
        msg += '\n' + '#' * 25 + '\n'
        msg += '=' * 25 + '\n' + 'RESULTADO' + '\n' + '=' * 25 + '\n'

        values = [
            initial_amount,
            final_amount,
            gain,
            loss,
            reward,
            tasa_de_aciertos,
            tasa_de_ganancia,
            n_trades,
            n_positive_trades,
            n_negative_trades,
            n_negative_trades / n_positive_trades,
            mean_rate,
            positive_rate,
            negative_rate,
            performance,
            daily_performance,
            monthly_performance,
            annual_performance
        ]

        for i, t in enumerate(TITLES):
            msg += f'{t}\n{values[i]:.2f} {UNITS[i]: <5}\n'
            msg += '.' * 50 + '\n' if i < len(TITLES) - 1 else '=' * 25 + '\n'

        return msg


TITLES = [
    'Monto Inicial',
    'Monto Final',
    'Ganancia Bruta',
    'Pérdida',
    'Ganancia Neta',
    'Acertabilidad',
    'Multiplicador',
    'N° de Trades',
    'N° de Trades Positivos',
    'N° de Trades Negativos',
    'Tasa de Aciertos',
    'Tasa Promedio',
    'Tasa de Ganancia Promedio',
    'Tasa de Pérdida Promedio',
    'Rendimiendo',
    'Rendimiendo Diario',
    'Rendimiendo Mensual',
    'Rendimiendo Anual'
]

UNITS = ['U$DT', 'U$DT', 'U$DT', 'U$DT', 'U$DT', '%', '', '', '', '', 'N/P', '%', '%', '%', '%', '%', '%', '%']

