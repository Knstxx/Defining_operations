import pandas as pd
import lasio
from datetime import datetime, timedelta

# Путь к файлу
file_path = r'/Users/r.r.shcherbatyuk/Downloads/Губкина_осложнения_обновленные_данные/Прихваты по новой иерархии - 30 прихватов (3 - новые, 1 - доп данные)/A) Бурение ротором + проработка - 7 прихватов/7) 449 АГКМ/449 АГКМ [19.04.2022-20.04.2022].las'

# Чтение файла LAS
las = lasio.read(file_path)
df = las.df()
df.index = pd.to_datetime(df.index, unit='ms')

# Функция для удаления выбросов
def remove_outliers(dataframe):
    q1 = dataframe.quantile(0.25)
    q3 = dataframe.quantile(0.75)
    iqr = q3 - q1
    dataframe_cleaned = dataframe[~((dataframe < (q1 - 1.5 * iqr)) | (dataframe > (q3 + 1.5 * iqr))).any(axis=1)]
    return dataframe_cleaned

df_cleaned = remove_outliers(df)
df_positive = df_cleaned.interpolate()
print(df_positive.head())

def algorithm(dataframe, time: str) -> str:
    time2_dt = datetime.fromisoformat(time)
    time1_dt = time2_dt - timedelta(hours=2)

    # Фильтрация DataFrame по времени
    filtered_df = dataframe[(dataframe.index >= time1_dt) & (dataframe.index <= time2_dt)]

    # Порог для определения (например, 50%)
    majority_threshold_for_bpos = 0.5
    majority_threshold_for_rpma = 0.5
    majority_threshold_for_woba = 0.5
    majority_threshold_for_hkla = 0.5

    # Количество значений, удовлетворяющих условию
    bpos_changed_count = 0
    rpma_greater_than_zero_count = 0
    woba_greater_than_zero_count = 0
    hkla_decreasing_trend_count = 0

    previous_bpos = None
    previous_hkla = None

    for idx, row in filtered_df.iterrows():
        bpos = row['BPOS']
        rpma = row['RPMA'] if 'RPMA' in row else 0  # Проверяем наличие столбца 'RPMA'
        woba = row['WOBA']
        hkla = row['HKLA']

        if previous_bpos is not None and bpos != previous_bpos:
            bpos_changed_count += 1
        previous_bpos = bpos

        if rpma > 0:
            rpma_greater_than_zero_count += 1

        if woba > 0:
            woba_greater_than_zero_count += 1

        if previous_hkla is not None and hkla < previous_hkla:
            hkla_decreasing_trend_count += 1
        previous_hkla = hkla

    filtered_list_len = len(filtered_df)

    majority_bpos_changed = (bpos_changed_count / filtered_list_len > majority_threshold_for_bpos)
    majority_rpma_greater_than_zero = (rpma_greater_than_zero_count / filtered_list_len > majority_threshold_for_rpma)
    majority_woba_greater_than_zero = (woba_greater_than_zero_count / filtered_list_len > majority_threshold_for_woba)
    majority_hkla_decreased = (hkla_decreasing_trend_count / filtered_list_len > majority_threshold_for_hkla)

    if majority_bpos_changed:
        result = "1. Положение талевого блока меняется\n"
        if majority_rpma_greater_than_zero:
            result += "2. Есть обороты ротора\n"
            if majority_woba_greater_than_zero:
                result += "3. Есть нагрузка на долото\n"
                result += "БУРЕНИЕ РОТОРОМ"
            else:
                result += "3. Нет нагрузки на долото\n"
                result += "ПРОРАБОТКА"
        else:
            result += "2. Нет оборотов ротора\n"
            if majority_woba_greater_than_zero:
                result += "3. Есть нагрузка на долото\n"
                result += "БУРЕНИЕ СЛАЙДОМ"
            else:
                if majority_hkla_decreased:
                    result += "4. Вес на крюке снижается\n"
                    result += "ПОДЪЕМ БК"
                else:
                    result += "4. Вес на крюке увеличивается\n"
                    result += "СПУСК БК/ОК"
    else:
        result = "1. Положение талевого блока не меняется\n"
        if majority_rpma_greater_than_zero:
            result += "2. Есть обороты ротора\n"
            result += "ПРОМЫВКА"
        else:
            result += "2. Нет оборотов ротора\n"
            result += "ПРОСТОЙ"

    return result

timeOfSticking = "2022-04-19 05:06:20"
operationType = algorithm(df_positive, timeOfSticking)
print(operationType)
