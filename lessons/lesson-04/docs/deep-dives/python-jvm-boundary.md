# Deep Dive: PySpark и Python/JVM boundary

## Что происходит

Classic PySpark client использует Python API, а Spark SQL execution engine работает в JVM. Built-in expressions (`pyspark.sql.functions`) описывают вычисление как expression tree, доступное optimizer.

Обычная Python UDF создаёт отдельную Python execution boundary:

- serialization/deserialization;
- меньше возможностей для optimizer;
- сложнее plan visibility;
- отдельный failure/performance profile.

## Правило выбора

1. Найти built-in Spark SQL function.
2. Рассмотреть SQL expression.
3. Если логика действительно внешняя — оценить pandas UDF/Arrow.
4. Обычная Python UDF — осознанный fallback с benchmark/evidence.

## Не делать культ

Запрет UDF не абсолютный. Важно зафиксировать:

- почему built-in недостаточно;
- input/output schema;
- serialization cost;
- unit tests;
- plan/runtime comparison.

Источник: [PySpark DataFrame API](https://spark.apache.org/docs/4.2.0/api/python/reference/pyspark.sql/dataframe.html).
