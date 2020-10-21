import pandas as pd

import getEventData


async def datahandle(client, cp, sdtstr, edtstr, event_start_time, draw_id, event_period, bet_type, breakdown,
                     indicators):
    dfs = await getEventData.getdata(client, cp, sdtstr, edtstr, event_start_time, draw_id, event_period, bet_type,
                                     breakdown)
    if dfs:
        df, df2 = dfs[1], dfs[2]
        order = ['CS', 'WDW', 'TG', 'HF', 'Total']
        df.set_index(["Indicator"], inplace=True)
        df['CS'] = df.apply(lambda x: x['CS/SGL'] + x['CS/DBL'] + x['CS/TBL'] + x['CS/ACC4'], axis=1)
        df['WDW'] = df.apply(lambda x: x['WDW/DBL'] + x['WDW/TBL'] + x['WDW/ACC4'], axis=1)
        df['TG'] = df.apply(lambda x: x['TG/DBL'] + x['TG/TBL'] + x['TG/ACC4'], axis=1)
        df['HF'] = df.apply(lambda x: x['HF/DBL'] + x['HF/TBL'] + x['HF/ACC4'], axis=1)
        df1 = df[order]

        df2.set_index(["Indicator"], inplace=True)
        df2['CS'] = df2.apply(lambda x: x['CS'], axis=1)
        df2['WDW'] = df2.apply(lambda x: x['WDW'], axis=1)
        df2['TG'] = df2.apply(lambda x: x['TG'], axis=1)
        df2['HF'] = df2.apply(lambda x: x['HF'], axis=1)
        df1.append(df2)
        frames = [df1, df2]
        newdf = pd.concat(frames)

        dff = pd.Series({'Start Time': sdtstr, 'Stop Time': edtstr})

        for x in indicators:
            sertmp = newdf.loc[x, :]
            newidx = {i: x.split(' ')[1] + ' ' + i for i in sertmp.index}
            sertmp.rename(index=newidx, inplace=True)
            dff = pd.concat([dff, sertmp])

        np = {key: [dff[key]] for key in dff.index}
        return pd.DataFrame(np)
    else:
        return None
