import org.testng.Assert
import org.testng.annotations.DataProvider
import org.testng.annotations.Test
import java.io.File
import java.nio.charset.Charset
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId


class Test {

    @Test(
        description = "Тестирование алгоритма",
        dataProviderClass = TestDataProvider::class,
        dataProvider = "testDataProvider"
    )
    fun testAlgorithm(filePath: String, startTime: String, endTime: String, expectedResult: String) {
        val result = algorithm(filePath, startTime, endTime)
        Assert.assertEquals(result, expectedResult)
    }

    private fun algorithm(path: String, time1: String, time2: String): String {
        val file = File(path).bufferedReader(Charset.forName("CP1251")).useLines { lines ->
            lines.toList()
        }

        val dataList = mutableListOf<DataClass>()
        file.forEach { line ->
            val data = parseLine(line)
            if (data != null) {
                dataList.add(data)
            }
        }

        val startTime = OffsetDateTime.parse(time1)
        val endTime = OffsetDateTime.parse(time2)
        val filteredList = dataList.filter { it.time in startTime..endTime }

        filteredList.forEach { println(it) }

        // Порог для определения (например, 80%)
        val majorityThresholdForBpos = 0.8
        val majorityThresholdForRpma = 0.8
        val majorityThresholdForWoba = 0.8
        val majorityThresholdForHkla = 0.8

        // Количество значений, удовлетворяющих условию
        var bposChangedCount = 0
        var rpmaGreaterThanZeroCount = 0
        var wobaGreaterThanZeroCount = 0
        var hklaDecreasingTrendCount = 0

        var previousBpos: Double? = null
        var previousHkla: Double? = null
        // Цикл по объектам из filteredList
        for (data in filteredList) {
            if (previousBpos != null && data.bpos != previousBpos) {
                // Значение bpos изменилось
                bposChangedCount++
            }
            previousBpos = data.bpos

            if (data.rpma > 0) {
                rpmaGreaterThanZeroCount++
            }

            if (data.woba > 0) {
                wobaGreaterThanZeroCount++
            }

            if (previousHkla != null && data.hkla < previousHkla) {
                hklaDecreasingTrendCount++
            }
            previousHkla = data.hkla
        }

        // Расчет изменений
        val majorityBposChanged = bposChangedCount.toDouble() / filteredList.size > majorityThresholdForBpos
        val majorityRpmaGreaterThanZero =
            rpmaGreaterThanZeroCount.toDouble() / filteredList.size > majorityThresholdForRpma
        val majorityWobaGreaterThanZero =
            wobaGreaterThanZeroCount.toDouble() / filteredList.size > majorityThresholdForWoba
        val majorityHklaDecreased = hklaDecreasingTrendCount.toDouble() / filteredList.size > majorityThresholdForHkla

        var result: String? = null
        // Алгоритм
        when {
            majorityBposChanged -> {
                println("1. Положение талевого блока меняется")

                when {
                    majorityRpmaGreaterThanZero -> {
                        println("2. Есть обороты ротора")

                        when {
                            majorityWobaGreaterThanZero -> {
                                println("3. Есть нагрузка на долото")
                                result = "БУРЕНИЕ РОТОРОМ"
                                println(String.format("ИТОГ: %s", result))
                            }

                            else -> {
                                println("3. Нет нагрузки на долото")
                                result = "ПРОРАБОТКА"
                                println(String.format("ИТОГ: %s", result))
                            }
                        }

                    }

                    else -> {
                        println("2. Нет оборотов ротора")

                        when {
                            majorityWobaGreaterThanZero -> {
                                println("3. Есть нагрузка на долото")
                                result = "БУРЕНИЕ СЛАЙДОМ"
                                println(String.format("ИТОГ: %s", result))
                            }

                            else -> {
                                println("3. Нет нагрузки на долото")

                                when {
                                    majorityHklaDecreased -> {
                                        println("4. Вес на крюке снижается")
                                        result = "ПОДЪЕМ БК"
                                        println(String.format("ИТОГ: %s", result))
                                    }

                                    else -> {
                                        println("4. Вес на крюке увеличивается")
                                        result = "СПУСК БК/ОК"
                                        println(String.format("ИТОГ: %s", result))
                                    }
                                }
                            }
                        }
                    }
                }

            }

            else -> {
                println("1. Положение талевого блока не меняется")

                when {
                    majorityRpmaGreaterThanZero -> {
                        println("2. Есть обороты ротора")
                        result = "ПРОМЫВКА"
                        println(String.format("ИТОГ: %s", result))
                    }

                    else -> {
                        println("2. Нет оборотов ротора")
                        result = "ПРОСТОЙ"
                        println(String.format("ИТОГ: %s", result))
                    }
                }
            }
        }

        return result
    }

    private fun parseLine(line: String): DataClass? {
        val dataList = line.split(" ").filter { it.isNotBlank() }.mapNotNull { it.toDoubleOrNull() }

        return if (dataList.size == 25) {
            DataClass(
                OffsetDateTime.ofInstant(Instant.ofEpochMilli(dataList[0].toLong()), ZoneId.of("Europe/Moscow")),
                dataList[1],
                dataList[2],
                dataList[3],
                dataList[4],
                dataList[5],
                dataList[6],
                dataList[7],
                dataList[8],
                dataList[9],
                dataList[10],
                dataList[11],
                dataList[12],
                dataList[13],
                dataList[14],
                dataList[15],
                dataList[16],
                dataList[17],
                dataList[18],
                dataList[19],
                dataList[20],
                dataList[21],
                dataList[22],
                dataList[23],
                dataList[24]
            )
        } else {
            null
        }
    }
}