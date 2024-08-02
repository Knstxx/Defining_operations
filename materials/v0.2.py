from datetime import datetime
from typing import Optional
import pytz


class DataClass:
    def __init__(self,
                 time: datetime,
                 bpos: float,
                 rpma: float,
                 woba: float,
                 hkla: float
                 ):
        self.time = time  # Время
        self.bpos = bpos  # Положение блока
        self.rpma = rpma  # Обороты ротора
        self.woba = woba  # Нагрузка на долото
        self.hkla = hkla  # Вес на крюке

    def __repr__(self):
        return (f"DataClass(time={self.time},",
                f" bpos={self.bpos},",
                f" rpma={self.rpma},",
                f" woba={self.woba},",
                f" hkla={self.hkla})")


def parse_line(line: str) -> Optional[DataClass]:
    data_list = [float(item) for item in line.split() if item.strip()]

    if len(data_list) == 25:
        time = datetime.fromtimestamp(data_list[0] / 1000,
                                      pytz.timezone('Europe/Moscow')
                                      )
        return DataClass(time, *data_list[1:5])
    else:
        return None


def algorithm(file_path: str, time1: str, time2: str) -> str:
    with open(file_path,
              'r',
              encoding='CP1251'
              ) as file:
        lines = file.readlines()

    data_list = [parse_line(line) for line in lines if parse_line(line)]
    start_time = datetime.fromisoformat(time1)
    end_time = datetime.fromisoformat(time2)
    filtered_list = []
    for data in data_list:
        if start_time <= data.time <= end_time:
            filtered_list.append(data)

    # Порог для определения (например, 80%)
    majority_threshold_for_bpos = 0.8
    majority_threshold_for_rpma = 0.8
    majority_threshold_for_woba = 0.8
    majority_threshold_for_hkla = 0.8

    # Количество значений, удовлетворяющих условию
    bpos_changed_count = 0
    rpma_greater_than_zero_count = 0
    woba_greater_than_zero_count = 0
    hkla_decreasing_trend_count = 0

    previous_bpos = None
    previous_hkla = None

    for data in filtered_list:
        if previous_bpos is not None and data.bpos != previous_bpos:
            # Значение bpos изменилось
            bpos_changed_count += 1
        previous_bpos = data.bpos

        if data.rpma > 0:
            rpma_greater_than_zero_count += 1

        if data.woba > 0:
            woba_greater_than_zero_count += 1

        if previous_hkla is not None and data.hkla < previous_hkla:
            hkla_decreasing_trend_count += 1
        previous_hkla = data.hkla

    # Расчет изменений
    majority_bpos_changed = (bpos_changed_count /
                             len(filtered_list)
                             > majority_threshold_for_bpos
                             )
    majority_rpma_greater_than_zero = (rpma_greater_than_zero_count /
                                       len(filtered_list)
                                       > majority_threshold_for_rpma
                                       )
    majority_woba_greater_than_zero = (woba_greater_than_zero_count /
                                       len(filtered_list)
                                       > majority_threshold_for_woba
                                       )
    majority_hkla_decreased = (hkla_decreasing_trend_count /
                               len(filtered_list)
                               > majority_threshold_for_hkla
                               )

    # Алгоритм
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


if __name__ == "__main__":
    # Путь к файлу, начальное и конечное время
    file_path = "file_path.txt"
    start_time = "2023-01-01T00:00:00"
    end_time = "2023-01-02T00:00:00"

    print(algorithm(file_path, start_time, end_time))
